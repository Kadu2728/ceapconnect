import type { Metadata } from "next";
import Link from "next/link";

import { AuthCard } from "@/features/auth/components/auth-card";
import { RegisterForm } from "@/features/auth/components/register-form";
import { Footer } from "@/features/landing/components/footer";
import { Navbar } from "@/features/landing/components/navbar";

export const metadata: Metadata = {
  title: "Criar conta",
};

/**
 * Tela de cadastro (USER_FLOW.md → "Cadastro").
 *
 * Server Component: toda a interatividade (formulário, mutation, máscaras)
 * fica isolada em `RegisterForm`/`AuthCard`, mantendo esta página como
 * composição estática.
 */
export default function CadastroPage() {
  return (
    <div className="flex min-h-svh flex-col">
      <Navbar authLink="login" />

      <main className="relative flex flex-1 items-center justify-center overflow-hidden px-4 py-12 sm:px-6 lg:px-8">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 left-1/2 size-[32rem] -translate-x-1/2 rounded-full bg-brand/10 blur-3xl"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -bottom-32 left-0 size-[28rem] rounded-full bg-brand-purple/10 blur-3xl"
        />
        <div className="relative w-full max-w-md">
          <AuthCard
            title="Comece sua jornada"
            description="Crie sua conta para acompanhar o processo seletivo do CEAP."
            footer={
              <>
                Já tem uma conta?{" "}
                <Link href="/login" className="font-medium text-primary hover:underline">
                  Entrar
                </Link>
              </>
            }
          >
            <RegisterForm />
          </AuthCard>
        </div>
      </main>

      <Footer />
    </div>
  );
}
