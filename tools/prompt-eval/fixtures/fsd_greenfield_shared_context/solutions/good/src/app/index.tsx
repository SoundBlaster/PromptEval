import { ThemeProvider, LocaleProvider, AuthProvider } from './providers';
import { SettingsPanel } from '@/widgets/settings-panel';

export function App() {
  return (
    <ThemeProvider>
      <LocaleProvider>
        <AuthProvider>
          <main>
            <h1>App</h1>
            <SettingsPanel />
          </main>
        </AuthProvider>
      </LocaleProvider>
    </ThemeProvider>
  );
}
