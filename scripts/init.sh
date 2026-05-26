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
    warn "Não pareço estar na raiz de um projecto baseado no template."
    warn "Corre este script a partir da raiz: ./scripts/init.sh"
    exit 1
fi

# Idempotência: se já não há placeholders, presumivelmente já correu
if ! grep -q '{{PROJECT_NAME}}' CLAUDE.md 2>/dev/null; then
    warn "Parece que init.sh já correu antes (placeholders já substituídos)."
    read -r -p "Continuar mesmo assim? [y/N] " ans
    [ "${ans,,}" = "y" ] || { echo "Cancelado."; exit 0; }
fi

# ─── Banner ──────────────────────────────────────────
cat <<EOF

${BOLD}┌─────────────────────────────────────────────┐
│  Inicialização do harness Laravel + Vue     │
└─────────────────────────────────────────────┘${RESET}

Vou fazer-te 4 perguntas curtas e depois preparar o repo.
Tudo o resto segue convenções do template — podes editar à mão depois.

EOF

# ─── Perguntas ───────────────────────────────────────
PROJECT_NAME=$(ask "Nome do projecto" "$(basename "$PWD")")
PROJECT_DESC=$(ask "Descrição curta (1 frase)")
MAIN_ENTITY=$(ask "Entidade principal do domínio (ex: Order, Lead, Post)")
DATABASE=$(ask "Base de dados [Postgres/MySQL]" "Postgres")

TODAY=$(date +%Y-%m-%d)

echo ""
info "Resumo:"
echo "  Nome:        $PROJECT_NAME"
echo "  Descrição:   $PROJECT_DESC"
echo "  Entidade:    $MAIN_ENTITY"
echo "  DB:          $DATABASE"
echo "  Data:        $TODAY"
echo ""
read -r -p "Prosseguir? [Y/n] " confirm
[ "${confirm,,}" = "n" ] && { echo "Cancelado."; exit 0; }

# ─── Substituições ───────────────────────────────────
info "A substituir placeholders..."

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
    sed_inplace "s|{{TERM}}|exemplo|g" "$f"
done

ok "Placeholders substituídos em ${#TARGETS[@]} ficheiros"

# ─── Apagar ficheiros do template ────────────────────
info "A remover ficheiros que só fazem sentido no template..."

# examples/ tem o sample do todo-list — podes apagar ou guardar para referência
read -r -p "Apagar pasta examples/ agora? [N/y] " del_examples
if [ "${del_examples,,}" = "y" ]; then
    rm -rf examples/
    ok "examples/ apagado"
else
    info "examples/ mantido — apaga manualmente quando já não precisares"
fi

# CHANGELOG do template (vais começar o teu próprio)
if [ -f "CHANGELOG.template.md" ]; then
    rm -f CHANGELOG.template.md
    ok "CHANGELOG do template removido"
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
[ "$removed_workflows" -gt 0 ] && ok "Workflows do template removidos ($removed_workflows ficheiros)"

# Ficheiro de versão do template — guardamos para upgrades futuros mas não é editável
# (já está no projecto inicializado, não precisa de mudar)

# init.sh em si — depois de correr, não faz sentido manter
read -r -p "Apagar este script (scripts/init.sh) agora que correu? [N/y] " del_init
if [ "${del_init,,}" = "y" ]; then
    # Não podemos apagar enquanto está a correr — marcamos para apagar no fim
    DELETE_SELF=1
else
    DELETE_SELF=0
fi

# ─── Pre-commit hook ─────────────────────────────────
info "A instalar pre-commit hook..."
if [ -d ".git/hooks" ]; then
    ln -sf "../../scripts/pre-commit" .git/hooks/pre-commit
    chmod +x scripts/pre-commit
    ok "Pre-commit hook instalado"
else
    warn ".git/hooks não existe — está este projecto sob git?"
    warn "Corre 'git init' e depois 'ln -sf ../../scripts/pre-commit .git/hooks/pre-commit'"
fi

# ─── Diretórios .harness ─────────────────────────────
mkdir -p .harness/state .harness/traces
echo "*" > .harness/.gitignore
echo "!.gitignore" >> .harness/.gitignore
ok ".harness/ criado (já no .gitignore)"

# ─── Commit inicial ──────────────────────────────────
if [ -d ".git" ]; then
    read -r -p "Fazer commit inicial com estas mudanças? [Y/n] " do_commit
    if [ "${do_commit,,}" != "n" ]; then
        git add -A
        git commit -m "chore: initialize $PROJECT_NAME from harness template

- Substituídos placeholders ({{PROJECT_NAME}}, {{MAIN_ENTITY}}, etc.)
- Pre-commit hook instalado
- .harness/ criado para state e traces
" >/dev/null 2>&1 && ok "Commit inicial feito" || warn "Falha no commit — fazer à mão"
    fi
fi

# ─── Self-delete se pedido ───────────────────────────
if [ "$DELETE_SELF" = "1" ]; then
    # Truque: agendar apagar depois do exit
    trap "rm -f scripts/init.sh; ok 'scripts/init.sh removido'" EXIT
fi

# ─── Próximos passos ─────────────────────────────────
cat <<EOF

${GREEN}${BOLD}✓ Harness inicializado para "$PROJECT_NAME"${RESET}

${BOLD}Próximos passos:${RESET}

  1. ${DIM}Editar CLAUDE.md${RESET} → secção "Modelo de dados" e "Domínio"
  2. ${DIM}Editar .env${RESET} → cp .env.example .env e preencher
  3. ${DIM}Configurar secret no GitHub${RESET} → Settings → Secrets → ANTHROPIC_API_KEY
  4. ${DIM}Instalar dependências${RESET} → composer install && npm install
  5. ${DIM}Levantar sandbox${RESET} → docker-compose up -d
  6. ${DIM}Criar primeiro ADR${RESET} → cp examples/adrs/*.md docs/adr/001-... (se mantiveste examples/)
  7. ${DIM}Adicionar primeira eval task${RESET} → ver examples/eval-tasks/

${BOLD}Documentação:${RESET}

  - README.md             ← visão geral
  - docs/template/UPGRADE.md  ← como receber updates do template no futuro

EOF
