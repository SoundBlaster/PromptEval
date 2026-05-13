import { normalizeProduct, ProductCard } from '@/entities/product';

const rawProducts = [
  { id: '1', name: 'Widget', price: 9.99 },
  { id: '2', name: 'Gadget', price: 24.99 },
];

export function ProductGrid() {
  const products = rawProducts.map(normalizeProduct);
  return (
    <div>
      {products.map((p) => (
        <ProductCard key={p.id} product={p} />
      ))}
    </div>
  );
}
