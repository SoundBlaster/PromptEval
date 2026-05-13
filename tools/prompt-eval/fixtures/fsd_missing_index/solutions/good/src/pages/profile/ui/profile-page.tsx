import { SettingsForm } from '@/features/user-settings';

interface Props {
  userId: string;
}

export function ProfilePage({ userId }: Props) {
  return (
    <main>
      <h1>Profile</h1>
      <section>
        <h2>Your settings</h2>
        <SettingsForm userId={userId} />
      </section>
    </main>
  );
}
