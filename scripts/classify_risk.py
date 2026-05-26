#!/usr/bin/env python3
"""
Classifica o risco de um PR baseado nos ficheiros alterados.
Output: critical | high | medium | low

Usado no CI para decidir:
- Quantos reviewers requer
- Se pode auto-merge
- Que gates extra correr
"""

import fnmatch
import subprocess
import sys
from pathlib import Path

import yaml

POLICY_FILE = Path(__file__).parent.parent / "config" / "harness" / "policy.yml"

RISK_ORDER = ["critical", "high", "medium", "low"]


def changed_files(base_ref: str = "origin/main") -> list[str]:
    """Lista ficheiros alterados vs base ref.

    Resiliente: se o base ref estiver vazio, for o SHA nulo (push inicial),
    ou o git falhar (ex.: primeiro commit sem parent, branch não fetchada),
    devolve [] em vez de rebentar — o caller trata isso como risco "low".
    """
    base_ref = (base_ref or "").strip()
    null_ref = base_ref.rsplit("/", 1)[-1].strip("0") == ""
    if not base_ref or null_ref:
        print(f"classify_risk: base ref inválido ('{base_ref}') — sem diff", file=sys.stderr)
        return []

    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(
            f"classify_risk: não consegui fazer diff contra '{base_ref}' "
            f"({result.stderr.strip()}) — a tratar como sem alterações",
            file=sys.stderr,
        )
        return []
    return [f for f in result.stdout.splitlines() if f.strip()]


def matches_any(path: str, patterns: list[str]) -> bool:
    """True se path corresponde a algum padrão glob."""
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
        # Suporte rudimentar para ** (qualquer profundidade)
        if "**" in pattern:
            simple = pattern.replace("**", "*")
            if fnmatch.fnmatch(path, simple):
                return True
            # Tenta também sem o ** (match em qualquer nível)
            parts = pattern.split("**")
            if len(parts) == 2 and path.startswith(parts[0].rstrip("/")) and path.endswith(parts[1].lstrip("/")):
                return True
    return False


def classify_file(path: str, policy: dict) -> str:
    """Retorna a classificação de risco para um único ficheiro."""
    risk_config = policy.get("risk_classification", {})
    for level in RISK_ORDER:
        patterns = risk_config.get(level, {}).get("paths", [])
        if matches_any(path, patterns):
            return level
    return "medium"  # default


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    policy = yaml.safe_load(POLICY_FILE.read_text())

    files = changed_files(base)
    if not files:
        print("low")
        return

    # O risco do PR é o maior risco entre todos os ficheiros
    classifications = [classify_file(f, policy) for f in files]

    for level in RISK_ORDER:
        if level in classifications:
            high_risk_files = [f for f, c in zip(files, classifications) if c == level]
            print(level)
            # Em stderr para o developer ver o detalhe
            print(f"Risco: {level}", file=sys.stderr)
            print(f"Ficheiros que determinam o risco:", file=sys.stderr)
            for f in high_risk_files[:5]:
                print(f"  - {f}", file=sys.stderr)
            return


if __name__ == "__main__":
    main()
