# ADR-000: Template para Architecture Decision Records

**Status**: template
**Data**: YYYY-MM-DD
**Decisores**: nome(s)

## Contexto

Que problema estamos a resolver? Que constraints existem?
Que opções considerámos?

## Decisão

O que decidimos. Numa frase clara.

## Consequências

### Positivas
- ...

### Negativas / trade-offs aceites
- ...

### Áreas afectadas
Que partes do código encarnam esta decisão? O agente deve ler este ADR
quando tocar nestes ficheiros.

- `app/...`
- `resources/js/...`

## Como o agente usa isto

ADRs são contexto **obrigatório** para tasks que tocam nas áreas afectadas.
Diferente do LEARNINGS.md (volátil), os ADRs são decisões arquitecturais
de longo prazo que justificam *porquê* o código está como está.

Se uma task parece exigir violar uma ADR, o agente deve:
1. Parar
2. Apontar a contradição ao developer
3. Sugerir: ou refinamos a task, ou actualizamos a ADR (com novo registo)

## Revisão

ADRs não se editam — superseded-se. Se esta decisão muda, cria-se uma nova ADR
e marca-se esta como `superseded by ADR-NNN`.
