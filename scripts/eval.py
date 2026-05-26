#!/usr/bin/env python3
"""
Eval runner.

Corre tasks do eval set contra o agente actual e produz um relatório
comparável ao longo do tempo. Detecta regressão.

Uso:
    python scripts/eval.py run --task add-priority-field
    python scripts/eval.py run --all
    python scripts/eval.py compare --baseline results/2026-05-20.json --current results/2026-05-26.json
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
EVAL_DIR = ROOT / "tests" / "harness" / "eval-set"
RESULTS_DIR = EVAL_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_manifest() -> dict:
    return yaml.safe_load((EVAL_DIR / "MANIFEST.yml").read_text())


def load_task(task_id: str) -> dict:
    task_dir = EVAL_DIR / "tasks" / task_id
    return {
        "id": task_id,
        "dir": task_dir,
        "prompt": (task_dir / "prompt.md").read_text(),
        "expected": yaml.safe_load((task_dir / "expected.yml").read_text()),
        "rubric": (task_dir / "rubric.md").read_text() if (task_dir / "rubric.md").exists() else "",
    }


def run_agent(task: dict) -> dict:
    """
    Stub: na implementação real, isto invoca o agente (Claude Code SDK ou
    API directa) com o prompt, num sandbox isolado, e captura tudo.

    Retorna métricas observadas: tool_calls, tokens, duration, files changed, etc.
    """
    # Placeholder — na realidade invoca o agente
    return {
        "tool_calls": 0,
        "tokens": 0,
        "duration_seconds": 0,
        "files_created": [],
        "files_modified": [],
        "files_deleted": [],
        "diff": "",
        "final_response": "",
        "trace_path": "",
    }


def check_hard_gates(task: dict, run_result: dict) -> dict:
    """Corre os gates esperados (PHPStan, Pest, etc.) no estado pós-task."""
    gates = task["expected"].get("hard_gates", {})
    results = {}

    gate_commands = {
        "phpstan_passes": ["./vendor/bin/phpstan", "analyse", "--no-progress"],
        "pint_clean": ["./vendor/bin/pint", "--test"],
        "pest_passes": ["./vendor/bin/pest", "--parallel"],
        "vitest_passes": ["npm", "run", "test"],
        "vue_tsc_clean": ["npm", "run", "typecheck"],
        "build_succeeds": ["npm", "run", "build"],
    }

    for gate_name, expected in gates.items():
        cmd = gate_commands.get(gate_name)
        if not cmd:
            results[gate_name] = {"ran": False, "passed": None}
            continue
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=600)
            results[gate_name] = {"ran": True, "passed": r.returncode == 0}
        except subprocess.TimeoutExpired:
            results[gate_name] = {"ran": True, "passed": False, "reason": "timeout"}

    return results


def check_file_expectations(task: dict, run_result: dict) -> dict:
    """Verifica required_files_*, forbidden_changes, etc."""
    exp = task["expected"]
    all_changed = set(run_result["files_created"] + run_result["files_modified"])
    created = set(run_result["files_created"])

    def matches_any(path: str, patterns: list) -> bool:
        return any(fnmatch.fnmatch(path, p) for p in patterns)

    results = {"required_created_missing": [], "required_modified_missing": [], "forbidden_touched": []}

    for pattern in exp.get("required_files_created", []):
        if not any(matches_any(f, [pattern]) for f in created):
            results["required_created_missing"].append(pattern)

    for pattern in exp.get("required_files_modified", []):
        if not any(matches_any(f, [pattern]) for f in all_changed):
            results["required_modified_missing"].append(pattern)

    for pattern in exp.get("forbidden_changes", []):
        for f in all_changed:
            if matches_any(f, [pattern]):
                results["forbidden_touched"].append(f)

    # Verificações adversariais
    for f in exp.get("must_not_create", []):
        if matches_any(f, list(created)):
            results["forbidden_touched"].append(f"created {f} but must_not_create")

    return results


def check_content(task: dict, run_result: dict) -> list:
    """Verifica content_checks e must_not_contain_in_any_file."""
    failures = []
    exp = task["expected"]

    for check in exp.get("content_checks", []):
        path = ROOT / check["file"]
        if not path.exists():
            failures.append(f"content_check: {check['file']} não existe")
            continue
        content = path.read_text()
        for needle in check.get("must_contain", []):
            if needle not in content:
                failures.append(f"{check['file']} deveria conter '{needle}'")
        for needle in check.get("must_not_contain", []):
            if needle in content:
                failures.append(f"{check['file']} NÃO deveria conter '{needle}'")

    # Verificação global
    forbidden_globals = exp.get("must_not_contain_in_any_file", [])
    if forbidden_globals:
        for f in run_result["files_created"] + run_result["files_modified"]:
            fp = ROOT / f
            if not fp.exists() or fp.is_dir():
                continue
            try:
                content = fp.read_text(errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue
            for needle in forbidden_globals:
                if needle in content:
                    failures.append(f"FORBIDDEN STRING '{needle}' em {f}")

    return failures


def score_run(task: dict, run_result: dict, gates: dict, file_check: dict, content_fails: list) -> dict:
    """Calcula score final do eval."""
    hard_pass = all(g.get("passed") for g in gates.values() if g.get("ran"))
    file_pass = (
        not file_check["required_created_missing"]
        and not file_check["required_modified_missing"]
        and not file_check["forbidden_touched"]
    )
    content_pass = not content_fails

    s = task["expected"].get("scoring", {})
    efficiency = 1.0
    if s.get("tool_calls_max"):
        efficiency *= min(1.0, s["tool_calls_max"] / max(run_result["tool_calls"], 1))
    if s.get("duration_max_seconds"):
        efficiency *= min(1.0, s["duration_max_seconds"] / max(run_result["duration_seconds"], 1))

    return {
        "passed": hard_pass and file_pass and content_pass,
        "hard_gates_pass": hard_pass,
        "file_expectations_pass": file_pass,
        "content_pass": content_pass,
        "efficiency_score": round(efficiency, 3),
        "gates_detail": gates,
        "file_check_detail": file_check,
        "content_failures": content_fails,
    }


def run_one_task(task_id: str) -> dict:
    print(f"\n▶ A correr eval: {task_id}")
    task = load_task(task_id)
    started = time.time()

    run_result = run_agent(task)
    gates = check_hard_gates(task, run_result)
    file_check = check_file_expectations(task, run_result)
    content_fails = check_content(task, run_result)
    score = score_run(task, run_result, gates, file_check, content_fails)

    return {
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "wallclock_seconds": time.time() - started,
        "run_metrics": run_result,
        "score": score,
    }


def compare(baseline_path: Path, current_path: Path) -> None:
    baseline = json.loads(baseline_path.read_text())
    current = json.loads(current_path.read_text())

    base_by_id = {r["task_id"]: r for r in baseline["results"]}
    cur_by_id = {r["task_id"]: r for r in current["results"]}

    regressions = []
    improvements = []
    for tid in base_by_id:
        if tid not in cur_by_id:
            continue
        bp = base_by_id[tid]["score"]["passed"]
        cp = cur_by_id[tid]["score"]["passed"]
        if bp and not cp:
            regressions.append(tid)
        elif cp and not bp:
            improvements.append(tid)

    print(f"\n=== Comparação eval set ===")
    print(f"Baseline: {baseline_path.name}")
    print(f"Actual:   {current_path.name}")
    print(f"\nRegressões: {len(regressions)}")
    for r in regressions:
        print(f"  ✗ {r}")
    print(f"\nMelhorias: {len(improvements)}")
    for i in improvements:
        print(f"  ✓ {i}")

    if regressions:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--task", help="ID de uma task específica")
    p_run.add_argument("--all", action="store_true")

    p_cmp = sub.add_parser("compare")
    p_cmp.add_argument("--baseline", required=True)
    p_cmp.add_argument("--current", required=True)

    args = parser.parse_args()

    if args.cmd == "run":
        manifest = load_manifest()
        if args.all:
            task_ids = [t["id"] for t in manifest["tasks"] if t.get("active", True)]
        elif args.task:
            task_ids = [args.task]
        else:
            print("Especifica --task ou --all", file=sys.stderr)
            sys.exit(1)

        results = [run_one_task(tid) for tid in task_ids]

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total": len(results),
            "passed": sum(1 for r in results if r["score"]["passed"]),
            "results": results,
        }
        out = RESULTS_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
        out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        print(f"\n✓ {summary['passed']}/{summary['total']} passou")
        print(f"  Guardado em {out.relative_to(ROOT)}")

    elif args.cmd == "compare":
        compare(Path(args.baseline), Path(args.current))


if __name__ == "__main__":
    main()
