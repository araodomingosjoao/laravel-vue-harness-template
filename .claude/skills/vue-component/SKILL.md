---
name: vue-component
description: Padrões sénior para componentes Vue 3 — script setup + TS, props/emits tipados, tamanho, acessibilidade, e quando extrair um composable. Usa ao criar ou rever componentes.
---

# Vue component (senior)

## Forma
- **`<script setup lang="ts">`** sempre. Nunca Options API.
- `defineProps<{...}>()` e `defineEmits<{...}>()` **com tipos TS**, não validação runtime.
- Props down, events up. **Nunca mutes uma prop** — emite um evento e deixa o pai mudar.
- Estado derivado em `computed`, não em métodos nem em data duplicada.

## Tamanho e responsabilidade
- Componente > ~150 linhas → parte em sub-componentes ou extrai um **composable**.
- Lógica de negócio/fetch **não** vive no componente → composable (`use*`) ou store.
- Fetch via `useApi()` (trata CSRF + erros), nunca `fetch()` direto.

## Qualidade
- **Sem `any`** — usa `unknown` + narrowing. Espelha o tipo do backend: se o backend
  devolve `completed_at: string | null`, o tipo é isso, não `boolean`.
- `v-for` sempre com `:key` estável; não juntes `v-if` e `v-for` no mesmo elemento.
- **Acessibilidade**: HTML semântico, `aria-label` em controlos sem texto, labels associadas.
- Estilos `scoped`; classes no estilo do projecto (ex.: BEM `block__element--modifier`).

## Não faças
- Não acedas ao DOM diretamente se um `ref`/binding resolve.
- Não metas um `watch` para o que um `computed` faz melhor.
