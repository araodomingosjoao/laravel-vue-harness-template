---
name: Feature request
about: Sugerir uma nova feature ou capacidade
title: '[FEAT] '
labels: enhancement
assignees: ''
---

## Objectivo de negócio
Uma frase sobre porque é que isto importa.

## Pedido original
Como descreverias isto a um colega humano numa conversa rápida?

## Para o agente
Menciona **@claude** neste issue para delegar a implementação. Se o pedido for
vago ou de escopo grande, o agente usa primeiro o sub-agente `spec-writer`:
publica uma spec e, se ficarem **perguntas em aberto**, pára e pergunta antes de
implementar. Responde nos comentários e volta a mencionar @claude.

Checklist do que costuma ficar por definir (se está em aberto, espera pela spec):

- [ ] Escopo está claro? (API only? UI only? ambos?)
- [ ] Modelo de dados está definido?
- [ ] Permissões/authorization está definida?
- [ ] Edge cases identificados?

## Critérios de aceitação (preencher quando definidos)
- [ ] ...
- [ ] ...

## Risco estimado
- [ ] low — só tests/ ou docs/
- [ ] medium — app/, resources/js/
- [ ] high — migrations, policies, requests
- [ ] critical — middleware, auth config, harness config

## Notas para o reviewer
- Há áreas a verificar manualmente além do que os gates cobrem?
