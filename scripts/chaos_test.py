#!/usr/bin/env python3
"""
Chaos test do sensor inferencial.

Corre o AI review contra cada bad-pr e verifica que rejeita correctamente.
Se algum passar, a rubrica está fraca.

Uso:
    python scripts/chaos_test.py
    python scripts/chaos_test.py --diff n-plus-one.diff
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
BAD_PR_DIR = ROOT / "tests" / "harness" / "bad-prs"
AI_REVIEW = ROOT / ".github" / "scripts" / "ai_review.py"


def run_review(diff_path: Path) -> dict:
    """Corre o ai_review.py num diff. Retorna o JSON output do modelo."""
    # O ai_review.py escreve JSON em stdout numa secção; vamos capturá-lo.
    result = subprocess.run(
        [sys.executable, str(AI_REVIEW), str(diff_path)],
        capture_output=True, text=True,
        env={**os.environ, "CHAOS_TEST": "1"},   # flag para devolver JSON puro
    )
    # Procura bloco JSON no output. O ai_review.py em modo CHAOS_TEST
    # devia emitir o JSON cru — aqui assumimos isso.
    output = result.stdout
    try:
        # Tenta parsear a última linha não-vazia como JSON
        for line in reversed(output.strip().split("\n")):
            if line.strip().startswith("{"):
                return json.loads(line)
    except json.JSONDecodeError:
        pass
    return {"passed": result.returncode == 0, "raw": output, "stderr": result.stderr}


def check_one(diff_name: str) -> tuple[bool, str]:
    diff_path = BAD_PR_DIR / diff_name
    expected_path = BAD_PR_DIR / diff_name.replace(".diff", ".expected.yml")

    if not diff_path.exists():
        return False, f"diff não existe: {diff_name}"
    if not expected_path.exists():
        return False, f"expected.yml não existe para {diff_name}"

    expected = yaml.safe_load(expected_path.read_text())
    review = run_review(diff_path)

    # Decisão esperada
    expected_decision = expected.get("expected_decision", "reject")
    actual_passed = review.get("passed", True)

    if expected_decision == "reject" and actual_passed:
        return False, "AI review aprovou um diff que devia rejeitar"
    if expected_decision == "approve" and not actual_passed:
        return False, "AI review rejeitou um diff que devia aprovar"

    # Verifica que as regras certas dispararam
    expected_rules = set(expected.get("expected_rules_triggered", []))
    if expected_rules:
        actual_rules = {v.get("rule") for v in review.get("violations", [])}
        missing = expected_rules - actual_rules
        if missing:
            return False, f"Regras esperadas não dispararam: {missing}"

    return True, "ok"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff", help="Testar apenas um diff específico")
    args = parser.parse_args()

    if args.diff:
        diffs = [args.diff]
    else:
        diffs = sorted(f.name for f in BAD_PR_DIR.glob("*.diff"))

    if not diffs:
        print("Nenhum bad-pr encontrado.", file=sys.stderr)
        sys.exit(1)

    passed = 0
    failed = []

    for d in diffs:
        ok, msg = check_one(d)
        marker = "✓" if ok else "✗"
        print(f"{marker} {d:<40} {msg}")
        if ok:
            passed += 1
        else:
            failed.append((d, msg))

    print()
    print(f"Resultado: {passed}/{len(diffs)} bad-prs rejeitados correctamente")

    if failed:
        print("\nFalhas (rubrica do AI review precisa de ser apertada):")
        for d, msg in failed:
            print(f"  - {d}: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
