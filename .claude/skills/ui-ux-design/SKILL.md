---
name: ui-ux-design
description: Fundamentos sénior de UX que a frontend-design (estética) não cobre — os 4 estados (loading/empty/error/success), acessibilidade (WCAG), UX de formulários, feedback e consistência. Usa ao construir ou rever qualquer UI, a par da frontend-design.
---

# UI/UX fundamentals (senior)

A skill `frontend-design` (oficial Anthropic) trata da **estética** — tipografia, cor,
layout, motion. Esta trata dos **fundamentos de UX** que fazem uma UI *funcionar bem e
ser acessível*. A régua do projecto (tokens, componentes existentes) ganha sempre —
**não inventes um sistema novo**.

## Os 4 estados de TODA a vista (o erro nº1)
Para cada ecrã/lista/dado vindo de I/O, trata os **quatro**, não só o sucesso:
- **Loading** — skeleton (preferível a spinner para conteúdo; evita layout shift).
- **Empty** — mensagem humana + próxima ação ("Ainda não tens todos. Cria o primeiro.").
- **Error** — o que falhou + como recuperar (botão retry); nunca um ecrã em branco.
- **Success/data** — o caso normal.

## Feedback (nunca silencioso)
- Ação assíncrona → estado pending: desativa o botão, mostra que está a acontecer.
- Confirma o resultado (inline ou toast). Erro de submit → mostra o porquê, **não limpes o form**.
- Optimistic UI quando a ação é segura e reversível; reverte com aviso se falhar.

## Acessibilidade (WCAG AA — não é opcional)
- HTML **semântico** (`<button>`, `<nav>`, `<label>`) antes de `div` com handlers.
- Operável por **teclado**; foco visível (não removas o outline sem alternativa).
- Contraste de texto ≥ 4.5:1. Não comuniques só por cor (junta ícone/texto).
- `aria-label`/`aria-*` em controlos sem texto; gere o foco ao abrir modal / mudar de rota.
- Touch targets ≥ ~44px.

## UX de formulários
- Label sempre (não só placeholder). Helper text curto onde ajuda.
- Validação inline, erro **junto ao campo**, linguagem humana. Valida no blur/submit, não a cada tecla.
- Desativa o submit enquanto pende; defaults sensatos; autofocus no 1º campo relevante.

## Consistência e microcopy
- Reutiliza componentes/tokens existentes. Espaçamento numa escala consistente (sem números mágicos).
- Botões com verbos claros ("Guardar alterações", não "Submeter"/"OK").
- Hierarquia visual por tamanho/peso/espaço, não por excesso de cor.

## Responsivo
- Mobile-first; layout fluido. Sem larguras fixas que rebentam. Testa em ecrã pequeno.
- Respeita `prefers-reduced-motion` — movimento só com propósito.
