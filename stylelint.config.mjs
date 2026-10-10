export default {
  ignores: [
    "core/static/lib/**",
    "**/staticfiles/**",
  ],
  plugins: ["stylelint-order"],
  rules: {
    "block-no-empty": true,
    "color-no-invalid-hex": true,
    "declaration-block-no-duplicate-properties": true,
    "order/properties-alphabetical-order": true,
  },
};
