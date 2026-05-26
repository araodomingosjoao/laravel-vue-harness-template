---
name: Bug report
about: Algo não funciona como esperado
title: '[BUG] '
labels: bug
assignees: ''
---

## Descrição
Descrição curta e clara do problema.

## Reprodução
Passos para reproduzir:
1. ...
2. ...
3. ...

## Comportamento esperado
O que devia acontecer.

## Comportamento actual
O que está a acontecer.

## Contexto
- Foi o agente que introduziu este bug? sim / não / não sei
- Se sim, o PR do agente passou todos os gates? sim / não
- Há entrada relevante no `LEARNINGS.md`?

## Sinais para o harness
Se este bug devia ter sido apanhado pelos sensores:
- [ ] Adicionar caso ao eval set (em `tests/harness/eval-set/`)
- [ ] Afinar o prompt do AI review (job `code-review` no `agent-pr.yml`)
- [ ] Adicionar entrada ao `LEARNINGS.md`
