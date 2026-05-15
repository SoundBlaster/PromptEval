export const locales = [
  { code: 'en', label: 'English' },
  { code: 'fr', label: 'Français' },
] as const;

export type LocaleCode = (typeof locales)[number]['code'];
