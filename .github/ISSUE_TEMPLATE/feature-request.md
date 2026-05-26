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
Se vais delegar isto ao agente, considera invocar primeiro o sub-agente
`spec-writer` para clarificar:

- [ ] Escopo está claro? (API only? UI only? ambos?)
- [ ] Modelo de dados está definido?
- [ ] Permissões/authorization está definida?
- [ ] Edge cases identificados?

Se algumas destas estão por responder, deixa o spec-writer perguntar antes
de chamar `laravel-backend` ou `vue-frontend`.

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
