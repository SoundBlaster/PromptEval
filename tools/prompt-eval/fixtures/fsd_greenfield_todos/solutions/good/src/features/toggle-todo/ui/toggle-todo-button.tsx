interface Props {
  done: boolean;
  onToggle: () => void;
}

export function ToggleTodoButton({ done, onToggle }: Props) {
  return (
    <button type="button" onClick={onToggle}>
      {done ? 'Undo' : 'Done'}
    </button>
  );
}
