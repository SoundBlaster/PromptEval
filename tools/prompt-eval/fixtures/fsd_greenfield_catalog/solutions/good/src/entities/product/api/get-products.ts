import { httpGet } from '@/shared/api';
import type { Product } from '../model/product';

export function getProducts(): Promise<Product[]> {
  return httpGet<Product[]>('/api/products');
}
