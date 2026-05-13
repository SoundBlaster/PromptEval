import { useCurrentUser, UserBadge } from '@/entities/user';
import { LogoutButton } from '@/features/logout';
import { NotificationsIcon } from '@/features/show-notifications';

export function AppHeader() {
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
