import { httpPost } from '@/shared/api';

interface LoginResponse {
  token: string;
}

export async function loginRequest(username: string, password: string): Promise<LoginResponse> {
  return httpPost<LoginResponse>('/api/auth/login', { username, password });
}
