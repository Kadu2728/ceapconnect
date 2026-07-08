import { AdmissionSection } from "@/features/landing/components/admission-section";
import { CoursesSection } from "@/features/landing/components/courses-section";
import { FinalCta } from "@/features/landing/components/final-cta";
import { Footer } from "@/features/landing/components/footer";
import { Hero } from "@/features/landing/components/hero";
import { JourneySection } from "@/features/landing/components/journey-section";
import { Navbar } from "@/features/landing/components/navbar";
import { Pillars } from "@/features/landing/components/pillars";
import { StatsBand } from "@/features/landing/components/stats-band";

/**
 * Landing Page do CEAP Connect.
 *
 * Server Component puro: compõe as seções da feature `landing` em ordem
 * narrativa (proposta → prova social → pilares → jornada → cursos → ingresso →
 * chamada final). Interatividade e animação ficam isoladas nas seções client.
 */
export default function Home() {
  return (
    <div className="flex min-h-svh flex-col">
      <Navbar showSectionNav />
      <main className="flex-1">
        <Hero />
        <StatsBand />
        <Pillars />
        <JourneySection />
        <CoursesSection />
        <AdmissionSection />
        <FinalCta />
      </main>
      <Footer />
    </div>
  );
}
