---
name: pest-testing
description: Padrões sénior de testes Pest para APIs Laravel — o que testar, como estruturar, datasets, autorização, edge cases, e o que NÃO testar. Usa ao escrever ou rever testes de backend.
---

# Pest testing (senior patterns)

## Princípios

- **Arrange → Act → Assert**, um foco por teste. O nome diz o comportamento:
  `it('forbids completing another users todo')`.
- **Feature tests** para endpoints (preferidos); **Unit** só para classes puras sem DB.
- Testa **comportamento e contrato**, não a implementação. Não testes que o Eloquent
  guarda na DB — testa o que o endpoint devolve.
- Não testes o framework: não testes que `required` valida; testa que o *teu* endpoint
  responde 422 quando falta o campo.

## O que cobrir em cada endpoint

- **Happy path** — o caso normal, assertando a forma do JSON (`assertJsonPath`).
- **Autorização** — um user sem permissão recebe 403 (via Policy).
- **Validação** — input inválido → 422 + os campos com erro.
- **Edge cases** — lista vazia, limites de paginação, valores null, recurso inexistente → 404.

## Ferramentas

- `actingAs($user)` para autenticar; `User::factory()` + estados.
- `assertJsonPath('data.x', ...)`, `assertJsonCount`, `assertOk/Created/Forbidden/UnprocessableEntity`.
- **Datasets** para varrer múltiplos inputs com um só teste.
- `RefreshDatabase` (já no TestCase base). Não dependas de ordem entre testes.
- Tempo → `travelTo()`; aleatoriedade → fixa o seed.

## Cheiros a evitar

- Testes que passam sempre (sem assert do que importa).
- Mock de tudo — testa o caminho real; mock só o I/O externo.
- Um teste gigante a testar 5 coisas — parte-o.
- Asserts frágeis em strings inteiras quando só importa um campo.
