import { LikeButton } from '@/features/like-post';
import { CommentForm } from '@/features/send-comment';

const FEATURED_POST_ID = 'featured-001';

export function HomePage() {
  return (
    <div>
      <h1>Latest post</h1>
      <LikeButton postId={FEATURED_POST_ID} />
      <CommentForm postId={FEATURED_POST_ID} />
    </div>
  );
}
