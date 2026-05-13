import type { Todo } from '../model/todo';

interface Props {
  todo: Todo;
  actionSlot?: React.ReactNode;
}

export function TodoRow({ todo, actionSlot }: Props) {
  return (
    <li>
      <span style={{ textDecoration: todo.done ? 'line-through' : 'none' }}>{todo.text}</span>
      {actionSlot}
    </li>
  );
}
