import { useLocale, type Locale } from '@/shared/lib/locale';

const LOCALES: Locale[] = ['en', 'fr'];

export function LocaleSwitcher() {
  const { locale, setLocale } = useLocale();

  return (
    <select value={locale} onChange={(e) => setLocale(e.target.value as Locale)}>
      {LOCALES.map((l) => (
        <option key={l} value={l}>{l.toUpperCase()}</option>
      ))}
    </select>
  );
}
