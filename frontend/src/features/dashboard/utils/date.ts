const FULL_DATE_FORMATTER = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "long",
  year: "numeric",
});

const EVENT_DATE_FORMATTER = new Intl.DateTimeFormat("pt-BR", {
  weekday: "short",
  day: "2-digit",
  month: "short",
});

const EVENT_TIME_FORMATTER = new Intl.DateTimeFormat("pt-BR", {
  hour: "2-digit",
  minute: "2-digit",
});

const MS_PER_DAY = 24 * 60 * 60 * 1000;

/**
 * Interpreta uma data ISO (`"2026-12-01"` ou `"2026-12-01T14:00:00Z"`) como
 * horário local, evitando o "bug de um dia a menos": `new Date("2026-12-01")`
 * é interpretado pelo JS como meia-noite UTC, o que desloca um dia para trás
 * em fusos horários negativos (ex.: Brasil).
 */
function parseIsoDate(iso: string): Date | null {
  const dateOnlyMatch = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);

  if (dateOnlyMatch) {
    const [, year, month, day] = dateOnlyMatch;
    return new Date(Number(year), Number(month) - 1, Number(day));
  }

  const parsed = new Date(iso);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

/** Formata uma data ISO como "1 de dezembro de 2026". */
export function formatFullDate(iso: string): string {
  const date = parseIsoDate(iso);
  return date ? FULL_DATE_FORMATTER.format(date) : "Data indisponível";
}

/** Formata a data (e horário, quando presente) de um evento em pt-BR. */
export function formatEventDate(iso: string): string {
  const date = parseIsoDate(iso);
  if (!date) return "Data indisponível";

  const hasTime = /T\d{2}:\d{2}/.test(iso);
  const datePart = EVENT_DATE_FORMATTER.format(date);

  return hasTime ? `${datePart} · ${EVENT_TIME_FORMATTER.format(date)}` : datePart;
}

/**
 * Diferença em dias de calendário (não em blocos de 24h) entre hoje e a data
 * alvo. Retorna `null` quando `iso` não é uma data válida.
 */
export function getDaysUntil(iso: string, from: Date = new Date()): number | null {
  const target = parseIsoDate(iso);
  if (!target) return null;

  const startOfFrom = new Date(from.getFullYear(), from.getMonth(), from.getDate());
  const startOfTarget = new Date(
    target.getFullYear(),
    target.getMonth(),
    target.getDate(),
  );

  return Math.round((startOfTarget.getTime() - startOfFrom.getTime()) / MS_PER_DAY);
}
