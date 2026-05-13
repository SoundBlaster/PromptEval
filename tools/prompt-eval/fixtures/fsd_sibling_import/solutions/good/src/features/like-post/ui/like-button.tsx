import { ActionButton } from '@/shared/ui';
import { useLikePost } from '../model/use-like-post';

interface Props {
  postId: string;
}

export function LikeButton({ postId }: Props) {
  const { like } = useLikePost(postId);
  return <ActionButton onClick={like}>Like</ActionButton>;
}
