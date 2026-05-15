import type { Post } from '../services/api';

interface PostCardProps {
  post: Post;
  onLike: () => void;
  onComment: (text: string) => void;
}

export function PostCard({ post, onLike, onComment }: PostCardProps) {
  return (
    <article>
      <h2>{post.title}</h2>
      <p>{post.body}</p>
      <span>{post.likes} likes</span>
      <button type="button" onClick={onLike}>Like</button>
      <ul>
        {post.comments.map((c) => <li key={c.id}>{c.text}</li>)}
      </ul>
    </article>
  );
}
