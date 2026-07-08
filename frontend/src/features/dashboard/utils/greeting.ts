/**
 * Saudação textual conforme o horário do dia — pequeno toque de
 * personalização (USER_FLOW.md → Dashboard: "Saudação").
 */
export function getTimeOfDayGreeting(date: Date = new Date()): string {
  const hour = date.getHours();

  if (hour < 12) return "Bom dia";
  if (hour < 18) return "Boa tarde";
  return "Boa noite";
}
