const { FlatCompat } = require('@eslint/eslintrc')

const compat = new FlatCompat()

module.exports = compat.config({
  env: {
    browser: true,
    es2021: true,
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: ['vue', '@typescript-eslint'],
  rules: {
    'vue/multi-word-component-names': 'off',
    'vue/no-mutating-props': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/ban-ts-comment': 'off',
  },
}, [
  'eslint:recommended',
  'plugin:vue/vue3-recommended',
  'plugin:@typescript-eslint/recommended',
])

