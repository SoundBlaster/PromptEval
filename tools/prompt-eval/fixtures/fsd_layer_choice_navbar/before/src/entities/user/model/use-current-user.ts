import { useEffect, useState } from 'react';
import { httpGet } from '@/shared/api';
import type { User } from './user';

export function useCurrentUser() {
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    httpGet<User>('/api/me').then(setUser);
  }, []);
  return user;
}
