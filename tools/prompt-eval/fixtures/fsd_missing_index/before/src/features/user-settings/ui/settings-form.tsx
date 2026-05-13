interface Props {
  userId: string;
}

export function SettingsForm({ userId }: Props) {
  function save() {
    console.log('saving settings for', userId);
  }
  return (
    <form onSubmit={(e) => { e.preventDefault(); save(); }}>
      <input name="displayName" type="text" placeholder="Display name" />
      <button type="submit">Save</button>
    </form>
  );
}
