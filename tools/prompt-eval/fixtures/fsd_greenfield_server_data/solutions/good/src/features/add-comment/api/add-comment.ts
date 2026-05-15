import { httpPost } from '@/shared/api';
import type { Comment } from '@/entities/post';

export function addComment(
  postId: string,
  text: string,
): Promise<Comment> {
  return httpPost<Comment>(`/posts/${postId}/comments`, { text });
}
