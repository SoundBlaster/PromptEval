import { useState } from 'react';
import { likePost } from '../api/like-post';

interface LikeButtonProps {
  postId: string;
  onLiked: (newLikes: number) => void;
}

export function LikeButton({ postId, onLiked }: LikeButtonProps) {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    try {
      const result = await likePost(postId);
      onLiked(result.likes);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button type="button" onClick={handleClick} disabled={loading}>
      {loading ? '…' : 'Like'}
    </button>
  );
}
