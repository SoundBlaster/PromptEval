import { useEffect, useState } from 'react';
import { getProducts, ProductCard, type Product } from '@/entities/product';
import { useCart, CartSummary } from '@/entities/cart';
import { AddToCartButton } from '@/features/add-to-cart';

export function CatalogPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const cart = useCart();

  useEffect(() => {
    getProducts().then(setProducts);
  }, []);

  return (
    <main>
      <header>
        <h1>Catalog</h1>
        <CartSummary count={cart.count} />
      </header>
      <section>
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            actionSlot={<AddToCartButton onAdd={() => cart.add(product.id)} />}
          />
        ))}
      </section>
    </main>
  );
}
