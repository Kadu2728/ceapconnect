import type { MetadataRoute } from "next";

/**
 * Manifesto do PWA (EPIC 18) — o que torna o CEAP Connect instalável na tela
 * inicial do celular/desktop. Gerado como rota (`/manifest.webmanifest`),
 * convenção nativa do Next.js App Router.
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "CEAP Connect",
    short_name: "CEAP Connect",
    description:
      "Acompanhe sua jornada no processo seletivo do CEAP — missões, conquistas e a prova, tudo em um só lugar.",
    start_url: "/dashboard",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#0066ae",
    orientation: "portrait-primary",
    icons: [
      { src: "/icons/icon192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icons/icon512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      {
        src: "/icons/maskable512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
