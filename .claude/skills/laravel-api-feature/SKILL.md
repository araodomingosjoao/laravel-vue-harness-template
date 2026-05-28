---
name: laravel-api-feature
description: Playbook sénior para construir uma feature de API REST em Laravel 12 — a sequência migration→model→request→resource→policy→controller→route→teste e as decisões que um sénior toma em cada passo. Usa quando implementas ou planeias um endpoint novo.
---

# Laravel API feature (senior playbook)

Conhecimento procedimental para implementar uma feature de API. As convenções
vivem no `CLAUDE.md` (fonte de verdade); aqui está a *sequência* e os *trade-offs*
que um sénior pesa em cada passo.

## Sequência

1. **Migration** — FKs com `constrained()` + `cascadeOnDelete()` quando faz sentido.
   Índice em toda FK e em colunas usadas em `where`/`orderBy`. `nullable()` deliberado,
   com default explícito.
2. **Model** — `$fillable` explícito (mass assignment sem isto é bug), `casts()`
   (datetime, bool, enum, json), relações tipadas. Nunca `$guarded = []`.
3. **Factory** — com estados (`->completed()`, `->for($user)`) que os testes vão usar.
4. **Form Request** — toda a validação aqui, nunca inline. `authorize()` delega à Policy.
5. **API Resource** — molda a resposta; nunca devolver o model cru. Decide a forma do
   JSON (datas ISO-8601, `whenLoaded` para relações, sem expor colunas internas).
6. **Policy** — se há autorização. `$this->authorize(...)`; nunca `if ($user->id === ...)`
   espalhado pelo código.
7. **Controller** — magro: validar (Request) → orquestrar → devolver Resource. Regras de
   negócio não-triviais vão para um Service (`app/Services/`). Multi-escrita → `DB::transaction()`.
8. **Route** — `routes/api.php`, agrupada por prefixo + middleware (`auth:sanctum`, `throttle:api`).
9. **Teste Pest** — Feature test: happy path + autorização (403) + validação (422) + edge
   cases. Ver a skill `pest-testing`.

## Decisões de sénior

- **Service ou não?** CRUD simples fica no controller. Regras de negócio, várias escritas
  ou reutilização → Service.
- **Transação?** Escreve em >1 tabela ou tem invariantes → `DB::transaction()`.
- **Paginação** por defeito em listagens (`->paginate(20)`), nunca `->get()` sem limite.
- **N+1**: eager-load tudo o que o Resource toca. Ver a skill `eloquent-performance`.
- **Erros**: deixa o Laravel formatar 422/403/404; não inventes formas de erro novas.

## Antes de declarar terminado

```bash
./vendor/bin/pint --test && ./vendor/bin/phpstan analyse && ./vendor/bin/pest
```