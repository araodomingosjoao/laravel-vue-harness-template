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
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
EVAL_DIR = ROOT / "tests" / "harness" / "eval-set"
RESULTS_DIR = EVAL_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

POLICY_FILE = ROOT / "config" / "harness" / "policy.yml"

# Agente headless: `claude -p` num sandbox isolado. Usa a auth local do `claude`
# (subscrição logada localmente, ou CLAUDE_CODE_OAUTH_TOKEN no CI).
AGENT_TIMEOUT = 1800  # segundos — alinha com budgets.max_duration_seconds
AGENT_ALLOWED_TOOLS = "Bash,Read,Edit,Write,Glob,Grep"


def load_policy() -> dict:
    return yaml.safe_load(POLICY_FILE.read_text()) if POLICY_FILE.exists() else {}


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


def _empty_run(**over) -> dict:
    base = {
        "tool_calls": 0, "tokens": 0, "cost_usd": 0.0, "duration_seconds": 0.0,
        "files_created": [], "files_modified": [], "files_deleted": [],
        "diff": "", "final_response": "", "sandbox": "", "error": None,
    }
    base.update(over)
    return base


def run_agent(task: dict) -> dict:
    """
    Corre o agente (Claude Code headless, `claude -p`) sobre o prompt da task num
    sandbox isolado, e captura métricas + diff. Usa a auth local do `claude`:
    a subscrição logada (local) ou CLAUDE_CODE_OAUTH_TOKEN (CI).

    O sandbox é uma cópia dos ficheiros tracked do repo (vendor/node_modules são
    symlinked para os gates poderem correr). A diff é obtida via git contra um
    commit baseline. Degrada com mensagem clara se o CLI `claude` não existir.
    """
    if shutil.which("claude") is None:
        return _empty_run(error="`claude` CLI não encontrado (npm i -g @anthropic-ai/claude-code)")

    sandbox = Path(tempfile.mkdtemp(prefix=f"eval-{task['id']}-"))
    git = ["git", "-C", str(sandbox)]
    try:
        # Cópia só dos ficheiros tracked (sem vendor/node_modules), via git archive.
        archive = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, capture_output=True)
        if archive.returncode != 0:
            return _empty_run(sandbox=str(sandbox), error="git archive HEAD falhou (repo sem commits?)")
        subprocess.run(["tar", "-x", "-C", str(sandbox)], input=archive.stdout, check=True)

        # Symlink das dependências para os gates (PHPStan/Pest/Vitest) correrem.
        for dep in ("vendor", "node_modules"):
            if (ROOT / dep).exists():
                (sandbox / dep).symlink_to(ROOT / dep)

        # Baseline para conseguir fazer diff do que o agente mudou.
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True, capture_output=True)
        subprocess.run(
            git + ["-c", "commit.gpgsign=false", "-c", "user.email=eval@harness",
                   "-c", "user.name=eval", "commit", "-qm", "baseline"],
            check=True, capture_output=True,
        )

        started = time.time()
        proc = subprocess.run(
            ["claude", "-p", task["prompt"], "--output-format", "json",
             "--permission-mode", "acceptEdits", "--allowedTools", AGENT_ALLOWED_TOOLS],
            cwd=sandbox, capture_output=True, text=True, timeout=AGENT_TIMEOUT,
        )
        duration = round(time.time() - started, 1)

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return _empty_run(sandbox=str(sandbox), duration_seconds=duration,
                              error=f"output do agente não-parseável: {proc.stdout[:300]}")

        usage = data.get("usage") or {}
        # `git add -A` + diff vs baseline lista cada ficheiro individualmente —
        # `git status --porcelain` colapsa diretórios novos e esconde os ficheiros lá dentro.
        subprocess.run(git + ["add", "-A"], capture_output=True)
        name_status = subprocess.run(
            git + ["diff", "--cached", "--name-status", "HEAD"], capture_output=True, text=True
        ).stdout
        created, modified, deleted = [], [], []
        for line in name_status.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            st, path = parts[0], parts[-1]
            if st.startswith("A"):
                created.append(path)
            elif st.startswith("D"):
                deleted.append(path)
            else:
                modified.append(path)
        diff = subprocess.run(git + ["diff", "--cached", "HEAD"], capture_output=True, text=True).stdout

        return {
            "tool_calls": data.get("num_turns", 0),
            "tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            "cost_usd": data.get("total_cost_usd", 0.0),
            "duration_seconds": duration,
            "files_created": created,
            "files_modified": modified,
            "files_deleted": deleted,
            "diff": diff,
            "final_response": data.get("result", ""),
            "sandbox": str(sandbox),
            "error": data.get("result") if data.get("is_error") else None,
        }
    except subprocess.TimeoutExpired:
        return _empty_run(sandbox=str(sandbox), error=f"agente excedeu {AGENT_TIMEOUT}s")
    except Exception as e:  # noqa: BLE001 — o eval nunca deve rebentar por uma task
        return _empty_run(sandbox=str(sandbox), error=str(e))


