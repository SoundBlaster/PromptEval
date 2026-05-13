import { useState } from 'react';
import type { Todo } from '@/entities/todo';

interface Props {
  onAdd: (todo: Todo) => void;
}

export function AddTodoForm({ onAdd }: Props) {
  const [text, setText] = useState('');
  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    onAdd({ id: crypto.randomUUID(), text: text.trim(), done: false });
    setText('');
  }
  return (
    <form onSubmit={submit}>
      <input value={text} onChange={(e) => setText(e.target.value)} placeholder="New todo" />
      <button type="submit">Add</button>
    </form>
  );
}
