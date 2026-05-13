import { useEffect, useState } from 'react';

interface Note {
  id: string;
  title: string;
  body: string;
}

export function NotesApp() {
  const [notes, setNotes] = useState<Note[]>(() => {
    const raw = localStorage.getItem('notes');
    return raw ? JSON.parse(raw) : [];
  });
  const [activeId, setActiveId] = useState<string | null>(notes[0]?.id ?? null);

  useEffect(() => {
    localStorage.setItem('notes', JSON.stringify(notes));
  }, [notes]);

  const active = notes.find((n) => n.id === activeId);

  return (
    <main>
      <aside>
        <button
          onClick={() => {
            const n = { id: crypto.randomUUID(), title: '', body: '' };
            setNotes([n, ...notes]);
            setActiveId(n.id);
          }}
        >
          New note
        </button>
        <ul>
          {notes.map((n) => (
            <li key={n.id}>
              <button onClick={() => setActiveId(n.id)}>{n.title || '(untitled)'}</button>
            </li>
          ))}
        </ul>
      </aside>
      <section>
        {active ? (
          <>
            <input
              value={active.title}
              onChange={(e) => setNotes(notes.map((n) => (n.id === active.id ? { ...n, title: e.target.value } : n)))}
            />
            <textarea
              value={active.body}
              onChange={(e) => setNotes(notes.map((n) => (n.id === active.id ? { ...n, body: e.target.value } : n)))}
            />
            <button
              onClick={() => {
                setNotes(notes.filter((n) => n.id !== active.id));
                setActiveId(null);
              }}
            >
              Delete
            </button>
          </>
        ) : (
          <p>Select or create a note.</p>
        )}
      </section>
    </main>
  );
}
