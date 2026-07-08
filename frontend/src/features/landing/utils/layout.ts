/**
 * Reexporta o container padrão da aplicação (`@/lib/layout`) sob o nome
 * histórico usado pela feature `landing`, evitando alterar os import sites
 * já validados (Hero, Pillars, Footer, Navbar) por uma mudança puramente
 * organizacional — a área autenticada (Dashboard) usa o mesmo container
 * diretamente via `APP_CONTAINER_CLASS`.
 */
export { APP_CONTAINER_CLASS as LANDING_CONTAINER_CLASS } from "@/lib/layout";
