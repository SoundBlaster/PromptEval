import { LoginForm } from '@/features/login';

export function LandingPage() {
  return (
    <main>
      <h1>Welcome</h1>
      <section>
        <h2>Sign in to continue</h2>
        <LoginForm />
      </section>
    </main>
  );
}
