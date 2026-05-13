interface Props {
  count: number;
}

export function CartSummary({ count }: Props) {
  return (
    <span aria-label="cart items">
      Cart: {count}
    </span>
  );
}
