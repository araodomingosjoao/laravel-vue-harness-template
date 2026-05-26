# Bad PRs — chaos engineering do sensor inferencial

Esta directoria contém diffs propositadamente problemáticos para testar
que o `ai_review.py` apanha o que deve apanhar.

Se o AI review aprovar algum destes, a rubrica está fraca e precisa de ser refinada.

## Como funciona

Cada bad-pr tem dois ficheiros:

```
bad-prs/
├── n-plus-one.diff           # o diff que devia ser rejeitado
├── n-plus-one.expected.yml   # que regra(s) deviam disparar
```

## Catálogo actual

| Bad PR | Problema | Regra(s) que devem disparar |
|---|---|---|
| `n-plus-one.diff` | Query Eloquent dentro de foreach | Backend rule 1 |
| `missing-fillable.diff` | Model novo sem `$fillable` | Backend rule 2 |
| `inline-validation.diff` | `$request->validate()` no controller | Backend rule 3 |
| `unpaginated-listing.diff` | `Todo::all()` num endpoint público | Backend rule 4 |
| `eloquent-leak.diff` | Controller devolve `Model` sem Resource | Backend rule 5 |
| `policy-bypass.diff` | `if (auth()->id() === $todo->user_id)` ad-hoc | Backend rule 6 |
| `fat-controller.diff` | 80 linhas de lógica num controller | Backend rule 7 |
| `typescript-any.diff` | Múltiplos `any` em TS sem justificação | Frontend rule 8 |
| `options-api.diff` | Componente novo em Options API | Frontend rule 9 |
| `fetch-in-component.diff` | `fetch()` directo num componente Vue | Frontend rule 11 |
| `inaccessible-input.diff` | `<input>` sem label nem aria-label | Frontend rule 12 |

## Correr

```bash
python scripts/chaos_test.py
```

Output esperado: 11/11 bad-prs rejeitados. Qualquer um aprovado é um bug
no sensor inferencial — refinar a rubrica em `ai_review.py`.

## Quando adicionar um novo bad-pr

Sempre que um bug real escapou ao AI review em produção:
1. Reduz o diff ao mínimo que exibe o problema
2. Adiciona aqui com expected.yml
3. Refina a rubrica até apanhar
4. Verifica que os outros bad-prs continuam a ser apanhados (regression)
