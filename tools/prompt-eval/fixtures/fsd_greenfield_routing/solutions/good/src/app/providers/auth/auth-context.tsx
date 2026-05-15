import { useState, type ReactNode } from 'react';
import { AuthContext } from '@/shared/lib/auth';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(
    () => sessionStorage.getItem('auth-token'),
  );

  function login(newToken: string) {
    sessionStorage.setItem('auth-token', newToken);
    setToken(newToken);
  }

  function logout() {
    sessionStorage.removeItem('auth-token');
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: token !== null, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
