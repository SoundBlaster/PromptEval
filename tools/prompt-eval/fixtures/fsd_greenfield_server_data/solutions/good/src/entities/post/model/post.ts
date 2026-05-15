import { useState, useEffect } from 'react';
import { getPosts } from '../api/posts-api';

export interface Post {
  id: string;
  title: string;
  body: string;
  likes: number;
  comments: Comment[];
}

export interface Comment {
  id: string;
  text: string;
}

interface UsePostsResult {
  posts: Post[];
  loading: boolean;
  error: string | null;
  setPosts: React.Dispatch<React.SetStateAction<Post[]>>;
}

export function usePosts(): UsePostsResult {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getPosts()
      .then(setPosts)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Unknown error');
      })
      .finally(() => setLoading(false));
  }, []);

  return { posts, loading, error, setPosts };
}
