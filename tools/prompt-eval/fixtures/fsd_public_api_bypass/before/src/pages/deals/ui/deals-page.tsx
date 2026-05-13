import { ProductGrid } from '@/widgets/product-grid';
import { ProductCard } from '@/entities/product';

export function DealsPage() {
  return (
    <div>
      <h1>Today's Deals</h1>
      <ProductGrid />
    </div>
  );
}
