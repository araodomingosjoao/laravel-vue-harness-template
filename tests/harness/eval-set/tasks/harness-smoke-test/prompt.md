# Task: Smoke test do harness

> **Quando usar**: imediatamente após `init.sh` num projecto novo. Esta task
> verifica que o agente consegue fazer **a coisa mais simples** dentro das
> regras do harness. Se isto falha, o harness está mal configurado.

## Pedido (o que dirias ao agente)

Adiciona um endpoint `GET /api/health-deep` que devolve JSON com:

- `status: "ok"`
- `app_name`: vindo de `config('app.name')`
- `php_version`: `PHP_VERSION`
- `database_connected`: boolean, true se conseguires fazer `DB::select('SELECT 1')` sem erro
- `timestamp`: ISO 8601 do momento actual

Não requer autenticação (é um health check).

No frontend, cria um componente Vue `<HealthBadge>` que:
1. Faz fetch a `/api/health-deep` ao montar
2. Mostra um badge verde ✓ se `status === "ok"`, vermelho ✗ caso contrário
3. Mostra o `app_name` ao lado do badge

Adiciona testes para ambos.

## Porque é "smoke test"

A task é deliberadamente simples mas exercita o caminho crítico do harness:

- ✓ Agente lê `CLAUDE.md` e percebe convenções
- ✓ Cria endpoint seguindo padrão (mesmo sem Form Request — endpoint público sem inputs)
- ✓ Devolve via Resource ou array (decisão menor; ambos aceitáveis)
- ✓ Cria componente Vue com `<script setup lang="ts">`
- ✓ Usa `useApi()` em vez de `fetch()` directo
- ✓ Define tipo TS para a resposta
- ✓ Adiciona testes Pest e Vitest
- ✓ Tudo passa nos gates locais

Se o agente falhar isto, o `CLAUDE.md` está pouco claro, ou os sub-agentes
não foram bem invocados, ou os gates estão mal configurados.

## Tempo esperado

Menos de 5 minutos do agente, menos de 30 tool calls.
