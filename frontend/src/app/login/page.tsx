import { CheckCircle2 } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";

import { AuthCard } from "@/features/auth/components/auth-card";
import { LoginForm } from "@/features/auth/components/login-form";
import { Footer } from "@/features/landing/components/footer";
import { Navbar } from "@/features/landing/components/navbar";

export const metadata: Metadata = {
  title: "Entrar",
};

interface LoginPageProps {
  searchParams: Promise<{ registered?: string }>;
}

/**
 * Tela de login (USER_FLOW.md → "Primeiro Login").
 *
 * Server Component: lê `?registered=1` diretamente via `searchParams` (Next
 * 15+) para exibir o banner de sucesso pós-cadastro sem precisar de um hook
 * client-side só para isso. A interatividade real (formulário, mutation)
 * fica isolada em `LoginForm`/`AuthCard`.
 */
export default async function LoginPage({ searchParams }: LoginPageProps) {
  const { registered } = await searchParams;
  const justRegistered = registered === "1";

  return (
    <div className="flex min-h-svh flex-col">
      <Navbar authLink="cadastro" />

      <main className="relative flex flex-1 items-center justify-center overflow-hidden px-4 py-12 sm:px-6 lg:px-8">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 left-1/2 size-[32rem] -translate-x-1/2 rounded-full bg-brand/10 blur-3xl"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -bottom-32 right-0 size-[28rem] rounded-full bg-brand-green/10 blur-3xl"
        />
        <div className="relative w-full max-w-md">
          {justRegistered ? (
            <div
              role="status"
              className="mb-6 flex items-start gap-3 rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-sm"
            >
              <CheckCircle2
                className="mt-0.5 size-5 shrink-0 text-success"
                aria-hidden="true"
              />
              <p>
                <span className="font-semibold">Conta criada com sucesso!</span> Faça
                login para continuar sua jornada.
              </p>
            </div>
          ) : null}

          <AuthCard
            title="Bem-vindo de volta"
            description="Entre para continuar acompanhando sua jornada no CEAP."
            footer={
              <>
                Ainda não tem conta?{" "}
                <Link
                  href="/cadastro"
                  className="font-medium text-primary hover:underline"
                >
                  Criar conta
                </Link>
              </>
            }
          >
            <LoginForm />
          </AuthCard>
        </div>
      </main>

      <Footer />
    </div>
  );
}
