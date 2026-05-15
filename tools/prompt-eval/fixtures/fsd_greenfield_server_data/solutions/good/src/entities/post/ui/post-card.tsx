import type { ReactNode } from 'react';
import type { Post } from '../model/post';

interface PostCardProps {
  post: Post;
  likeSlot?: ReactNode;
  commentSlot?: ReactNode;
}

export function PostCard({ post, likeSlot, commentSlot }: PostCardProps) {
  return (
    <article>
      <h2>{post.title}</h2>
      <p>{post.body}</p>
      <footer>
        <span>{post.likes} likes</span>
        {likeSlot}
      </footer>
      <section>
        <h3>Comments ({post.comments.length})</h3>
        <ul>
          {post.comments.map((c) => (
            <li key={c.id}>{c.text}</li>
          ))}
        </ul>
        {commentSlot}
      </section>
    </article>
  );
}
