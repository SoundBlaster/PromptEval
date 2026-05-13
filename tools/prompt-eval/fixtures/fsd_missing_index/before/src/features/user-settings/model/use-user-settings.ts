export function useUserSettings(userId: string) {
  function saveSettings(displayName: string) {
    console.log('saving', displayName, 'for', userId);
  }
  return { saveSettings };
}
