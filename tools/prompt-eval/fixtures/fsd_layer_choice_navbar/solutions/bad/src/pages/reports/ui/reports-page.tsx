import { useCurrentUser, UserBadge } from '@/entities/user';
import { LogoutButton } from '@/features/logout';
import { NotificationsIcon } from '@/features/show-notifications';

function AppHeaderLocal() {
  const user = useCurrentUser();
  return (
    <header>
      <strong>Acme</strong>
      {user && <UserBadge user={user} />}
      <NotificationsIcon />
      <LogoutButton />
    </header>
  );
}

export function ReportsPage() {
  return (
    <div>
      <AppHeaderLocal />
      <main>
        <h1>Reports</h1>
        <p>Tables go here.</p>
      </main>
    </div>
  );
}
