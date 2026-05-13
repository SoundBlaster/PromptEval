export function LogoutButton() {
  function logout() {
    document.cookie = 'session=; Max-Age=0';
    window.location.reload();
  }
  return (
    <button type="button" onClick={logout}>
      Log out
    </button>
  );
}
