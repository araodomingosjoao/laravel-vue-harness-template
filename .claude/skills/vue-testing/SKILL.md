---
name: vue-testing
description: Padrões sénior de testes Vitest + Vue Test Utils — testar comportamento e contrato (props, eventos, render), mockar o I/O, cobrir estados. Usa ao escrever ou rever testes de frontend.
---

# Vue testing (Vitest + VTU, senior)

## Princípios
- **Arrange → Act → Assert**, um foco por teste. Testa **comportamento e contrato**,
  não a implementação interna.
- `mount` para testar o componente como o user o vê; `shallowMount` se isolas de filhos pesados.
- Testa o que o componente **promete**: emite o evento certo, rende o estado certo dado
  props, reage a mudanças.

## O que cobrir
- **Eventos**: `wrapper.emitted('toggle')` com o payload certo após a interação.
- **Render condicional**: classe/estado muda com a prop (ex.: `--done` quando `completed_at`).
- **Estados**: loading, vazio, erro — não só o happy path.

## Ferramentas
- `await wrapper.find('...').trigger('click')` / `.setValue(...)`; espera o `nextTick`.
- `flushPromises()` para resolver fetch assíncrono.
- **Mock o I/O** (`useApi`/rede), não o componente todo. Testa o caminho real do resto.

## Não faças
- Não testes o Vue (não testes que um `computed` recomputa) — testa o teu componente.
- Não asserts em HTML inteiro; assert no que importa (texto, classe, atributo).
- Não dependas de timers reais; usa fake timers se precisas.