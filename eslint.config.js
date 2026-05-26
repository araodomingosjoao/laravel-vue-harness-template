import pluginVue from 'eslint-plugin-vue'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'

export default defineConfigWithVueTs(
    {
        ignores: [
            'node_modules/**',
            'public/build/**',
            'vendor/**',
            'resources/js/types/generated/**',
            'dist/**',
            'coverage/**',
        ],
    },

    pluginVue.configs['flat/recommended'],
    vueTsConfigs.recommended,

    {
        rules: {
            '@typescript-eslint/no-explicit-any': 'error',
            '@typescript-eslint/no-unused-vars': ['error', {
                argsIgnorePattern: '^_',
                varsIgnorePattern: '^_',
            }],
            'vue/multi-word-component-names': 'off',
            'vue/component-api-style': ['error', ['script-setup']],
            'vue/define-emits-declaration': ['error', 'type-based'],
            'vue/define-props-declaration': ['error', 'type-based'],
            'vue/no-undef-components': 'error',
        },
    },
)