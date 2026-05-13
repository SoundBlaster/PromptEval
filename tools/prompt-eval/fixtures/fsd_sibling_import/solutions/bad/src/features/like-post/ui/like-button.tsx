// Still a cross-feature import — now via index, but FSD slice isolation still violated
import { ActionButton } from '@/features/send-comment';
import { useLikePost } from '../model/use-like-post';

interface Props {
  postId: string;
}

export function LikeButton({ postId }: Props) {
  const { like } = useLikePost(postId);
  return <ActionButton onClick={like}>Like</ActionButton>;
}
