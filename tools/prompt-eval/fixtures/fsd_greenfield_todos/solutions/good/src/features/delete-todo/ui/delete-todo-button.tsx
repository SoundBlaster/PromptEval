interface Props {
  onDelete: () => void;
}

export function DeleteTodoButton({ onDelete }: Props) {
  return (
    <button type="button" onClick={onDelete}>
      Delete
    </button>
  );
}
