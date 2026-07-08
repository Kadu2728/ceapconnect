import { getTimeOfDayGreeting } from "@/features/dashboard/utils/greeting";

interface GreetingProps {
  name: string;
}

/**
 * Saudação principal do Dashboard — a primeira coisa que o candidato lê,
 * respondendo de imediato "quem sou eu aqui" (USER_FLOW.md → Dashboard).
 */
export function Greeting({ name }: GreetingProps) {
  return (
    <div>
      <p className="text-sm font-medium text-muted-foreground">
        {getTimeOfDayGreeting()},
      </p>
      <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{name}</h1>
    </div>
  );
}
