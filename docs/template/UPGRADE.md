# Como receber updates do template

Quando o template `laravel-vue-harness-template` for actualizado, projectos
baseados nele NÃO recebem updates automaticamente (GitHub templates fazem uma
cópia única no momento da criação).

Este guia mostra como verificar se há updates e como aplicá-los.

## 1. Verificar a versão actual

O teu projecto tem um ficheiro `.harness-template-version` que regista de
que versão do template foi criado.

```bash
cat .harness-template-version
# 2.0.0
```

Confronta com a [última release do template](https://github.com/araodomingosjoao/laravel-vue-harness-template/releases).

## 2. Decidir se vale a pena fazer upgrade

Lê o `CHANGELOG.template.md` do template entre a tua versão e a actual.
Decide com base em:

- **PATCH** (X.Y.Z+1): quase sempre safe e útil. Faz upgrade.
- **MINOR** (X.Y+1.0): adiciona funcionalidade — opt-in. Faz upgrade se a feature te interessa.
- **MAJOR** (X+1.0.0): breaking. Faz upgrade só se tiveres tempo para migração.

## 3. Aplicar o upgrade

Não há ferramenta automática (seria perigoso — o teu projecto já divergiu).
O processo é manual mas estruturado:

### Estratégia A: ficheiros isolados (PATCH/MINOR sem conflito)

Para mudanças em ficheiros que NÃO editaste no teu projecto (ex: `scripts/`,
`.github/workflows/`, `config/harness/policy.yml`):

```bash
# 1. Adicionar template como remote temporário
git remote add template https://github.com/araodomingosjoao/laravel-vue-harness-template.git
git fetch template

# 2. Cherry-pick os commits relevantes
git log template/main --oneline
git cherry-pick <commit-hash>

# 3. Resolver conflitos se houver, testar
composer gates && npm run gates

# 4. Actualizar versão
echo "2.1.0" > .harness-template-version
git add .harness-template-version
git commit --amend
```

### Estratégia B: diff manual (mudanças sensíveis)

Para ficheiros que personalizaste (ex: `CLAUDE.md`, `phpstan.neon`):

```bash
# 1. Clonar o template numa pasta temporária
git clone https://github.com/araodomingosjoao/laravel-vue-harness-template.git /tmp/template-new

# 2. Comparar ficheiro a ficheiro
diff CLAUDE.md /tmp/template-new/CLAUDE.md

# 3. Trazer mudanças relevantes manualmente
# Decidir caso a caso o que adoptar
```

### Estratégia C: novo projecto (BREAKING)

Para upgrades MAJOR onde a estrutura mudou muito, às vezes é mais simples:

```bash
# 1. Criar novo projecto a partir do template novo
# (no GitHub: Use this template → ...)

# 2. Migrar o código de aplicação (app/, resources/js/, tests/)
cp -r ../projecto-antigo/app .
cp -r ../projecto-antigo/resources/js resources/
cp -r ../projecto-antigo/tests .

# 3. Migrar config específica do projecto
cp ../projecto-antigo/.env .
# CLAUDE.md, LEARNINGS.md, ADRs — copiar e adaptar

# 4. Correr gates para confirmar
composer install && npm install
composer gates && npm run gates
```

## 4. Validar que o upgrade não partiu nada

Antes de fazer merge:

```bash
# Sensores locais
composer gates && npm run gates

# Eval set (detecta regressão do agente após mudanças no harness)
python scripts/eval.py run --all
python scripts/eval.py compare \
  --baseline tests/harness/eval-set/results/<antes-do-upgrade>.json \
  --current tests/harness/eval-set/results/<depois>.json

# Chaos test (confirma que os sensores inferenciais continuam afinados)
python scripts/chaos_test.py
```

## 5. Documentar o upgrade

Adiciona ao teu `CHANGELOG.md` (do projecto, não do template):

```markdown
## [unreleased]

### Mudou
- Upgrade do harness template: 2.0.0 → 2.1.0
- Adoptado: novo dashboard com métricas de custo
- Não adoptado: novo sub-agente de migrations (não aplicável ao nosso projecto)
```

---

## Política de suporte de versões do template

- A última MAJOR é sempre suportada
- A penúltima MAJOR recebe security fixes durante 6 meses após release da nova
- Versões mais antigas: por tua conta

## Quando NÃO fazer upgrade

Sinais de que o upgrade não vale o esforço:

- O teu projecto está em fase final de entrega e estável
- O changelog não menciona nada que te resolva um problema real
- Já personalizaste profundamente as áreas que mudaram
- Não tens tempo para validar com o eval set

O template é uma ajuda, não uma obrigação. Um harness estável e antigo é melhor
do que um harness moderno mas em transição.
