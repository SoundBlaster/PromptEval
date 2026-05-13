interface Props {
  onCreate: () => void;
}

export function CreateNoteButton({ onCreate }: Props) {
  return (
    <button type="button" onClick={onCreate}>
      New note
    </button>
  );
}
