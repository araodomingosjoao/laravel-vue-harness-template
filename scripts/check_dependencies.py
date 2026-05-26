#!/usr/bin/env python3
"""
Verifica que apenas dependências do allow-list estão presentes em composer.json
e package.json. Bloqueia o PR se o agente adicionou um package novo sem aprovação.
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
ALLOWLIST = ROOT / "config" / "harness" / "dependencies.yml"


def main():
    allow = yaml.safe_load(ALLOWLIST.read_text())
    composer_allow = set(allow.get("composer", []))
    npm_allow = set(allow.get("npm", []))
    blocked = set(allow.get("blocked", []))

    violations = []

    # Composer
    composer_json = json.loads((ROOT / "composer.json").read_text())
    for section in ["require", "require-dev"]:
        for pkg in composer_json.get(section, {}):
            if pkg == "php":
                continue
            if pkg in blocked:
                violations.append(f"BLOCKED package: {pkg} (composer)")
            elif pkg not in composer_allow:
                violations.append(f"Não na allow-list: {pkg} (composer)")

    # NPM
    pkg_json = json.loads((ROOT / "package.json").read_text())
    for section in ["dependencies", "devDependencies"]:
        for pkg in pkg_json.get(section, {}):
            if pkg in blocked:
                violations.append(f"BLOCKED package: {pkg} (npm)")
            elif pkg not in npm_allow:
                violations.append(f"Não na allow-list: {pkg} (npm)")

    if violations:
        print("❌ Violações de dependency policy:", file=sys.stderr)
        for v in violations:
            print(f"   {v}", file=sys.stderr)
        print(
            "\nSe esta dependência é legítima, adiciona-a a "
            "config/harness/dependencies.yml num PR separado com justificação.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("✓ Todas as dependências estão na allow-list")


if __name__ == "__main__":
    main()
