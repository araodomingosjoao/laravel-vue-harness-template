# Exemplos de entradas LEARNINGS.md

Estas são entradas de exemplo, retiradas do projecto original. Servem para
mostrar o **formato e o tom** de uma boa entrada de LEARNINGS — não para
serem copiadas para um projecto novo.

---

### [YYYY-MM-DD] StripeService tem retry interno
**Contexto**: Agente adicionou retry loop à volta de calls ao StripeService, criando double-retry.
**Aprendizagem**: `StripeService` (em `app/Services/StripeService.php`) já tem retry com backoff exponencial via Saloon connector. Não envolver em retry adicional.
**Validade**: Até refactor do StripeService (issue #234).

### [YYYY-MM-DD] User factory cria utilizadores não-verificados por defeito
**Contexto**: Testes falhavam porque o middleware `verified` rejeitava factory users.
**Aprendizagem**: Usar `User::factory()->verified()->create()` em testes que passem por rotas com middleware `verified`. Há um state `unverified` para o caminho contrário.
**Validade**: Estável.

---

## O que torna uma boa entrada

- **Específica**: refere ficheiro/função/classe concreta
- **Accionável**: o agente sabe exactamente o que fazer/evitar
- **Tem validade**: data ou condição para revisão (evita acumular cruft)
- **Curta**: 3-5 linhas, não um ensaio

## O que NÃO pertence aqui

- Convenções estáveis → vão para `CLAUDE.md`
- Decisões arquitecturais com trade-offs → vão para `docs/adr/`
- Bugs corrigidos → vão para git log, não aqui
- TODOs do developer → vão para o issue tracker
