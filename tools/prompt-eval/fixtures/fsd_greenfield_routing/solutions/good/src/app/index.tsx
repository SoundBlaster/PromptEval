import { AuthProvider } from './providers/auth';
import { AppRouter } from './providers/router';

export function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}
