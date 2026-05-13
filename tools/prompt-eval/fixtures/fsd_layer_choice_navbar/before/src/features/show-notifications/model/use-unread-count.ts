import { useEffect, useState } from 'react';
import { httpGet } from '@/shared/api';

export function useUnreadCount() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    httpGet<{ unread: number }>('/api/notifications/unread').then((r) => setCount(r.unread));
  }, []);
  return count;
}
