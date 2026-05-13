import type { Product } from '../model/product';

interface Props {
  product: Product;
}

export function ProductCard({ product }: Props) {
  return (
    <div>
      <span>{product.name}</span>
      <span>${product.price.toFixed(2)}</span>
    </div>
  );
}
