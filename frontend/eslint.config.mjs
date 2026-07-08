import nextConfig from "eslint-config-next";
import prettierConfig from "eslint-config-prettier";

/**
 * Next.js 16 exporta `eslint-config-next` como flat config nativo — o shim
 * `FlatCompat` (usado em projetos anteriores ao ESLint 9) não é necessário
 * e quebra a validação de schema com essa versão do plugin React.
 */
const eslintConfig = [
  ...nextConfig,
  prettierConfig,
  {
    files: ["**/*.ts", "**/*.tsx"],
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
    },
  },
  {
    ignores: [".next/**", "node_modules/**"],
  },
];

export default eslintConfig;
