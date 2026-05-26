# Eval set do harness

Sem isto, qualquer mudança no harness é fé cega. Esta suite executa o agente contra
um conjunto de tasks-padrão e verifica que produz outputs aceitáveis.

## Quando correr

- Antes de mudar `CLAUDE.md` significativamente
- Antes de mudar o modelo (ex: subir de Sonnet para Opus)
- Antes de mudar prompts dos sub-agentes
- Semanalmente em CI (para detectar regressão silenciosa de modelos da Anthropic/OpenAI)

## Estrutura de cada eval

Cada task vive em `tasks/<nome>/` com:

```
tasks/add-priority-field/
├── prompt.md                # o que pedimos ao agente
├── starting_state.tar.gz    # snapshot do repo antes da task
├── expected.yml             # critérios mensuráveis de sucesso
└── rubric.md                # critérios qualitativos para AI-as-judge
```

## Critérios de sucesso (em expected.yml)

Cada eval tem múltiplos critérios — não basta "passa nos testes":

```yaml
hard_gates:                  # se algum falhar, eval falha (boolean)
  - phpstan_passes: true
  - pint_clean: true
  - tests_pass: true
  - build_succeeds: true

required_files_created:
  - app/Models/Todo.php
  - database/migrations/*_add_priority_to_todos_table.php
  - tests/Feature/TodoPriorityTest.php

required_files_modified:
  - app/Http/Controllers/Api/TodoController.php
  - resources/js/types/Todo.ts

forbidden_changes:
  - .env
  - composer.json            # não devia adicionar dependências
  - config/auth.php          # task é sobre todos, não auth

scoring:
  files_changed_max: 12      # se mexer em mais, penaliza
  files_changed_target: 8
  lines_changed_max: 400
  tool_calls_max: 40
  duration_max_seconds: 600

ai_judge_min_score: 0.75     # rubrica avaliada por LLM-as-judge
```

## Métricas tracked ao longo do tempo

Para cada run guardamos em `results/<timestamp>.json`:

- Pass rate (% de evals que passam todos os hard gates)
- Mean score (média dos AI judge scores)
- Mean duration por eval
- Mean cost por eval
- Detecção de regressão (qualquer eval que passou antes e agora falha)

## Como adicionar um novo eval

1. Reproduz uma task real onde o agente falhou ou onde queres garantir competência
2. Cria a directoria com os 4 ficheiros acima
3. Corre `python scripts/eval.py run --task <nome>` para validar
4. Adiciona ao `tasks/MANIFEST.yml`

## Política de evolução

- **Nunca apagar evals** — só marcar como deprecated em MANIFEST.yml
- **Nunca relaxar critérios** sem documentar razão
- Quando um eval passa de "falha" para "passa" 3 vezes seguidas, podes apertar os critérios
