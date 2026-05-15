const BASE = '/api';

export interface Post {
  id: string;
  title: string;
  body: string;
  likes: number;
  comments: Array<{ id: string; text: string }>;
}

export async function fetchPosts(): Promise<Post[]> {
  const res = await fetch(`${BASE}/posts`);
  if (!res.ok) throw new Error(`Failed to fetch posts: ${res.status}`);
  return res.json() as Promise<Post[]>;
}

export async function likePost(postId: string): Promise<{ likes: number }> {
  const res = await fetch(`${BASE}/posts/${postId}/like`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to like post: ${res.status}`);
  return res.json() as Promise<{ likes: number }>;
}

export async function addComment(
  postId: string,
  text: string,
): Promise<{ id: string; text: string }> {
  const res = await fetch(`${BASE}/posts/${postId}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`Failed to add comment: ${res.status}`);
  return res.json() as Promise<{ id: string; text: string }>;
}
