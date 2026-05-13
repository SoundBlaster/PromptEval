import type { Note } from '@/entities/note';

export function buildEmptyNote(): Note {
  return { id: crypto.randomUUID(), title: '', body: '', updatedAt: Date.now() };
}
