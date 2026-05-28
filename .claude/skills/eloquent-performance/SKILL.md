---
name: eloquent-performance
description: Como um sénior evita problemas de performance no Eloquent — N+1, eager loading, índices, queries em loops, datasets grandes. Usa ao implementar ou rever queries de backend.
---

# Eloquent performance (senior)

## N+1 — o erro nº1

Sintoma: um `foreach` sobre uma coleção que acede a uma relação (`$todo->user->name`)
→ 1 query por linha.

- **Eager load**: `Todo::with('user')->get()`. Carrega as relações que o Resource toca.
- `load()` para eager-load depois de já ter o model.
- `withCount('comments')` em vez de `$model->comments->count()`.
- `$with = [...]` no model só para relações *sempre* necessárias (carrega sempre — cuidado).
- O harness liga `Model::preventLazyLoading()` em dev → lazy load rebenta cedo. Aproveita.

## Queries em loops — nunca

- Nada de `Model::find()` / `->save()` dentro de `foreach`. Junta: `whereIn`, `upsert`,
  `insert` em massa.
- Agregações na DB (`sum`, `count`, `avg`), não em PHP sobre coleções carregadas.

## Colunas e índices

- `select(['id', 'title'])` quando não precisas do row inteiro (listas grandes).
- Índice em **toda FK** e em colunas de `where`/`orderBy`/`whereIn`. Índice composto na
  ordem das colunas da query.

## Datasets grandes

- `chunk()` / `lazy()` / `cursor()` para milhares de linhas sem rebentar memória.
- Paginação sempre em endpoints de listagem.

## Como verificar

- Conta queries num teste (`DB::enableQueryLog()`), ou confia no strict mode do harness
  que apanha lazy loading em dev.