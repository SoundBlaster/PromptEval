interface Props {
  onAdd: () => void;
}

export function AddToCartButton({ onAdd }: Props) {
  return (
    <button type="button" onClick={onAdd}>
      Add to cart
    </button>
  );
}
