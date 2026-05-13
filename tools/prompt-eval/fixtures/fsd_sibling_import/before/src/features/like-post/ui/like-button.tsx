// FSD VIOLATION: cross-feature import from a sibling slice
import { ActionButton } from '@/features/send-comment/ui/send-button';
import { useLikePost } from '../model/use-like-post';

interface Props {
  postId: string;
}

export function LikeButton({ postId }: Props) {
  const { like } = useLikePost(postId);
  return <ActionButton onClick={like}>Like</ActionButton>;
}
