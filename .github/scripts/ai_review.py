#!/usr/bin/env python3
"""
Sensor inferencial: usa Claude para revisar o diff do PR contra uma rubrica.
Falha o CI se forem detectados problemas semânticos que linters não apanham.
"""

import json
import os
import sys
from pathlib import Path

import anthropic

RUBRIC = """
És um code reviewer sénior especializado em Laravel 11 e Vue 3.
Recebes um diff de PR e avalias APENAS contra esta rubrica.

CRITÉRIOS (cada um vale pass/fail):

Backend (PHP/Laravel):
1. Não há N+1 queries (queries dentro de loops, .load() em foreach)
2. Models novos têm $fillable explícito
3. Validação está em Form Requests, não inline no controller
4. Endpoints de listagem usam paginação, não ->all() ou ->get() sem limite
5. Respostas API usam Resources, não retornam Eloquent directamente
6. Authorization usa Policies ou Gates, não if-checks ad-hoc
7. Lógica de negócio não está em controllers (controllers magros)

Frontend (Vue/TS):
8. Sem uso de `any` em TypeScript (excepto com comentário a justificar)
9. Componentes usam `<script setup lang="ts">`, não Options API
10. Stores Pinia usam setup syntax, não Options
11. Sem fetch() directo em componentes — deve passar por composable
12. Inputs têm labels associadas (acessibilidade básica)

RESPOSTA OBRIGATÓRIA — JSON puro, nada mais:
{
  "passed": true|false,
  "violations": [
    {"rule": <número>, "file": "<path>", "line": <int>, "issue": "<descrição curta>"}
  ],
  "summary": "<1-2 frases>"
}

Se o diff for trivial (apenas formatação, comentários, docs), responde com passed: true e violations: [].
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: ai_review.py <diff_file>", file=sys.stderr)
        sys.exit(2)

    diff = Path(sys.argv[1]).read_text()

    if not diff.strip():
        print("Diff vazio, skip.")
        sys.exit(0)

    # Trunca diffs muito grandes — code reviews humanos também não revêem PRs gigantes
    MAX_CHARS = 80_000
    if len(diff) > MAX_CHARS:
        diff = diff[:MAX_CHARS] + "\n\n[... diff truncado ...]"

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        system=RUBRIC,
        messages=[{
            "role": "user",
            "content": f"Diff a rever:\n\n```diff\n{diff}\n```\n\nResponde apenas com o JSON da rubrica.",
        }],
    )

    text = "".join(b.text for b in response.content if b.type == "text").strip()

    # Limpa code fences se o modelo as adicionar
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Falha a parsear resposta do modelo: {e}", file=sys.stderr)
        print(f"Resposta: {text}", file=sys.stderr)
        sys.exit(1)

    # Output formatado para GitHub
    print(f"\n## AI Review\n")
    print(f"**Sumário**: {result.get('summary', '(sem sumário)')}\n")

    violations = result.get("violations", [])
    if violations:
        print(f"### Violações ({len(violations)})\n")
        for v in violations:
            print(f"- **Regra {v['rule']}** em `{v['file']}:{v.get('line', '?')}` — {v['issue']}")

    if not result.get("passed", False):
        print("\n❌ AI review failed")
        sys.exit(1)

    print("\n✅ AI review passed")


if __name__ == "__main__":
    main()
