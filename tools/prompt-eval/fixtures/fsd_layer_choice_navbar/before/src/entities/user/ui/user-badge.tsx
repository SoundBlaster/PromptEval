import type { User } from '../model/user';

interface Props {
  user: User;
}

export function UserBadge({ user }: Props) {
  return (
    <span>
      <img src={user.avatarUrl} alt="" width={24} height={24} />
      {user.name}
    </span>
  );
}
