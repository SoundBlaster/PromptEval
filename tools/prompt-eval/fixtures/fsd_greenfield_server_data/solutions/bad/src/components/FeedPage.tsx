import { usePosts } from '../hooks/usePosts';
import { Spinner } from './Spinner';
import { LikeButton } from './LikeButton';
import { CommentForm } from './CommentForm';

export function FeedPage() {
  const { posts, setPosts, loading, error } = usePosts();

  if (loading) return <Spinner />;
  if (error) return <p role="alert">Error: {error}</p>;

  return (
    <main>
      <h1>Feed</h1>
      {posts.map((post) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.body}</p>
          <span>{post.likes} likes</span>
          <LikeButton
            postId={post.id}
            onLiked={(likes) =>
              setPosts((prev) =>
                prev.map((p) => (p.id === post.id ? { ...p, likes } : p)),
              )
            }
          />
          <ul>
            {post.comments.map((c) => (
              <li key={c.id}>{c.text}</li>
            ))}
          </ul>
          <CommentForm
            postId={post.id}
            onAdded={(c) =>
              setPosts((prev) =>
                prev.map((p) =>
                  p.id === post.id
                    ? { ...p, comments: [...p.comments, c] }
                    : p,
                ),
              )
            }
          />
        </article>
      ))}
    </main>
  );
}
