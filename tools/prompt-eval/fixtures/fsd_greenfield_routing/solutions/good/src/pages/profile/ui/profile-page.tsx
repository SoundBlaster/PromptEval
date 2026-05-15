import { useAuth } from '@/shared/lib/auth';

export function ProfilePage() {
  const { token } = useAuth();

  return (
    <main>
      <h1>Profile</h1>
      <p>Logged in with token: <code>{token}</code></p>
    </main>
  );
}
