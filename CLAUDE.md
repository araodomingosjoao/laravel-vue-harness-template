# {{PROJECT_NAME}} — Convenções do projecto

> **Nota para o developer**: Este ficheiro foi gerado a partir do template
> [laravel-vue-harness-template](https://github.com/araodomingosjoao/laravel-vue-harness-template).
> Edita-o para reflectir as decisões reais do TEU projecto. Os marcadores
> `{{...}}` foram preenchidos pelo `scripts/init.sh`; o conteúdo abaixo é
> o padrão recomendado para qualquer projecto Laravel 11 + Vue 3.

{{PROJECT_DESCRIPTION}}

Este ficheiro é o contexto principal para qualquer agente de IA que trabalhe neste repositório.
Lê-o antes de qualquer task. Se uma instrução aqui conflituar com o prompt do utilizador, pergunta.

## Ordem de leitura obrigatória no início de cada sessão

1. **Este ficheiro (CLAUDE.md)** — convenções estáveis
2. **LEARNINGS.md** — aprendizagens recentes que ainda podem mudar
3. **docs/adr/** — decisões arquitecturais relevantes para os ficheiros que vais tocar
4. **config/harness/policy.yml** — limites e restrições do harness

## Stack

- **Backend**: Laravel 12, PHP 8.4, {{DATABASE}}
- **Frontend**: Vue 3 (Composition API), TypeScript, Pinia, Vite
- **Testes**: Pest (backend), Vitest + Vue Test Utils (frontend), Playwright (e2e)
- **Qualidade**: PHPStan/Larastan level 8, Pint, ESLint, vue-tsc

> **Segue as últimas versões estáveis que o ecossistema suporta.** Ao adicionar
> ou actualizar dependências, usa a versão estável mais recente que **resolve e
> passa os gates** (verifica em packagist.org / npmjs.com). "Última" não é
> bleeding-edge a todo o custo: se uma major nova ainda não tem suporte das
> dependências, fica na anterior até resolver. Confirma sempre com
> `composer gates && pnpm gates` depois de mexer em versões. A base de dados é
> **PostgreSQL** (não MySQL) e o gestor de pacotes do frontend é **pnpm** (não npm).

## Estrutura do repo

```
app/
  Http/Controllers/Api/    # apenas controllers API, resource ou invokáveis
  Http/Requests/           # Form Requests para validação, nunca validação inline
  Http/Resources/          # API Resources para serialização
  Models/                  # Eloquent models, sempre com $fillable explícito
  Services/                # lógica de negócio que não pertence ao model
database/
  migrations/
  factories/
  seeders/
routes/api.php             # toda a API vive aqui, agrupada por prefixo
tests/
  Feature/                 # testes de endpoint end-to-end (preferidos)
  Unit/                    # apenas para classes puras sem DB
resources/js/
  components/              # componentes Vue, um por ficheiro, PascalCase
  composables/             # use* hooks, camelCase
  stores/                  # Pinia stores, sufixo Store.ts
  views/                   # páginas de rota
  router/
  types/                   # tipos TS partilhados (manuais)
  types/generated/         # tipos TS gerados do backend (NUNCA editar à mão)
```

## Regras de ouro

### Backend

1. **Nunca validação inline.** Cria sempre um Form Request:
   ```php
   php artisan make:request StoreSomethingRequest
   ```

2. **Nunca devolver Eloquent directamente.** Usa sempre um Resource:
   ```php
   return SomethingResource::collection($items);
   ```

3. **`$fillable` é obrigatório** em todos os models. Mass assignment sem `$fillable` é um bug.

4. **Sem queries em loops.** Se vês um `foreach` com `->load()` ou `->relation` dentro, refactoriza para eager loading (`with()`).

5. **Paginação por defeito.** Endpoints de listagem usam `->paginate(20)`, nunca `->all()` ou `->get()` sem limite.

6. **Controllers magros.** Lógica de negócio vai para `app/Services/`. Controllers só orquestram: validar → chamar service → devolver resource.

7. **Authorization via Policy**, nunca `if ($user->id === $resource->user_id)` espalhado pelo código.

### Frontend

1. **Composition API com `<script setup lang="ts">`**. Nunca Options API.

2. **Pinia stores com setup syntax**:
   ```ts
   export const useThingsStore = defineStore('things', () => {
     const items = ref<Thing[]>([])
     // ...
     return { items, fetchAll }
   })
   ```

3. **Tipos partilhados em `resources/js/types/generated/`**. Gerados do backend, nunca editados à mão.

4. **Fetch via composable**, nunca `fetch()` directo no componente. Usa `useApi()` que já trata de CSRF e erros.

5. **Componentes pequenos**. Se um componente passa de 150 linhas, parte em sub-componentes ou extrai um composable.

6. **Sem `any`**. Se precisas de `any`, escreve `unknown` e faz narrowing.

## Para tasks vagas ou de escopo grande

Se o pedido for vago, **invoca primeiro o sub-agente `spec-writer`**. Não inventes decisões.

## Workflow obrigatório para cada task

1. **Lê primeiro** — usa grep/glob para encontrar ficheiros relevantes antes de escrever código novo.
2. **Planeia em voz alta** — descreve os ficheiros que vais criar/modificar antes de o fazer.
3. **Backend antes do frontend** — define o contrato da API primeiro, depois o frontend consome.
4. **Teste com o código** — cada endpoint novo tem teste Pest, cada componente Vue tem teste Vitest.
5. **Corre os sensores antes de declarar terminado**:
   ```bash
   composer gates
   pnpm gates
   ```
6. **Se algum sensor falhar, arranja antes de avançar.** Não abras PR com testes vermelhos.

## Antes de fazer commit

- Pre-commit hook em `scripts/pre-commit` apanha segredos
- Corre `composer gates && pnpm gates` para validar tudo localmente
- Se vais adicionar uma dependência, verifica `config/harness/dependencies.yml` primeiro
- Mensagem de commit no formato Conventional Commits (ver "Convenções de commits")

## Comandos úteis

```bash
# Backend
php artisan make:model Thing -mfsc        # model + migration + factory + seeder + controller
php artisan make:request StoreThingRequest
php artisan make:resource ThingResource
php artisan route:list --path=api         # ver todas as rotas API
php artisan tinker                        # REPL para experimentar queries

# Qualidade
composer gates                            # Pint + PHPStan + Pest
pnpm gates                                # typecheck + lint + vitest
```

## Convenções de naming

- **Migrations**: `create_things_table`, `add_status_to_things_table`
- **Models**: singular PascalCase — `Thing`, não `Things`
- **Controllers**: `ThingController` (resource) ou `CompleteThingController` (invokável)
- **Requests**: `StoreThingRequest`, `UpdateThingRequest`
- **Tests**: `ThingTest.php` para feature, descreve com `it('does something', ...)`
- **Componentes Vue**: `ThingList.vue`, `ThingItem.vue` — PascalCase
- **Composables**: `useThings.ts` — camelCase com prefixo `use`
- **Stores**: `thingsStore.ts` exporta `useThingsStore`

## Convenções de comentários

Comentários explicam o **porquê**, não o **quê**. O código já diz o quê; um
comentário só ganha o seu lugar quando acrescenta algo que o código não consegue
dizer sozinho.

**Comenta quando:**
- A razão de uma decisão não é óbvia — um workaround, uma escolha contra-intuitiva, um *gotcha* que evita uma regressão futura.
- Uma omissão é deliberada e alguém a desfaria sem saber porquê (ex.: "sem cache aqui: este job não instala").

**NÃO comentes quando:**
- Apenas narras a linha seguinte (`// incrementa o contador`).
- Repetes o nome da função, variável ou job (um job `code-review` não precisa de um comentário a dizer "faz review do código").
- Explicas uma ausência ("não precisamos de X") — a ausência não precisa de justificação.
- Documentas a versão ou o estado actual, que o git e o `CHANGELOG` já registam.

**Forma:**
- Curto. Uma linha chega quase sempre; se precisas de um parágrafo, talvez o código devesse ser mais claro.
- Iguala a densidade de comentários do código à volta — não introduzas um estilo mais verboso do que o ficheiro já tem.
- Prefere docstrings/PHPDoc a comentários soltos quando a linguagem os suporta e eles acrescentam tipo ou contrato.

> Na dúvida, não comentes. É mais fácil acrescentar um comentário em falta do que limpar ruído.

**Idioma do feedback:** comentários e docs do projecto são em português, mas tudo
o que o harness **emite como feedback** — mensagens de CI (`::notice::`/`::error::`),
output dos scripts, e os comentários do AI review nos PRs — é em **inglês** (a
mesma regra dos commits).

## Convenções de commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/). É o padrão
que os devs experientes usam para manter o histórico legível e gerar changelogs.

Formato:

```
<tipo>(<escopo opcional>): <descrição no imperativo, minúsculas, sem ponto final>

<corpo opcional: explica o PORQUÊ da mudança, não o quê>

<rodapé opcional: BREAKING CHANGE:, Refs #issue, Closes #issue>
```

**Tipos permitidos:**

- `feat` — nova funcionalidade
- `fix` — correcção de bug
- `docs` — só documentação
- `style` — formatação sem alterar lógica (espaços, Pint, ESLint)
- `refactor` — mudança de código que não corrige bug nem adiciona feature
- `perf` — melhoria de performance
- `test` — adicionar ou corrigir testes
- `build` — build ou dependências (composer, pnpm, Vite, Docker)
- `ci` — alterações ao CI (`.github/workflows`)
- `chore` — manutenção sem impacto em código de produção ou testes

**Regras:**

- **Mensagem sempre em inglês** (assunto, corpo e rodapé), mesmo que o resto do repo esteja em português.
- Assunto ≤ 72 caracteres, no imperativo em inglês ("add", não "added"/"adds"), sem ponto final.
- Escopo opcional identifica a área: `feat(api): ...`, `fix(auth): ...`, `test(things): ...`.
- Breaking changes: `feat!: ...` ou rodapé `BREAKING CHANGE: <descrição>`.
- Um commit = uma mudança lógica. Não misturar refactor com feature.
- Liga ao issue no rodapé quando aplicável: `Refs #123` / `Closes #123`.
- **Não adicionar rodapés de co-autoria** (ex.: `Co-Authored-By`), de agentes de IA ou outros.

**Exemplos:**

```
feat(api): add paginated listing endpoint for things
fix(auth): fix token expiry on refresh
refactor(services): extract price calculation into PriceCalculator
docs: document the eval workflow in the README
test(things): cover the empty pagination case
```

## O que NÃO fazer

- Não correr `php artisan migrate:fresh` em ambientes que não sejam o sandbox local
- Não fazer `composer update` sem pedir — só `composer install`
- Não tocar em ficheiros em `vendor/` ou `node_modules/`
- Não adicionar dependências novas sem justificar e sem actualizar `config/harness/dependencies.yml`
- Não desabilitar regras do PHPStan ou ESLint para "fazer passar" — corrige o código
- Não fazer commit em `main`/`master` directamente — sempre branch + PR

---

## Modelo de dados deste projecto

> **Preencher esta secção** com as entidades principais do projecto.
> O agente usa isto como fonte de verdade do schema.

<!-- EXEMPLO — apagar e substituir com o teu schema real -->

```
{{MAIN_ENTITY}}
├── id (bigint, pk)
├── ...
├── created_at, updated_at
```

## Domínio: vocabulário do projecto

> **Preencher** com termos específicos do domínio que o agente deve conhecer.
> Por exemplo: o que é um "lead" vs "deal", o que significa "active" num utilizador, etc.

<!-- EXEMPLO -->

- **{{TERM}}**: definição
- ...
