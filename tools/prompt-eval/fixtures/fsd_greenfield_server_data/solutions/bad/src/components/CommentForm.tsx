import { useState } from 'react';
import { addComment } from '../services/api';

interface CommentFormProps {
  postId: string;
  onAdded: (comment: { id: string; text: string }) => void;
}

export function CommentForm({ postId, onAdded }: CommentFormProps) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    try {
      const comment = await addComment(postId, text.trim());
      onAdded(comment);
      setText('');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add a comment…"
        disabled={loading}
      />
      <button type="submit" disabled={loading || !text.trim()}>
        Comment
      </button>
    </form>
  );
}
