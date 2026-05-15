import { useState, type ReactNode } from 'react';
import { AuthContext } from '@/shared/lib/auth';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  function signIn(newToken: string) {
    setToken(newToken);
  }

  function signOut() {
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: token !== null, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
