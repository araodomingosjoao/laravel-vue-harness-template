# Harness smoke test

Este é o **primeiro eval task** que deves correr num projecto novo.

## Quando correr

- ✅ Logo após `init.sh`, antes de qualquer feature de negócio
- ✅ Após qualquer mudança significativa ao `CLAUDE.md`
- ✅ Após upgrade do template (ver `docs/template/UPGRADE.md`)
- ✅ Após mudar o modelo do agente (ex: subir/descer versão do Claude)

## Como copiar para o teu eval set

```bash
# Após init.sh:
cp -r examples/eval-tasks/harness-smoke-test tests/harness/eval-set/tasks/

# Adicionar ao MANIFEST.yml:
cat >> tests/harness/eval-set/MANIFEST.yml <<EOF
  - id: harness-smoke-test
    category: meta
    description: "Smoke test do harness — task simples para validar setup"
    difficulty: easy
    expected_duration_seconds: 300
    active: true
EOF

# Correr
python scripts/eval.py run --task harness-smoke-test
```

## O que esperar

| Resultado | Significa | Acção |
|---|---|---|
| ✓ passed, `healthy` | Harness OK | Avançar com features reais |
| ✓ passed, `needs_calibration` | Avisos menores | Rever `CLAUDE.md`, ajustar |
| ✗ failed, `broken` | Harness mal configurado | NÃO usar agente até resolver |

## Diagnóstico se falhar

### Os gates falham
- Falha em PHPStan → `phpstan.neon` está com nível mal calibrado ou Larastan não foi instalado
- Falha em Pint → `pint.json` está com regras conflituantes
- Falha em vue-tsc → `tsconfig.json` ou paths mal configurados

### O agente não respeita convenções
- Verifica que o `CLAUDE.md` foi preenchido após `init.sh` (secção "Modelo de dados", etc.)
- Verifica que o sub-agente `laravel-backend.md` e `vue-frontend.md` estão presentes em `.claude/agents/`
- Verifica que o `ANTHROPIC_API_KEY` está configurado

### O agente usa demasiados tool calls
- Pode ser sinal de que o `CLAUDE.md` está demasiado verboso ou contraditório
- Verifica também `LEARNINGS.md` — entradas mal escritas confundem o agente

### Falsos positivos no chaos test
- Refinar rubrica em `.github/scripts/ai_review.py`
- Adicionar exemplos contrastantes em `tests/harness/bad-prs/`
