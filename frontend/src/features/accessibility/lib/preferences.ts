export type TextSize = "default" | "large" | "xlarge";
export type Contrast = "default" | "high";

export interface AccessibilityPreferences {
  readable: boolean;
  textSize: TextSize;
  contrast: Contrast;
}

export const DEFAULT_PREFERENCES: AccessibilityPreferences = {
  readable: false,
  textSize: "default",
  contrast: "default",
};

export const STORAGE_KEY = "ceap-a11y";

/**
 * Aplica as preferências como atributos `data-*` no `<html>` — o CSS em
 * `globals.css` faz todo o resto. Manter a aplicação aqui (e não em cada
 * componente) é o que permite zero JavaScript por tela.
 */
export function applyPreferences(preferences: AccessibilityPreferences): void {
  const root = document.documentElement;
  root.dataset.a11yReadable = String(preferences.readable);
  root.dataset.a11yText = preferences.textSize;
  root.dataset.a11yContrast = preferences.contrast;
}

export function readStoredPreferences(): AccessibilityPreferences {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_PREFERENCES;
    return {
      ...DEFAULT_PREFERENCES,
      ...(JSON.parse(raw) as Partial<AccessibilityPreferences>),
    };
  } catch {
    return DEFAULT_PREFERENCES;
  }
}
