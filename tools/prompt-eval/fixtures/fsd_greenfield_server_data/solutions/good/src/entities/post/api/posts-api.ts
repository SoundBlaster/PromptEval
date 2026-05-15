import { httpGet } from '@/shared/api';
import type { Post } from '../model/post';

export function getPosts(): Promise<Post[]> {
  return httpGet<Post[]>('/posts');
}
