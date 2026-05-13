interface Product {
  id: string;
  name: string;
  price: number;
}

interface Props {
  product: Product;
  onAdd: () => void;
}

export function ProductCard({ product, onAdd }: Props) {
  return (
    <article>
      <h3>{product.name}</h3>
      <p>${product.price.toFixed(2)}</p>
      <button type="button" onClick={onAdd}>Add to cart</button>
    </article>
  );
}
