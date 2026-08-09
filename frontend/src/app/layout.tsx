import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { AppProviders } from "@/components/providers/app-providers";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "CEAP Connect",
    template: "%s | CEAP Connect",
  },
  description:
    "Plataforma de Candidate Experience gamificada do processo seletivo do CEAP.",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/icons/icon512.png",
    apple: "/icons/icon192.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0e1a1d" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning className="scroll-smooth">
      <head>
        {/* Aplica as preferências de acessibilidade (EPIC 21) antes da
            primeira pintura, evitando o "flash" de texto no tamanho errado
            para quem depende justamente desse ajuste. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var p=JSON.parse(localStorage.getItem("ceap-a11y")||"{}"),d=document.documentElement.dataset;d.a11yReadable=String(!!p.readable);d.a11yText=p.textSize||"default";d.a11yContrast=p.contrast||"default"}catch(e){}`,
          }}
        />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
