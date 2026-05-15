import { useAuth } from '@/shared/lib/auth';
import { useNavigate } from 'react-router-dom';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  function handleLogin() {
    login('demo-token');
    navigate('/');
  }

  return (
    <main>
      <h1>Login</h1>
      <button onClick={handleLogin}>Sign in</button>
    </main>
  );
}
