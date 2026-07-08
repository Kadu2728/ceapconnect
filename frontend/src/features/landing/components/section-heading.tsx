import { Reveal } from "@/components/motion/reveal";
import { cn } from "@/lib/utils";

interface SectionHeadingProps {
  eyebrow: string;
  title: string;
  description?: string;
  align?: "center" | "left";
  className?: string;
}

/**
 * Cabeçalho padrão das seções da Landing Page (eyebrow + título + descrição).
 *
 * Garante ritmo tipográfico e espaçamento consistentes entre todas as seções,
 * evitando divergência visual à medida que a página cresce.
 */
export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "center",
  className,
}: SectionHeadingProps) {
  return (
    <Reveal
      className={cn(
        "flex flex-col gap-3",
        align === "center" ? "mx-auto max-w-2xl text-center" : "max-w-2xl",
        className,
      )}
    >
      <span className="text-sm font-semibold tracking-wide text-brand uppercase">
        {eyebrow}
      </span>
      <h2 className="text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
        {title}
      </h2>
      {description ? (
        <p className="text-pretty text-muted-foreground sm:text-lg">{description}</p>
      ) : null}
    </Reveal>
  );
}
