import { LikeButton } from '@/features/like-post';
import { CommentForm } from '@/features/send-comment';

interface Props {
  postId: string;
}

export function PostPage({ postId }: Props) {
  return (
    <div>
      <LikeButton postId={postId} />
      <CommentForm postId={postId} />
    </div>
  );
}