def check_hard_gates(task: dict, cwd: Path) -> dict:
    """Corre os gates esperados (PHPStan, Pest, etc.) no sandbox pós-task."""
    gates = task["expected"].get("hard_gates", {})
    results = {}

    gate_commands = {
        "phpstan_passes": ["./vendor/bin/phpstan", "analyse", "--no-progress"],
        "pint_clean": ["./vendor/bin/pint", "--test"],
        "pest_passes": ["./vendor/bin/pest", "--parallel"],
        "vitest_passes": ["pnpm", "run", "test"],
        "vue_tsc_clean": ["pnpm", "run", "typecheck"],
        "build_succeeds": ["pnpm", "run", "build"],
    }

    for gate_name, expected in gates.items():
        cmd = gate_commands.get(gate_name)
        if not cmd:
            results[gate_name] = {"ran": False, "passed": None}
            continue
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=600, cwd=cwd)
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


def check_content(task: dict, run_result: dict, cwd: Path) -> list:
    """Verifica content_checks e must_not_contain_in_any_file (no sandbox)."""
    failures = []
    exp = task["expected"]

    for check in exp.get("content_checks", []):
        path = cwd / check["file"]
        if not path.exists():
            failures.append(f"content_check: {check['file']} does not exist")
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
            fp = cwd / f
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


def run_one_task(task_id: str, policy: dict) -> dict:
    print(f"\n▶ Running eval: {task_id}")
    task = load_task(task_id)
    started = time.time()

    run_result = run_agent(task)
    if run_result.get("error"):
        print(f"  ⚠ agent: {run_result['error']}", file=sys.stderr)
    sandbox = Path(run_result["sandbox"]) if run_result.get("sandbox") else ROOT
    try:
        gates = check_hard_gates(task, sandbox)
        file_check = check_file_expectations(task, run_result)
        content_fails = check_content(task, run_result, sandbox)
        score = score_run(task, run_result, gates, file_check, content_fails)
    finally:
        if run_result.get("sandbox"):
            shutil.rmtree(run_result["sandbox"], ignore_errors=True)

    # Budget guard per task: enforce budgets.max_cost_usd from policy.yml
    max_cost = policy.get("budgets", {}).get("max_cost_usd")
    cost = run_result.get("cost_usd", 0.0)
    score["over_budget"] = bool(max_cost and cost > max_cost)
    if score["over_budget"]:
        print(f"  🛑 task cost ${cost:.2f} exceeded budget ${max_cost}", file=sys.stderr)

    return {
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "wallclock_seconds": time.time() - started,
        "cost_usd": cost,
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

    print("\n=== Eval set comparison ===")
    print(f"Baseline: {baseline_path.name}")
    print(f"Current:  {current_path.name}")
    print(f"\nRegressions: {len(regressions)}")
    for r in regressions:
        print(f"  ✗ {r}")
    print(f"\nImprovements: {len(improvements)}")
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
            print("Specify --task or --all", file=sys.stderr)
            sys.exit(1)

        policy = load_policy()
        # Cumulative cost ceiling for the whole run — configurable per env.
        run_budget = float(os.environ.get("HARNESS_EVAL_MAX_COST_USD", "5"))

        results = []
        total_cost = 0.0
        for tid in task_ids:
            r = run_one_task(tid, policy)
            results.append(r)
            total_cost += r.get("cost_usd", 0.0)
            if total_cost > run_budget:
                print(f"\n🛑 cumulative cost ${total_cost:.2f} exceeded "
                      f"HARNESS_EVAL_MAX_COST_USD ${run_budget} — stopping", file=sys.stderr)
                break

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total": len(results),
            "passed": sum(1 for r in results if r["score"]["passed"]),
            "total_cost_usd": round(total_cost, 4),
            "results": results,
        }
        out = RESULTS_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
        out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        print(f"\n✓ {summary['passed']}/{summary['total']} passed  (cost ${total_cost:.2f})")
        print(f"  Saved to {out.relative_to(ROOT)}")

    elif args.cmd == "compare":
        compare(Path(args.baseline), Path(args.current))


if __name__ == "__main__":
    main()
