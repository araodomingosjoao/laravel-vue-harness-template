# Filosofia do template

Este documento explica os princípios por detrás das decisões do template.
Lê isto antes de propor mudanças significativas.

## 1. Foco em Laravel + Vue, não generalização

O template **não** tenta suportar Django, Rails, Next.js ou outras stacks.
Cada generalização adiciona complexidade e dilui a qualidade dos defaults
para a stack principal.

Se precisares de outra stack: faz fork e adapta. Forks divergem; tudo bem.

## 2. Mínimo de configuração

`init.sh` faz 4 perguntas e usa convenções para tudo o resto. Resistimos à
tentação de oferecer 20 opções porque:

- Mais opções = mais combinações para testar = mais bugs
- Os defaults vão estar quase sempre correctos
- Quem quer mais controlo edita os ficheiros à mão depois

## 3. Production-grade por defeito, não "starter"

O template inclui kill switch, budgets, eval set, chaos tests — coisas que
um projecto novo "não precisa ainda". Mas adicionar isto depois é trabalhoso
e quase ninguém o faz. Pré-incluir torna trivial usar; quem não quiser desliga.

## 4. Documentação como código

Tudo o que o template assume está escrito num ficheiro versionado:

- `CLAUDE.md` — convenções
- `policy.yml` — limites
- `dependencies.yml` — allow-list
- `ADRs` — decisões arquitecturais

Nada vive "na cabeça da equipa". Se vive, é um bug.

## 5. O agente é parte do sistema, não um deus

O harness assume que o agente vai cometer erros:

- Vai entrar em loops → trajectory.py detecta
- Vai exceder budget → budget_check.py corta
- Vai querer fazer algo destrutivo → human approval required
- Vai falhar em tasks específicas → eval set detecta

Não tentamos eliminar erros do agente. Tentamos contê-los e tornar visíveis.

## 6. Não há fila zero — todos os defeitos são reais

Cada vez que alguém disser "isto é raro, podemos ignorar", a resposta é não.
Em produção, "raro" acontece todas as semanas. Os edge cases são o trabalho.

## 7. Reversibilidade

Toda mudança importante deve ser revertível:

- `kill_switch` reverte o agente em segundos
- ADRs podem ser superseded por outras ADRs
- O eval set permite detectar regressão e reverter mudanças no `CLAUDE.md`

## 8. Honestidade sobre o custo

Usar IA tem custo monetário. O dashboard expõe isso. Esconder o custo leva a
surpresas no fim do mês. Mostrar leva a decisões informadas.

## Quando propor mudanças ao template

Mudanças bem-vindas:
- ✓ Mais sensores inferenciais (regras na rubrica do AI review)
- ✓ Mais tasks no eval set ou bad-prs
- ✓ Correcções a falsos positivos dos sensores
- ✓ Melhorias ao `init.sh`
- ✓ Sub-agentes especializados em áreas específicas (ex: migrations complexas, auth)
- ✓ Templates para issues e PRs

Mudanças que requerem discussão profunda:
- ⚠ Mudar a stack ou versões base
- ⚠ Adicionar dependências runtime ao template
- ⚠ Mudar estrutura de directorias (afecta upgrade path)
- ⚠ Remover ou renomear scripts existentes

Mudanças que não pertencem aqui:
- ✗ Suporte a outras frameworks (faz fork)
- ✗ Features específicas de um projecto teu (vão no teu projecto, não no template)
- ✗ Defaults baseados em preferência pessoal sem dados
