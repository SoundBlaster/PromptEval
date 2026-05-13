import { useEffect, useState } from 'react';
import { readJSON, writeJSON } from '@/shared/lib/storage';
import type { Note } from './note';

const KEY = 'notes.v1';

export function useNotes() {
  const [notes, setNotes] = useState<Note[]>(() => readJSON<Note[]>(KEY, []));
  useEffect(() => writeJSON(KEY, notes), [notes]);
  return { notes, setNotes };
}
