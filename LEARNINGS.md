# LEARNINGS — memória volátil do agente

> Este ficheiro é a **memória curta** do agente entre sessões.
> Veja `examples/learnings/sample.md` para exemplos de entradas.

## Como funciona

- **O agente lê este ficheiro no início de cada sessão**, depois do CLAUDE.md
- Quando o developer corrige uma incompreensão repetida, anota aqui
- Entradas com mais de 90 dias são revistas — ou viram convenção (movem para CLAUDE.md / ADR), ou são removidas
- **Não é commit-friendly por design**: pode ter contradições temporárias, hipóteses, notas

## Formato

```
### [YYYY-MM-DD] Título curto
**Contexto**: O que aconteceu (qual o bug, qual a confusão)
**Aprendizagem**: A regra a aplicar
**Validade**: Até quando isto é relevante (data ou condição)
```

---

## Entradas activas

<!-- Adiciona aqui as primeiras aprendizagens à medida que trabalhas com o agente. -->

*(nenhuma entrada ainda)*

---

## Quando promover para CLAUDE.md ou ADR

- **Vira convenção estável** → move para CLAUDE.md
- **É uma decisão arquitectural com trade-offs** → cria um ADR em `docs/adr/`
- **Já não se aplica** → remove (o git log preserva histórico)
