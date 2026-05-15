import { useAuth } from '../hooks/useAuth';

export function Settings() {
  const { logout } = useAuth();
  return (
    <main>
      <h1>Settings</h1>
      <button type="button" onClick={logout}>Log out</button>
    </main>
  );
}
