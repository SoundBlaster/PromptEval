import { TodoRow, useTodos } from '@/entities/todo';
import { AddTodoForm } from '@/features/add-todo';
import { ToggleTodoButton } from '@/features/toggle-todo';
import { DeleteTodoButton } from '@/features/delete-todo';

export function TodosPage() {
  const { todos, setTodos } = useTodos();

  return (
    <main>
      <h1>Todos</h1>
      <AddTodoForm onAdd={(todo) => setTodos((prev) => [...prev, todo])} />
      <ul>
        {todos.map((todo) => (
          <TodoRow
            key={todo.id}
            todo={todo}
            actionSlot={
              <>
                <ToggleTodoButton
                  done={todo.done}
                  onToggle={() =>
                    setTodos((prev) => prev.map((t) => (t.id === todo.id ? { ...t, done: !t.done } : t)))
                  }
                />
                <DeleteTodoButton onDelete={() => setTodos((prev) => prev.filter((t) => t.id !== todo.id))} />
              </>
            }
          />
        ))}
      </ul>
    </main>
  );
}
