import type { Metadata } from "next";

import { GuardianPortalContent } from "@/features/guardian-portal/components/guardian-portal-content";
import { Footer } from "@/features/landing/components/footer";
import { Navbar } from "@/features/landing/components/navbar";

export const metadata: Metadata = {
  title: "Confirmação do responsável",
};

interface GuardianPortalPageProps {
  params: Promise<{ token: string }>;
}

/**
 * Portal do Responsável (item 5 do backlog) — página pública, sem
 * `AuthenticatedShell`/login: o responsável não tem conta, a posse do
 * `token` na URL (link mágico enviado por e-mail/WhatsApp pelo candidato)
 * é a única autorização.
 */
export default async function GuardianPortalPage({ params }: GuardianPortalPageProps) {
  const { token } = await params;

  return (
    <div className="flex min-h-svh flex-col">
      <Navbar authLink="login" />

      <main className="relative flex flex-1 items-center justify-center overflow-hidden px-4 py-12 sm:px-6 lg:px-8">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 left-1/2 size-[32rem] -translate-x-1/2 rounded-full bg-brand/10 blur-3xl"
        />
        <div className="relative w-full max-w-md">
          <GuardianPortalContent token={token} />
        </div>
      </main>

      <Footer />
    </div>
  );
}
