---
name: code-review-rubric
description: Rubrica sénior para rever um diff — correção, convenções, segurança, performance, testes — sem deixar passar o que importa nem inventar ruído. Usa ao rever código antes de um PR ou merge.
---

# Code review rubric (senior)

Revê o **diff**, não o repo todo. O `CLAUDE.md` é a régua das convenções. Sinaliza só
o que muda a decisão de merge; distingue **🔴 bloqueante** de **🟡 sugestão**.

## 1. Correção
- Faz o que a spec/task pede? Edge cases tratados (null, vazio, limites)?
- Erros tratados, não engolidos. Sem código morto ou TODO esquecido.

## 2. Convenções (CLAUDE.md)
- Backend: Form Request (não validação inline), Resource (não model cru), `$fillable`,
  Policy para authz, controller magro, paginação.
- Sem desativar regras de PHPStan/ESLint para "passar".

## 3. Segurança (bloqueante)
- **Authorization**: toda a ação sensível passa por Policy. Sem IDOR (aceder a recurso de
  outro user via id).
- **Mass assignment**: `$fillable` explícito; sem `$guarded = []`.
- **Injeção**: query builder/bindings, nunca SQL/HTML concatenado. Input validado.
- **Segredos**: nada de chaves/tokens no código; sem dados sensíveis em logs.

## 4. Performance
- N+1 (ver `eloquent-performance`), paginação em listagens, sem queries em loops.

## 5. Testes
- Há testes e cobrem o comportamento novo (happy + authz + validação + edge), não só o
  happy path.

## Como devolver a review
- Agrupa por ficheiro, severidade clara (🔴 bloqueante / 🟡 sugestão).
- Aponta o *porquê* e o fix concreto, não só "isto está mal".
- Em **inglês** (o feedback do harness é em inglês).
