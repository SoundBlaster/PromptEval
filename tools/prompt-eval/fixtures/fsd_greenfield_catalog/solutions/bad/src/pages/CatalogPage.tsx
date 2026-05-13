import { useEffect, useState } from 'react';
import { ProductCard } from '../components/ProductCard';
import { useCart } from '../hooks/useCart';
import { fetchProducts } from '../services/api';

export function CatalogPage() {
  const [products, setProducts] = useState<{ id: string; name: string; price: number }[]>([]);
  const cart = useCart();

  useEffect(() => {
    fetchProducts().then(setProducts);
  }, []);

  return (
    <main>
      <header>
        <h1>Catalog</h1>
        <span>Cart: {cart.count}</span>
      </header>
      {products.map((p) => (
        <ProductCard key={p.id} product={p} onAdd={() => cart.add(p.id)} />
      ))}
    </main>
  );
}
