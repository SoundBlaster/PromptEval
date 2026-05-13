import { useState } from 'react';
import { NoteListItem, useNotes, type Note } from '@/entities/note';
import { CreateNoteButton, buildEmptyNote } from '@/features/create-note';
import { NoteEditor } from '@/features/edit-note';
import { DeleteNoteButton } from '@/features/delete-note';

export function EditorPage() {
  const { notes, setNotes } = useNotes();
  const [activeId, setActiveId] = useState<string | null>(notes[0]?.id ?? null);
  const active = notes.find((n) => n.id === activeId) ?? null;

  function createNote() {
    const note = buildEmptyNote();
    setNotes((prev) => [note, ...prev]);
    setActiveId(note.id);
  }

  function updateActive(next: Note) {
    setNotes((prev) => prev.map((n) => (n.id === next.id ? next : n)));
  }

  function deleteActive() {
    if (!active) return;
    setNotes((prev) => prev.filter((n) => n.id !== active.id));
    setActiveId(null);
  }

  return (
    <main>
      <aside>
        <CreateNoteButton onCreate={createNote} />
        <ul>
          {notes.map((note) => (
            <NoteListItem
              key={note.id}
              note={note}
              active={note.id === activeId}
              onSelect={() => setActiveId(note.id)}
            />
          ))}
        </ul>
      </aside>
      <section>
        {active ? (
          <>
            <NoteEditor note={active} onChange={updateActive} />
            <DeleteNoteButton onDelete={deleteActive} />
          </>
        ) : (
          <p>Select or create a note.</p>
        )}
      </section>
    </main>
  );
}
