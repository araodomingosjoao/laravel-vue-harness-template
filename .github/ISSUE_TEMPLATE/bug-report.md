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
- [ ] Adicionar bad-PR ao chaos test (em `tests/harness/bad-prs/`)
- [ ] Refinar rubrica do AI review (em `.github/scripts/ai_review.py`)
- [ ] Adicionar entrada ao `LEARNINGS.md`
