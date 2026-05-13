import { useEffect, useState } from 'react';
import { readJSON, writeJSON } from '@/shared/lib/storage';

const CART_KEY = 'cart.v1';

interface CartItem {
  productId: string;
  quantity: number;
}

export function useCart() {
  const [items, setItems] = useState<CartItem[]>(() => readJSON<CartItem[]>(CART_KEY, []));

  useEffect(() => {
    writeJSON(CART_KEY, items);
  }, [items]);

  function add(productId: string) {
    setItems((prev) => {
      const existing = prev.find((item) => item.productId === productId);
      if (existing) {
        return prev.map((item) =>
          item.productId === productId ? { ...item, quantity: item.quantity + 1 } : item,
        );
      }
      return [...prev, { productId, quantity: 1 }];
    });
  }

  const count = items.reduce((sum, item) => sum + item.quantity, 0);
  return { items, count, add };
}
