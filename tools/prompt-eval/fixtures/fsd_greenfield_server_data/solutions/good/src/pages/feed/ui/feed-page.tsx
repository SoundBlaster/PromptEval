import { usePosts, PostCard } from '@/entities/post';
import { LikeButton } from '@/features/like-post';
import { CommentForm } from '@/features/add-comment';
import { Spinner } from '@/shared/ui/spinner';

export function FeedPage() {
  const { posts, loading, error, setPosts } = usePosts();

  if (loading) return <Spinner />;
  if (error) return <p role="alert">Error: {error}</p>;

  function handleLiked(postId: string, newLikes: number) {
    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? { ...p, likes: newLikes } : p)),
    );
  }

  function handleCommentAdded(
    postId: string,
    comment: { id: string; text: string },
  ) {
    setPosts((prev) =>
      prev.map((p) =>
        p.id === postId
          ? { ...p, comments: [...p.comments, comment] }
          : p,
      ),
    );
  }

  return (
    <main>
      <h1>Feed</h1>
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          likeSlot={
            <LikeButton
              postId={post.id}
              onLiked={(likes) => handleLiked(post.id, likes)}
            />
          }
          commentSlot={
            <CommentForm
              postId={post.id}
              onAdded={(c) => handleCommentAdded(post.id, c)}
            />
          }
        />
      ))}
    </main>
  );
}
