// FSD VIOLATION: imports directly from feature internal path — no index.ts exists
import { SettingsForm } from '@/features/user-settings/ui/settings-form';

interface Props {
  userId: string;
}

export function SettingsPage({ userId }: Props) {
  return (
    <main>
      <h1>Settings</h1>
      <SettingsForm userId={userId} />
    </main>
  );
}
