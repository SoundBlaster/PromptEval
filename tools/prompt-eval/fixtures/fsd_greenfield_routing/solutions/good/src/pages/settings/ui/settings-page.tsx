import { useAuth } from '@/shared/lib/auth';

export function SettingsPage() {
  const { logout } = useAuth();

  return (
    <main>
      <h1>Settings</h1>
      <button onClick={logout}>Log out</button>
    </main>
  );
}
