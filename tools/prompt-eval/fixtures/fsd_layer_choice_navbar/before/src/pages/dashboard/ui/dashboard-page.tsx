import { useCurrentUser, UserBadge } from '@/entities/user';
import { LogoutButton } from '@/features/logout';
import { NotificationsIcon } from '@/features/show-notifications';

export function DashboardPage() {
  const user = useCurrentUser();
  return (
    <div>
      <header>
        <strong>Acme</strong>
        {user && <UserBadge user={user} />}
        <NotificationsIcon />
        <LogoutButton />
      </header>
      <main>
        <h1>Dashboard</h1>
        <p>Charts go here.</p>
      </main>
    </div>
  );
}
