import { useState, useEffect } from 'react';
import { fetchPosts, type Post } from '../services/api';

export function usePosts() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPosts()
      .then(setPosts)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Error');
      })
      .finally(() => setLoading(false));
  }, []);

  return { posts, setPosts, loading, error };
}
