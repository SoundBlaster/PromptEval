import { SettingsForm } from '@/features/user-settings';

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
