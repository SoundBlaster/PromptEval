// Bad: imports directly from internal path instead of public API
import { LoginForm } from '@/features/login/LoginForm';

export function AuthPage() {
  return (
    <main>
      <h1>Sign In</h1>
      <LoginForm />
    </main>
  );
}
