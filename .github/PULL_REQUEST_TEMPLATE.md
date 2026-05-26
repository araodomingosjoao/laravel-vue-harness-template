<!--
  Antes de submeter, escolhe o caso aplicável e apaga os outros.
-->

## Tipo de PR

- [ ] Aberto pelo agente (espera-se que os gates passem todos)
- [ ] Aberto por humano (gates podem ter falsos positivos, justificar)
- [ ] Hotfix de produção (justificar urgência)
- [ ] Mudança ao harness (config/harness/, scripts/, .claude/agents/)

## Descrição
O que muda e porquê.

## Issue / spec relacionada
Closes #...

## Checklist do autor

### Sempre
- [ ] Branch criada a partir de `main` actualizada
- [ ] Todos os gates passam localmente (`composer gates && npm run gates`)
- [ ] Não foram adicionadas dependências fora da allow-list

### Se mudaste código
- [ ] Há testes para o caminho feliz
- [ ] Há testes para pelo menos um edge case
- [ ] Não há `any` em TypeScript novo
- [ ] Não há queries N+1 introduzidas
- [ ] Não há validação inline (deve estar em Form Request)

### Se mudaste config sensível
- [ ] ADR escrita para a decisão (em `docs/adr/`)
- [ ] Risco crítico/alto → tem 2+ approvals
- [ ] Não toquei em `.env`, `config/harness/`, ou `vendor/`

### Se mudaste algo no harness
- [ ] Eval set corrido para detectar regressão do agente
- [ ] Chaos test corrido para detectar regressão dos sensores
- [ ] `CHANGELOG.template.md` actualizado (se for melhoria genérica)

## Para o reviewer humano

Os gates já cobrem o trivial. Foca a atenção em:

- [ ] **Intent**: isto resolve o problema descrito na issue?
- [ ] **Apropriação**: a solução é simples? Não há over-engineering?
- [ ] **UX**: se mexe na UI, faz sentido para o utilizador final?
- [ ] **Segurança de domínio**: authorization correcta? Dados sensíveis expostos?
- [ ] **Reversibilidade**: dá para reverter este PR se algo correr mal?
