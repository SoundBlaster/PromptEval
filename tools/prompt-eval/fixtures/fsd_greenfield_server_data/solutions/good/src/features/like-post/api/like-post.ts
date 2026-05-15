import { httpPost } from '@/shared/api';

export function likePost(postId: string): Promise<{ likes: number }> {
  return httpPost<{ likes: number }>(`/posts/${postId}/like`);
}
