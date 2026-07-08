/** @type {import("prettier").Config} */
const config = {
  semi: true,
  singleQuote: false,
  trailingComma: "all",
  printWidth: 90,
  tabWidth: 2,
  plugins: ["prettier-plugin-organize-imports"],
};

export default config;
