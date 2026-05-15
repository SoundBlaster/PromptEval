import { useTheme } from '../hooks/useTheme';
import { useLocale } from '../hooks/useLocale';
import { useAuthCtx } from '../contexts/AuthContext';
import { locales, type LocaleCode } from '../utils/i18n';
import { useState } from 'react';

export function SettingsPanel() {
  const { theme, toggleTheme } = useTheme();
  const { locale, setLocale } = useLocale();
  const { token, setToken } = useAuthCtx();
  const [inputToken, setInputToken] = useState('');

  return (
    <section>
      <h2>Settings</h2>
      <div>
        <span>Theme: {theme}</span>
        <button type="button" onClick={toggleTheme}>
          Toggle
        </button>
      </div>
      <div>
        <select
          value={locale}
          onChange={(e) => setLocale(e.target.value as LocaleCode)}
        >
          {locales.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
      </div>
      <div>
        {token ? (
          <button type="button" onClick={() => setToken(null)}>
            Sign out
          </button>
        ) : (
          <>
            <input
              type="text"
              value={inputToken}
              onChange={(e) => setInputToken(e.target.value)}
              placeholder="Token"
            />
            <button type="button" onClick={() => setToken(inputToken)}>
              Sign in
            </button>
          </>
        )}
      </div>
    </section>
  );
}
