export interface Product {
  id: string;
  name: string;
  price: number;
}

export function normalizeProduct(raw: Record<string, unknown>): Product {
  return {
    id: String(raw['id']),
    name: String(raw['name']),
    price: Number(raw['price']),
  };
}
