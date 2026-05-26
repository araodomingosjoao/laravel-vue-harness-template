<script setup lang="ts">
// Componente raiz da aplicação.
// Substitui isto pela tua árvore de componentes / router-view.
// Nota: o placeholder vive aqui (string TS), não dentro de uma mustache do
// template — assim o ficheiro é Vue válido antes e depois do init.sh.
const appName = '{{PROJECT_NAME}}'
</script>

<template>
  <div id="app">
    <h1>{{ appName }}</h1>
    <p>Substitui este componente pela tua aplicação.</p>
  </div>
</template>