import type { Note } from '../model/note';

interface Props {
  note: Note;
  active: boolean;
  onSelect: () => void;
}

export function NoteListItem({ note, active, onSelect }: Props) {
  return (
    <li>
      <button type="button" onClick={onSelect} aria-current={active}>
        {note.title || '(untitled)'}
      </button>
    </li>
  );
}
