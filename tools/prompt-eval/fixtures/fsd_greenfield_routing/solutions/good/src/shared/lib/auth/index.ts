// Auth context lives in shared so that pages and features can consume
// useAuth without crossing into the app/ layer.
import { createContext, useContext } from 'react';

export interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

// The context object is owned by shared/; the AuthProvider in app/ provides it.
export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
