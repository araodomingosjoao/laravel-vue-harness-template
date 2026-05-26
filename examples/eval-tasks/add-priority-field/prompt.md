# Task: Adicionar campo priority aos todos

## Pedido (o que dirias ao agente)

Adiciona um campo `priority` aos todos com três valores possíveis: `low`, `medium`, `high`.
O default é `medium`. Inclui:

1. Migration para adicionar a coluna
2. Update do model `Todo` (fillable, casts se necessário)
3. Validação no `StoreTodoRequest` e `UpdateTodoRequest`
4. Expor o campo no `TodoResource`
5. Permitir filtrar `GET /api/todos?priority=high`
6. UI: badge colorido no `TodoItem.vue` baseado na prioridade
7. UI: dropdown para escolher prioridade no formulário de criação
8. Testes Pest para os novos casos
9. Teste Vitest para o badge

## Contexto adicional

- Este é um campo simples, não inventes uma tabela `priorities` separada
- O default `medium` deve ser definido na migration *e* no model (defensive)
- O filtro deve devolver 422 se passarem valor inválido
