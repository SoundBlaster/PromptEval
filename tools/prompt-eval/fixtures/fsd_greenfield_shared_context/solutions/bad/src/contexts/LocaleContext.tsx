import { createContext, useContext, useState, type ReactNode } from 'react';

type Locale = 'en' | 'fr';

interface LocaleContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>('en');

  return (
    <LocaleContext.Provider value={{ locale, setLocale }}>
      {children}
    </LocaleContext.Provider>
  );
}

export function useLocaleCtx() {
  const ctx = useContext(LocaleContext);
  if (!ctx) throw new Error('Missing LocaleProvider');
  return ctx;
}
