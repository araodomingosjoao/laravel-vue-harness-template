# Rubrica para AI judge — add-priority-field

És um reviewer sénior. Avalia o PR contra esta rubrica.
Para cada critério, dá score 0.0 a 1.0. Score final é a média ponderada.

## Critérios (peso entre parênteses)

### Correctness (peso 3)
- O campo priority é persistido correctamente?
- O filtro por priority funciona end-to-end?
- O default medium é aplicado em todos os caminhos (DB, model, UI)?

### Convenções do projecto (peso 2)
- Segue o CLAUDE.md? (Form Request, Resource, fillable, etc.)
- Estilo PSR-12 e Composition API respeitados?
- Naming consistente com o resto do código?

### Testes (peso 2)
- Cobre happy path?
- Cobre validação (input inválido)?
- Cobre o filtro?
- Testes são legíveis e seguem o padrão Pest existente?

### Frontend (peso 2)
- Badge tem cores distintas para cada prioridade?
- Acessibilidade: cor não é o único indicador (há label/aria)?
- Dropdown está integrado no formulário existente, não substitui-o?

### Simplicidade (peso 1)
- A solução é minimal? (sem over-engineering)
- Não inventou abstracções desnecessárias (enum class, value object, etc.)?
- Não tocou em ficheiros não relacionados?

## Resposta esperada (JSON)

```json
{
  "scores": {
    "correctness": 0.0-1.0,
    "conventions": 0.0-1.0,
    "tests": 0.0-1.0,
    "frontend": 0.0-1.0,
    "simplicity": 0.0-1.0
  },
  "weighted_score": 0.0-1.0,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "would_approve": true|false
}
```
