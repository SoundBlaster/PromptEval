import { useAuth } from '@/shared/lib/auth';

export function SignInButton() {
  const { isAuthenticated, signIn, signOut } = useAuth();

  if (isAuthenticated) {
    return <button type="button" onClick={signOut}>Sign out</button>;
  }
  return <button type="button" onClick={() => signIn('demo-token')}>Sign in</button>;
}
