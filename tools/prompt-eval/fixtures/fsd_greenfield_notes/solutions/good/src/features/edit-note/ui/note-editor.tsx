import type { Note } from '@/entities/note';

interface Props {
  note: Note;
  onChange: (next: Note) => void;
}

export function NoteEditor({ note, onChange }: Props) {
  return (
    <div>
      <input
        value={note.title}
        placeholder="Title"
        onChange={(e) => onChange({ ...note, title: e.target.value, updatedAt: Date.now() })}
      />
      <textarea
        value={note.body}
        placeholder="Write here…"
        onChange={(e) => onChange({ ...note, body: e.target.value, updatedAt: Date.now() })}
      />
    </div>
  );
}
