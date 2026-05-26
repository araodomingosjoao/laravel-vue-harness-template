# ADR-001: Estado de conclusão como timestamp, não boolean

**Status**: accepted
**Data**: 2026-04-01
**Decisores**: equipa backend

## Contexto

Ao modelar todos, tínhamos duas opções para representar "concluído":

1. `is_completed: boolean` — simples, óbvio
2. `completed_at: timestamp nullable` — `null` = não concluído, data = quando foi concluído

A maior parte das aplicações começa com opção 1 porque é o instinto natural.
Mas descobrimos pedidos recorrentes ao longo do primeiro mês:
- "quando é que o user X completou esta task?"
- "mostra-me todas as tasks concluídas esta semana"
- "qual o tempo médio entre criar e concluir um todo?"

Todos eles exigem o timestamp. Tê-lo de raiz evita migrações tardias e
double-source-of-truth (ter ambos `is_completed` e `completed_at`).

## Decisão

Usamos `completed_at: timestamp nullable`. Não temos coluna boolean.
"Está concluído?" calcula-se: `completed_at !== null`.

## Consequências

### Positivas
- Auditoria temporal grátis
- Queries de analytics directas
- Uma coluna em vez de duas

### Negativas / trade-offs aceites
- Código de leitura ligeiramente mais verboso (`->whereNotNull('completed_at')` vs `->where('is_completed', true)`)
- Frontend tem de saber que `completed_at` string não-vazia significa concluído

### Áreas afectadas
- `app/Models/Todo.php`
- `database/migrations/*_create_todos_table.php`
- `app/Http/Resources/TodoResource.php`
- `resources/js/types/Todo.ts`
- Qualquer query que filtre por estado de conclusão

## Como o agente usa isto

Se uma task pedir "adiciona campo `is_completed`" ou "muda completed_at para boolean",
o agente deve:
1. Apontar este ADR
2. Confirmar com o developer se há razão para reverter a decisão
3. Se sim, criar ADR-NNN a superseder esta antes de mudar código
