interface Props {
  onDelete: () => void;
}

export function DeleteNoteButton({ onDelete }: Props) {
  return (
    <button type="button" onClick={onDelete}>
      Delete
    </button>
  );
}
