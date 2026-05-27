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
- Gestor de pacotes do frontend passou de **npm para pnpm** (`packageManager` no `package.json`, `pnpm/action-setup` no CI, `corepack` no docker-compose, docs e agentes)
- Stack actualizada para as últimas versões estáveis que o ecossistema suporta: Laravel 12, PHP 8.4, Vue 3.5, Vite 8, Vitest 4, Pest 4, Larastan 3, ESLint 10, TypeScript 6, Pinia 3, Node 24, Playwright 1.60 (Laravel 13 ainda não resolve — `tinker`/plugins capam em 12)
- AI review do CI migrado do `ai_review.py` (rubrica custom de 12 regras) para a action oficial `anthropics/claude-code-action@v1`: repo-aware, comenta inline, usa o `CLAUDE.md` como rubrica (fonte de verdade única, sem drift) e cobre qualidade **e** segurança num só job. Autentica **só** via subscrição (`CLAUDE_CODE_OAUTH_TOKEN`) — a API key tem precedência e seria cobrada, por isso fica reservada aos jobs opt-in — e salta se o token não estiver configurado
- `eslint.config.js` migrado para a API `defineConfigWithVueTs` (`@vue/eslint-config-typescript` v14)
- Lock files (`composer.lock`, `pnpm-lock.yaml`) passam a ser commitados; o CI usa `--frozen-lockfile`

### Adicionado
- Secção "Convenções de commits" no `CLAUDE.md` — Conventional Commits, em inglês, sem rodapés de co-autoria
- Secção "Convenções de comentários" no `CLAUDE.md` — comentários explicam o porquê, não o quê
- Princípio "segue as últimas versões estáveis que o ecossistema suporta" no `CLAUDE.md` e no `README.md`
- `.gitignore` padrão do Laravel em `bootstrap/cache` e `storage/*` (um clone fresco arranca sem passos manuais)
- Smoke test Playwright (`tests/e2e/smoke.spec.ts`) + `playwright.config.ts` — o job e2e não tinha specs e falhava em qualquer PR de risco ≥ medium
- Jobs pagos opcionais, desligados por defeito e configuráveis por repo Variables: `security-review` (`HARNESS_SECURITY_REVIEW=true`) e `eval-set` (`HARNESS_EVAL_SET=true`), ambos com `ANTHROPIC_API_KEY`
- `eval.py` `run_agent` implementado: corre o `claude` CLI headless num sandbox isolado por task (cópia dos ficheiros tracked + symlink de `vendor`/`node_modules`), captura custo/tokens/diff, corre os gates no sandbox, e aplica tetos de custo — `budgets.max_cost_usd` por task e `HARNESS_EVAL_MAX_COST_USD` por run
- Convenção: o **feedback do harness** (notices/erros do CI, output dos scripts e comentários do AI review) é em **inglês**, mesmo com docs/comentários internos em português

### Corrigido
- `classify_risk.py` rebentava (exit 128) em eventos `push`/`schedule`/`dispatch` porque `github.base_ref` está vazio fora de PRs — agora é resiliente e o workflow usa `HEAD~1` como base nesses eventos
- Template passa agora os próprios gates: `App.vue` válido antes do `init.sh`, `tsconfig` sem `baseUrl` (TS 6), `phpstan.neon` compatível com PHPStan 2, e Pest do CI sem o gate de 80% de cobertura (impossível num esqueleto)

### Removido
- Subsistema da rubrica custom de AI review — `ai_review.py`, `chaos_test.py`, o job `chaos-test` e os fixtures `bad-prs/`. Substituído pela action oficial; calibrar uma rubrica que já não está no pipeline não fazia sentido

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
