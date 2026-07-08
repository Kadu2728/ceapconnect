import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Configuração do lint-staged para o backend (ver docs/monorepo da lib:
 * https://github.com/lint-staged/lint-staged#how-to-use-lint-staged-in-a-multi-package-monorepo).
 * Por estar em `backend/`, o lint-staged usa este diretório como cwd das
 * tasks abaixo e só a aplica a arquivos staged dentro de `backend/`.
 */
const backendDir = path.dirname(fileURLToPath(import.meta.url));

/**
 * Resolve o executável do ruff priorizando o virtualenv local do backend
 * (`backend/.venv`), para o hook funcionar sem depender de uma instalação
 * global no PATH do desenvolvedor. Cai para o binário global `ruff` caso o
 * venv não exista (ex.: CI, ou um venv com outro nome/local).
 */
function resolveRuff() {
  const windowsVenvRuff = path.join(backendDir, ".venv", "Scripts", "ruff.exe");
  const posixVenvRuff = path.join(backendDir, ".venv", "bin", "ruff");

  if (existsSync(windowsVenvRuff)) return `"${windowsVenvRuff}"`;
  if (existsSync(posixVenvRuff)) return `"${posixVenvRuff}"`;

  return "ruff";
}

const ruff = resolveRuff();

export default {
  "*.py": [`${ruff} check`, `${ruff} format --check`],
};
