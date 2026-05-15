import { useAuth } from '../hooks/useAuth';

export function Profile() {
  const { token } = useAuth();
  return (
    <main>
      <h1>Profile</h1>
      <p>Token: <code>{token}</code></p>
    </main>
  );
}
