export type { Product } from './model/product';
export { ProductCard } from './ui/product-card';
export { normalizeProduct } from './model/product';
// Partial fix: exports normalizeProduct, but the widget still imports from internal path
