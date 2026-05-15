import { ThemeToggle } from '@/features/switch-theme';
import { LocaleSwitcher } from '@/features/switch-locale';
import { SignInButton } from '@/features/sign-in';

export function SettingsPanel() {
  return (
    <section>
      <h2>Settings</h2>
      <div>
        <label>Theme</label>
        <ThemeToggle />
      </div>
      <div>
        <label>Language</label>
        <LocaleSwitcher />
      </div>
      <div>
        <label>Auth</label>
        <SignInButton />
      </div>
    </section>
  );
}
