export interface LocaleOption {
  code: 'en' | 'fr';
  label: string;
}

export const LOCALES: LocaleOption[] = [
  { code: 'en', label: 'English' },
  { code: 'fr', label: 'Français' },
];

export const translations = {
  en: {
    settings: 'Settings',
    theme: 'Theme',
    language: 'Language',
    auth: 'Auth',
  },
  fr: {
    settings: 'Paramètres',
    theme: 'Thème',
    language: 'Langue',
    auth: 'Auth',
  },
} as const;
