export default [
  {
    ignores: [
      "**/static/lib/**",
      "**/staticfiles/**",
    ],
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        document: "readonly",
        window: "readonly",
        IntersectionObserver: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
      },
    },
    linterOptions: {
      reportUnusedDisableDirectives: "error",
    },
    rules: {
      "eqeqeq": "error",
      "no-constant-condition": "error",
      "no-duplicate-imports": "error",
      "no-undef": "error",
      "no-unreachable": "error",
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    },
  },
];
