# Changelog do harness template

Todas as mudanças notáveis ao **template em si** são registadas aqui.
Não confundir com o CHANGELOG do projecto que usa o template — esse é separado.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/),
e este projecto adere a [Semantic Versioning](https://semver.org/).

## Como interpretar versões

- **MAJOR** (X.0.0): muda contratos. Projectos baseados em versões antigas precisam de migração não-trivial.
- **MINOR** (0.X.0): adiciona capacidades (novo sub-agente, novo script). Retro-compatível.
- **PATCH** (0.0.X): correcções, refinamentos, melhorias de docs. Retro-compatível.

---

## [2.1.0] - 2026-05-26

### Mudou
- Base de dados passou de MySQL para **PostgreSQL 18** (`docker-compose.yml`, serviços do CI, `config/database.php`, `.env.example`, default do `init.sh`)
- Stack actualizada para as últimas versões estáveis: Laravel 13, PHP 8.4, Vue 3.5, Vite 8, Vitest 4, Pest 4, Larastan 3, ESLint 10, TypeScript 6, Pinia 3, Node 24, Playwright 1.60
- `eslint.config.js` migrado para a API `defineConfigWithVueTs` (`@vue/eslint-config-typescript` v14)

### Adicionado
- Secção "Convenções de commits" no `CLAUDE.md` — Conventional Commits, em inglês, sem rodapés de co-autoria
- Princípio "segue sempre as últimas versões estáveis" no `CLAUDE.md` e no `README.md`
- Job `security-review` com a action oficial `anthropics/claude-code-security-review`

### Mudou
- AI review do CI migrado do `ai_review.py` (rubrica custom de 12 regras) para a
  action oficial `anthropics/claude-code-action@v1`: repo-aware, comenta inline,
  e usa o `CLAUDE.md` como rubrica (fonte de verdade única, sem drift)

### Corrigido
- `classify_risk.py` rebentava (exit 128) em eventos `push`/`schedule`/`dispatch`
  porque `github.base_ref` está vazio fora de PRs. O script tornou-se resiliente
  (base inválida/SHA nulo/primeiro commit → risco "low") e o workflow passa a usar
  `HEAD~1` como base nesses eventos.

## [2.0.0] - 2026-05-26

### Mudou (BREAKING)
- Estrutura reorganizada para template GitHub reutilizável
- Ficheiros específicos do projecto agora em `examples/` (são apagados pelo `init.sh`)
- `CLAUDE.md`, `LEARNINGS.md` e `MANIFEST.yml` agora têm placeholders `{{PROJECT_NAME}}`, etc.

### Adicionado
- `scripts/init.sh` — bootstrap interactivo de projecto novo
- `.harness-template-version` — versionamento explícito do template
- `docs/template/UPGRADE.md` — guia para receber updates do template
- Issue templates do GitHub para `.github/ISSUE_TEMPLATE/`

## [1.0.0] - 2026-05-26

### Adicionado
- Sub-agente `spec-writer` que clarifica intent antes da execução
- `LEARNINGS.md` + `docs/adr/` para memória entre sessões
- `docs/handoffs/` para contrato backend → frontend
- `config/harness/policy.yml` com budgets, rate limits, kill switch
- `config/harness/dependencies.yml` com allow-list de packages
- `scripts/budget_check.py` para enforcement de orçamentos
- `scripts/classify_risk.py` para classificação de PRs por risco
- `scripts/trajectory.py` para logging estruturado de tool calls
- `scripts/dashboard.py` para observabilidade do harness
- `scripts/eval.py` runner do eval set
- `scripts/chaos_test.py` para validação dos sensores inferenciais
- `scripts/pre-commit` com detecção de segredos
- `scripts/check_dependencies.py` para enforcement da allow-list
- Workflow CI v2 com classificação de risco e gates condicionais
- Retry e health check no AI review

## [0.1.0] - 2026-05-26

### Adicionado
- Estrutura base com sub-agentes `laravel-backend` e `vue-frontend`
- Convenções no `CLAUDE.md`
- Sensores computacionais: PHPStan/Larastan, Pint, Pest, vue-tsc, ESLint, Vitest
- Sensor inferencial: AI review com rubrica de 12 regras
- Workflow CI básico
- Docker compose para sandbox isolado
