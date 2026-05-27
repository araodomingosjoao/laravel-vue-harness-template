# Laravel + Vue harness template

> Template GitHub para projectos Laravel 12 + Vue 3 construídos maioritariamente
> por agentes de IA (Claude Code, Cursor, etc.) com humano no papel de reviewer.

[![Template version](https://img.shields.io/badge/template-v2.1.0-blue)](CHANGELOG.template.md)

## Para que serve

Se vais construir um projecto Laravel + Vue e queres usar agentes de IA de forma
**segura e auditável** desde o dia zero, este template dá-te:

- Convenções claras que o agente respeita (`CLAUDE.md`)
- Sub-agentes especializados em backend e frontend
- Sensores que apanham bugs antes do PR (PHPStan, Pint, Pest, vue-tsc, ESLint, Vitest)
- AI review (qualidade + segurança) via Claude Code Action — comentários inline no PR; rubrica = o teu `CLAUDE.md`; corre na tua subscrição (OAuth) ou via API
- Kill switch e budgets para limitar danos quando algo correr mal
- Eval set para detectar regressões
- Trajectory logging para perceber o que o agente realmente fez
- Dashboard de saúde do harness

Não é "demo bonita". É production-grade.

## Começar

### 1. Criar um projecto a partir deste template

No GitHub: clica em **"Use this template"** → **"Create a new repository"**.

Ou via CLI com a [GitHub CLI](https://cli.github.com/):
```bash
gh repo create meu-projecto --template araodomingosjoao/laravel-vue-harness-template --private
```

### 2. Inicializar

```bash
cd meu-projecto
./scripts/init.sh
```

O script faz 4 perguntas curtas e prepara tudo. Demora menos de um minuto.

### 3. Instalar dependências

```bash
composer install
pnpm install
cp .env.example .env
php artisan key:generate
```

### 4. Levantar o sandbox

```bash
docker-compose up -d
docker-compose exec app php artisan migrate
```

### 5. Configurar o CI

**Subscrição (sem custos de API).** Corre `claude setup-token` localmente e guarda
o resultado em **Settings → Secrets and variables → Actions → New repository
secret** como `CLAUDE_CODE_OAUTH_TOKEN`. Este token serve o `ai-review` e o
`eval-set` — ambos correm na tua subscrição Pro/Max, não na API. Sem ele, o
`ai-review` é saltado (não falha o CI). *(Sem subscrição? Troca
`claude_code_oauth_token` por `anthropic_api_key` no `agent-pr.yml`.)*

**Jobs opcionais (repo Variables, desligados por defeito):**

- `HARNESS_EVAL_SET=true` — eval set semanal, na **subscrição** (`CLAUDE_CODE_OAUTH_TOKEN`);
  teto de custo via `HARNESS_EVAL_MAX_COST_USD` (default `$5`). Localmente corre só
  com `python scripts/eval.py run --all` (usa a tua sessão logada, sem secret).
- `HARNESS_SECURITY_REVIEW=true` — passe de segurança dedicado em cada PR. **É o
  único que exige API** (`ANTHROPIC_API_KEY`), porque a action de segurança não
  suporta subscrição.

> Se usares a API (security-review), define um **spend limit** no Anthropic Console
> (platform.claude.com → Limits/Billing) — é o único tecto fiável. O `eval-set` na
> subscrição é limitado pela tua quota, não pelos $.

**Claude GitHub App — obrigatório para os jobs de IA.** Instala o app em
github.com/apps/claude (ou `/install-github-app` no Claude Code) e seleciona o
repo. A `claude-code-action` (usada pelo `ai-review` e pelo `claude.yml`) troca
por um token de app para agir no GitHub — **sem o app, esses jobs falham** com
*"Claude Code is not installed on this repository"*. Instalá-lo também faz os PRs
do agente dispararem o `agent-pr.yml` (um PR aberto só pelo `GITHUB_TOKEN` não
dispara outros workflows).

**Implementação conduzida pelo agente (`claude.yml`).** Com o app instalado,
menciona `@claude` num issue ou comentário de PR (ex.: *"@claude adiciona um
endpoint GET /api/ping"*) → o agente implementa numa branch e abre/atualiza o PR,
na tua subscrição; os gates + reviews validam-no.

### 6. Validar que tudo funciona

```bash
composer gates && pnpm gates
python scripts/dashboard.py
```

Se ambos passam, estás pronto para começar a pedir features ao agente.

## Stack assumida

| Camada | Tecnologia | Versão |
|---|---|---|
| Backend | Laravel | 12 |
| PHP | | 8.4 |
| Base de dados | PostgreSQL | 18 |
| Frontend | Vue + TypeScript | 3.5 + 6 |
| Bundler | Vite | 8 |
| Testes BE | Pest | 4 |
| Testes FE | Vitest | 4 |
| E2E | Playwright | 1.60+ |
| Análise estática | PHPStan + Larastan | level 8 (Larastan 3) |
| Style | Pint | preset Laravel |

> **Princípio: segue as últimas versões estáveis _que o ecossistema suporta_.**
> Referencia as versões estáveis mais recentes que **resolvem e passam os gates**.
> "Última" não é "bleeding edge a todo o custo": se uma major nova ainda não tem
> suporte das dependências (ex.: um pacote first-party que ainda capa na major
> anterior), fica na anterior até resolver — foi por isso que ficámos em Laravel
> 12 e não 13. Corre sempre `composer gates && pnpm gates` antes de assumir que um
> bump está bem. As versões acima reflectem o estado em 2026-05.

Se queres uma stack diferente, faz fork e adapta. O template não tenta ser
agnóstico — é deliberadamente focado.

## Estrutura

```
.
├── CLAUDE.md                 # Convenções do projecto (lido pelo agente)
├── LEARNINGS.md              # Memória volátil entre sessões
├── README.md                 # Este ficheiro (no projecto novo, substitui-o)
├── CHANGELOG.template.md     # Versões do template
├── .harness-template-version # Versão actual do template usado
│
├── .claude/agents/           # Sub-agentes especializados
│   ├── spec-writer.md
│   ├── laravel-backend.md
│   └── vue-frontend.md
│
├── .github/                  # CI/CD, templates de issues e PRs
│   ├── workflows/agent-pr.yml   # gates + AI review + security review + e2e
│   ├── workflows/claude.yml     # @claude → o agente implementa e abre PR
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── config/harness/           # Política do harness
│   ├── policy.yml            # Budgets, rate limits, kill switch, risco
│   └── dependencies.yml      # Allow-list de packages
│
├── scripts/                  # Ferramentas operacionais
│   ├── init.sh               # Bootstrap interactivo
│   ├── pre-commit            # Detecção de segredos
│   ├── budget_check.py       # Enforcement de budgets
│   ├── classify_risk.py      # Risco por path
│   ├── trajectory.py         # Logging estruturado
│   ├── dashboard.py          # Métricas
│   ├── eval.py               # Eval set runner
│   └── check_dependencies.py # Allow-list enforcement
│
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   ├── handoffs/             # Contrato backend → frontend
│   └── template/             # Documentação do template em si
│       ├── PHILOSOPHY.md
│       └── UPGRADE.md
│
├── tests/harness/
│   └── eval-set/             # Tasks-padrão para benchmark
│
├── examples/                 # APAGADO pelo init.sh — exemplos só do template
│   ├── eval-tasks/
│   ├── adrs/
│   └── learnings/
│
├── phpstan.neon              # Larastan level 8
├── pint.json                 # Style PHP
├── composer.json             # Scripts: gates, test, lint
├── package.json              # Scripts: gates, test, typecheck
└── docker-compose.yml        # Sandbox isolado
```

## Próximos passos depois do init

Lê estes ficheiros, por esta ordem:

1. **`CLAUDE.md`** — entende as convenções que o agente vai seguir
2. **`docs/template/PHILOSOPHY.md`** — entende porque as decisões foram feitas assim
3. **`config/harness/policy.yml`** — ajusta budgets se o defaults não te servem
4. **`examples/eval-tasks/add-priority-field/`** — exemplo completo de eval task

Depois adapta:

- **`CLAUDE.md`** → preenche a secção "Modelo de dados" com as tuas entidades
- **`docs/adr/`** → começa a registar decisões arquitecturais à medida que as tomas
- **`tests/harness/eval-set/`** → cria a tua primeira eval task baseada num caso real

## Manutenção do template

Quando este template recebe updates, o teu projecto **não** os recebe automaticamente.
Vê [`docs/template/UPGRADE.md`](docs/template/UPGRADE.md) para o processo.

## Filosofia em uma linha

> O agente escreve código. Os sensores validam. O humano aprova o que importa.

Para mais detalhe sobre as decisões de design, vê
[`docs/template/PHILOSOPHY.md`](docs/template/PHILOSOPHY.md).

## Licença

MIT.
