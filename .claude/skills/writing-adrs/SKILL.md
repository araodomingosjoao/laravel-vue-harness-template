---
name: writing-adrs
description: Decidir se uma decisão é arquiteturalmente significativa e, se for, redigir um ADR no formato do projecto (docs/adr/). Usa quando uma task envolve uma escolha de design não-trivial.
---

# Writing ADRs (senior)

## Primeiro: isto merece um ADR?

Um ADR regista uma **decisão arquiteturalmente significativa** — não toda a escolha.

**Merece ADR:**
- Difícil de reverter (escolha de DB, auth, estrutura de módulos, contrato de API público).
- Cross-cutting (afeta vários módulos/equipas).
- Trade-off não-óbvio que alguém vai questionar daqui a 6 meses.
- Desvio de uma convenção do `CLAUDE.md`.

**NÃO merece** (não inventes ruído):
- Decisões já cobertas pelo `CLAUDE.md` ou óbvias dado o contexto.
- Detalhes de implementação reversíveis (nome de variável, qual helper).
- Coisas que o git/CHANGELOG já registam.

> Regra: se for fácil de mudar e ninguém vai questionar, não é ADR.

## Formato (`docs/adr/NNNN-titulo-curto.md`)

```markdown
# NNNN. <título da decisão>

- Status: proposed | accepted | superseded by ADR-XXXX
- Date: YYYY-MM-DD

## Context
O problema e as forças em jogo. Porque é que há uma decisão a tomar.

## Decision
O que decidimos, no activo: "Vamos usar X."

## Consequences
O que melhora, o que piora, o que passa a ser mais difícil. Trade-offs honestos.

## Alternatives considered
Opções rejeitadas e porquê (1 linha cada).
```

## Numeração

Próximo número sequencial em `docs/adr/`. Não reutilizes nem saltes. Em modo
assíncrono, propõe o ADR com `Status: proposed` para o humano aceitar.