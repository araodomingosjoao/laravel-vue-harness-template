#!/usr/bin/env bash
#
# init.sh — inicializa um projecto novo a partir deste template.
#
# Uso (após criar repo a partir do template no GitHub):
#   ./scripts/init.sh
#
# O script:
#   1. Pergunta nome do projecto, descrição, entidade principal
#   2. Substitui placeholders em CLAUDE.md, README.md, .env.example
#   3. Apaga ficheiros que só fazem sentido no template (examples/, CHANGELOG do template)
#   4. Instala o pre-commit hook
#   5. Faz commit inicial com mensagem "chore: initialize from template"
#
# É idempotente: se já correu, detecta e pergunta se quer correr de novo.

set -euo pipefail

# ─── Cores ───────────────────────────────────────────
if [ -t 1 ]; then
    BOLD='\033[1m'
    DIM='\033[2m'
    GREEN='\033[32m'
    YELLOW='\033[33m'
    RESET='\033[0m'
else
    BOLD='' DIM='' GREEN='' YELLOW='' RESET=''
fi

info() { echo -e "${BOLD}▶${RESET} $1"; }
ok()   { echo -e "${GREEN}✓${RESET} $1"; }
warn() { echo -e "${YELLOW}⚠${RESET} $1"; }
ask()  {
    local prompt="$1"
    local default="${2:-}"
    local var
    if [ -n "$default" ]; then
        read -r -p "$prompt [$default]: " var
        var="${var:-$default}"
    else
        read -r -p "$prompt: " var
    fi
    echo "$var"
}

# ─── Verificação de pré-requisitos ────────────────────
if ! [ -f "CLAUDE.md" ] || ! [ -d "scripts" ]; then
    warn "This does not look like the root of a template-based project."
    warn "Run this script from the repo root: ./scripts/init.sh"
    exit 1
fi

# Idempotência: se já não há placeholders, presumivelmente já correu
if ! grep -q '{{PROJECT_NAME}}' CLAUDE.md 2>/dev/null; then
    warn "init.sh seems to have run already (placeholders are gone)."
    read -r -p "Continue anyway? [y/N] " ans
    [ "${ans,,}" = "y" ] || { echo "Cancelled."; exit 0; }
fi

# ─── Banner ──────────────────────────────────────────
cat <<EOF

${BOLD}┌─────────────────────────────────────────────┐
│  Laravel + Vue harness — initialization     │
└─────────────────────────────────────────────┘${RESET}

I'll ask you 4 short questions and then prepare the repo.
Everything else follows the template conventions — edit by hand later.

EOF

# ─── Perguntas ───────────────────────────────────────
PROJECT_NAME=$(ask "Project name" "$(basename "$PWD")")
PROJECT_DESC=$(ask "Short description (1 sentence)")
MAIN_ENTITY=$(ask "Main domain entity (e.g. Order, Lead, Post)")
DATABASE=$(ask "Database [Postgres/MySQL]" "Postgres")

TODAY=$(date +%Y-%m-%d)

echo ""
info "Summary:"
echo "  Name:         $PROJECT_NAME"
echo "  Description:  $PROJECT_DESC"
echo "  Entity:       $MAIN_ENTITY"
echo "  DB:           $DATABASE"
echo "  Date:         $TODAY"
echo ""
read -r -p "Proceed? [Y/n] " confirm
[ "${confirm,,}" = "n" ] && { echo "Cancelled."; exit 0; }

# ─── Substituições ───────────────────────────────────
info "Replacing placeholders..."

# Cross-platform sed in-place (Linux usa -i'', macOS pede -i '')
sed_inplace() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# Lista explícita de ficheiros com placeholders.
# Usamos lista explícita (não glob) para EVITAR substituir em sítios onde
# {{PROJECT_NAME}} aparece literalmente — por exemplo, dentro de workflows do
# template (template-release.yml, template-bump.yml) que verificam placeholders.
TARGETS=(
    "CLAUDE.md"
    "README.md"
    ".env.example"
    "tests/harness/eval-set/MANIFEST.yml"
    "docker-compose.yml"
    "composer.json"
    "package.json"
    "resources/js/App.vue"
)

for f in "${TARGETS[@]}"; do
    [ -f "$f" ] || continue
    sed_inplace "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$f"
    sed_inplace "s|{{PROJECT_DESCRIPTION}}|$PROJECT_DESC|g" "$f"
    sed_inplace "s|{{MAIN_ENTITY}}|$MAIN_ENTITY|g" "$f"
    sed_inplace "s|{{DATABASE}}|$DATABASE|g" "$f"
    sed_inplace "s|{{TODAY}}|$TODAY|g" "$f"
    # Placeholders genéricos que não foram preenchidos — comentário ajuda futuros leitores
    sed_inplace "s|{{TERM}}|example|g" "$f"
