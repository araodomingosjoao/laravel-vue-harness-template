# Examples — exemplos do template

Esta pasta existe **apenas no template**. Quando inicializas um projecto novo,
o `scripts/init.sh` apaga esta pasta inteira.

Os ficheiros aqui são exemplos extraídos do projecto original "todo list" que
serviu de cobaia para construir este harness. Servem como referência para
quando o developer (ou agente) precisar de criar:

- Um eval task novo → ver `eval-tasks/add-priority-field/`
- Um eval adversarial → ver `eval-tasks/hardcode-api-key/`
- Um bad-PR para chaos testing → ver `bad-prs/n-plus-one.diff`
- Uma ADR nova → ver `adrs/001-completed-at-timestamp.md`
- Uma entrada de LEARNINGS → ver `learnings/sample.md`

## Como usar durante o desenvolvimento

```bash
# Copiar um exemplo de eval task como ponto de partida
cp -r examples/eval-tasks/add-priority-field tests/harness/eval-set/tasks/my-new-eval
# Editar o conteúdo para o teu caso

# Copiar um exemplo de bad-PR
cp examples/bad-prs/n-plus-one.diff tests/harness/bad-prs/
cp examples/bad-prs/n-plus-one.expected.yml tests/harness/bad-prs/
# Editar para o teu caso
```

## Quando apagar esta pasta

Se inicializaste um projecto a partir deste template e já tens os teus próprios
exemplos no eval set e bad-prs, podes apagar esta pasta:

```bash
rm -rf examples/
```

Mas não há urgência — está fora do path de qualquer ferramenta de produção.
