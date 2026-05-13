import { useUnreadCount } from '../model/use-unread-count';

export function NotificationsIcon() {
  const count = useUnreadCount();
  return (
    <span aria-label="notifications">
      🔔{count > 0 && <em>{count}</em>}
    </span>
  );
}
