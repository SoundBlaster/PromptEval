import { useEffect, useState } from 'react';

interface Todo {
  id: string;
  text: string;
  done: boolean;
}

export function TodoList() {
  const [todos, setTodos] = useState<Todo[]>(() => {
    const raw = localStorage.getItem('todos');
    return raw ? JSON.parse(raw) : [];
  });
  const [text, setText] = useState('');

  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos));
  }, [todos]);

  return (
    <main>
      <h1>Todos</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!text.trim()) return;
          setTodos([...todos, { id: crypto.randomUUID(), text: text.trim(), done: false }]);
          setText('');
        }}
      >
        <input value={text} onChange={(e) => setText(e.target.value)} />
        <button type="submit">Add</button>
      </form>
      <ul>
        {todos.map((t) => (
          <li key={t.id}>
            <span style={{ textDecoration: t.done ? 'line-through' : 'none' }}>{t.text}</span>
            <button onClick={() => setTodos(todos.map((x) => (x.id === t.id ? { ...x, done: !x.done } : x)))}>
              {t.done ? 'Undo' : 'Done'}
            </button>
            <button onClick={() => setTodos(todos.filter((x) => x.id !== t.id))}>Delete</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
