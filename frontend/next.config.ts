import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Gera um build "standalone" (server.js autocontido + apenas as
  // dependências de produção efetivamente usadas) — necessário para a
  // imagem Docker final ficar enxuta. Ver frontend/Dockerfile.
  output: "standalone",
  // Fixa explicitamente a raiz do workspace do Turbopack como `frontend/`.
  // Sem isso, o Next.js infere a raiz a partir do `package.json`/lockfile
  // mais externo que encontrar (o do monorepo, usado apenas para orquestrar
  // husky/lint-staged), o que gera um warning e pode levar a resolução
  // incorreta de módulos/tracing de arquivos.
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;