done

ok "Placeholders replaced in ${#TARGETS[@]} files"

# ─── Apagar ficheiros do template ────────────────────
info "Removing files that only make sense in the template..."

# examples/ tem o sample do todo-list — podes apagar ou guardar para referência
read -r -p "Delete the examples/ folder now? [N/y] " del_examples
if [ "${del_examples,,}" = "y" ]; then
    rm -rf examples/
    ok "examples/ deleted"
else
    info "examples/ kept — delete it manually when you no longer need it"
fi

# CHANGELOG do template (vais começar o teu próprio)
if [ -f "CHANGELOG.template.md" ]; then
    rm -f CHANGELOG.template.md
    ok "Template CHANGELOG removed"
fi

# Workflows que só fazem sentido no repo do template em si (release, bump version).
# O teu projecto não os deve manter — vai gerir as suas próprias releases.
TEMPLATE_WORKFLOWS=(
    ".github/workflows/template-release.yml"
    ".github/workflows/template-bump.yml"
)
removed_workflows=0
for w in "${TEMPLATE_WORKFLOWS[@]}"; do
    if [ -f "$w" ]; then
        rm -f "$w"
        removed_workflows=$((removed_workflows + 1))
    fi
done
[ "$removed_workflows" -gt 0 ] && ok "Template workflows removed ($removed_workflows files)"

# Ficheiro de versão do template — guardamos para upgrades futuros mas não é editável
# (já está no projecto inicializado, não precisa de mudar)

# init.sh em si — depois de correr, não faz sentido manter
read -r -p "Delete this script (scripts/init.sh) now that it has run? [N/y] " del_init
if [ "${del_init,,}" = "y" ]; then
    # Não podemos apagar enquanto está a correr — marcamos para apagar no fim
    DELETE_SELF=1
else
    DELETE_SELF=0
fi

# ─── Pre-commit hook ─────────────────────────────────
info "Installing the pre-commit hook..."
if [ -d ".git/hooks" ]; then
    ln -sf "../../scripts/pre-commit" .git/hooks/pre-commit
    chmod +x scripts/pre-commit
    ok "Pre-commit hook installed"
else
    warn ".git/hooks not found — is this project under git?"
    warn "Run 'git init', then 'ln -sf ../../scripts/pre-commit .git/hooks/pre-commit'"
fi

# ─── Diretórios .harness ─────────────────────────────
mkdir -p .harness/state .harness/traces
echo "*" > .harness/.gitignore
echo "!.gitignore" >> .harness/.gitignore
ok ".harness/ created (already gitignored)"

# ─── Commit inicial ──────────────────────────────────
if [ -d ".git" ]; then
    read -r -p "Create the initial commit with these changes? [Y/n] " do_commit
    if [ "${do_commit,,}" != "n" ]; then
        git add -A
        git commit -m "chore: initialize $PROJECT_NAME from harness template

- Replaced placeholders ({{PROJECT_NAME}}, {{MAIN_ENTITY}}, etc.)
- Installed the pre-commit hook
- Created .harness/ for state and traces
" >/dev/null 2>&1 && ok "Initial commit created" || warn "Commit failed — do it by hand"
    fi
fi

# ─── Self-delete se pedido ───────────────────────────
if [ "$DELETE_SELF" = "1" ]; then
    # Truque: agendar apagar depois do exit
    trap "rm -f scripts/init.sh; ok 'scripts/init.sh removed'" EXIT
fi

# ─── Próximos passos ─────────────────────────────────
cat <<EOF

${GREEN}${BOLD}✓ Harness initialized for "$PROJECT_NAME"${RESET}

${BOLD}Next steps:${RESET}

  1. ${DIM}Edit CLAUDE.md${RESET} → "Modelo de dados" and "Domínio" sections
  2. ${DIM}Edit .env${RESET} → cp .env.example .env and fill it in
  3. ${DIM}Configure the CI secret${RESET} → CLAUDE_CODE_OAUTH_TOKEN (see README §5)
  4. ${DIM}Install dependencies${RESET} → composer install && pnpm install
  5. ${DIM}Start the sandbox${RESET} → docker-compose up -d
  6. ${DIM}Write the first ADR${RESET} → cp examples/adrs/*.md docs/adr/001-... (if you kept examples/)
  7. ${DIM}Add the first eval task${RESET} → see examples/eval-tasks/

${BOLD}Docs:${RESET}

  - README.md                 ← overview
  - docs/template/UPGRADE.md   ← how to receive template updates later

EOF
