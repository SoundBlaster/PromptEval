import { ThemeProvider } from './contexts/ThemeContext';
import { LocaleProvider } from './contexts/LocaleContext';
import { AuthProvider } from './contexts/AuthContext';
import { SettingsPanel } from './components/SettingsPanel';

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
