import { useEffect, useState } from 'react';
import { readJSON, writeJSON } from '@/shared/lib/storage';
import type { Todo } from './todo';

const KEY = 'todos.v1';

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>(() => readJSON<Todo[]>(KEY, []));
  useEffect(() => writeJSON(KEY, todos), [todos]);
  return { todos, setTodos };
}
