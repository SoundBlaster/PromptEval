import type { Product } from '../model/product';

interface Props {
  product: Product;
  actionSlot?: React.ReactNode;
}

export function ProductCard({ product, actionSlot }: Props) {
  return (
    <article>
      <h3>{product.name}</h3>
      <p>${product.price.toFixed(2)}</p>
      {actionSlot}
    </article>
  );
}
