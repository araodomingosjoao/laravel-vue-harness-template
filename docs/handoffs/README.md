# Handoff backend → frontend

Este documento é criado pelo agente de backend ao terminar uma feature, e lido
pelo agente de frontend antes de começar. Garante que ambos partilham o
mesmo contrato.

## Como funciona

1. Agente backend termina → escreve `docs/handoffs/<feature-name>.md`
2. Agente backend corre `php artisan typescript:transform` (spatie/laravel-typescript-transformer)
3. Tipos TS gerados são commitados em `resources/js/types/generated/`
4. Agente frontend é invocado COM o handoff doc no contexto
5. Frontend importa de `@/types/generated/`, NUNCA redefine tipos

## Template

```markdown
# Handoff: <nome da feature>

## Endpoints

### GET /api/todos
- Auth: required (sanctum)
- Query params:
  - `priority`: string, opcional, enum: low|medium|high
  - `page`: int, default 1
- Response: 200 — paginated TodoResource collection
- Error: 422 se priority inválido

### PATCH /api/todos/{id}/complete
- Auth: required + ownership policy
- Response: 200 — TodoResource (com completed_at preenchido)
- Error: 403 se não for dono, 404 se não existe, 422 se já concluído

## Tipos gerados

Importar de:
\`\`\`ts
import type { TodoData, TodoCollection } from '@/types/generated'
\`\`\`

## Notas para o frontend

- O campo `priority` é string, não enum TS — usa union literal
- Datas vêm como ISO 8601 strings, parsear com `new Date()` apenas no momento de display
- Paginação devolve `meta.last_page` e `links.next` — usa para paginação infinita

## Migrations necessárias

Já foram executadas no sandbox. Para frontend rodar localmente:
\`\`\`bash
php artisan migrate --seed
\`\`\`
```

## Política

- Frontend **nunca** assume um endpoint sem handoff doc
- Se backend muda contrato a meio, **actualiza o handoff** ANTES de fazer push
- Quando o handoff é actualizado, frontend é re-invocado com diff visível
