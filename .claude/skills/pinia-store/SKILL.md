---
name: pinia-store
description: Padrões sénior para stores Pinia (setup syntax) — estado tipado, getters, actions, fetch via useApi, e o que NÃO pôr numa store. Usa ao criar ou rever stores.
---

# Pinia store (senior)

## Setup syntax (obrigatório)

```ts
export const useThingsStore = defineStore('things', () => {
  const items = ref<Thing[]>([])                                   // estado: ref tipado
  const loading = ref(false)
  const pending = computed(() => items.value.filter(t => !t.done)) // derivado: computed
  async function fetchAll() { /* action */ }
  return { items, loading, pending, fetchAll }                     // só o que é público
})
```

## Regras
- Estado em `ref` **tipado** (`ref<Thing[]>([])`), derivado em `computed`, ações em funções.
- **Devolve só o que é público.** O interno fica fora do return.
- Fetch via `useApi()` (composable), nunca `fetch()` direto. Trata `loading`/erro.
- Sufixo `Store` no ficheiro (`thingsStore.ts`), exporta `useThingsStore`.

## O que NÃO pôr na store
- Estado que só interessa a um componente (fica `ref` local no componente).
- Lógica de UI/apresentação. A store é dados + operações sobre dados.
- Não dupliques o servidor inteiro em memória "só porque sim" — guarda o que a UI usa.