import { useEffect, useState } from 'react';

const KEY = 'cart';

export function useCart() {
  const [items, setItems] = useState<{ productId: string; quantity: number }[]>(() => {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  });

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(items));
  }, [items]);

  function add(productId: string) {
    setItems((prev) => {
      const existing = prev.find((i) => i.productId === productId);
      if (existing) {
        return prev.map((i) => (i.productId === productId ? { ...i, quantity: i.quantity + 1 } : i));
      }
      return [...prev, { productId, quantity: 1 }];
    });
  }

  return { items, count: items.reduce((s, i) => s + i.quantity, 0), add };
}
