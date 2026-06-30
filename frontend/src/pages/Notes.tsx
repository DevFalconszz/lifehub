import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useT } from '../modules/i18n/store';

export default function Notes() {
  const [notes, setNotes] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [editId, setEditId] = useState<string | null>(null);
  const t = useT();

  const load = () => api.listNotes().then((r) => setNotes(r.data || []));

  useEffect(() => { load(); }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editId) {
      await api.updateNote(editId, { title, content });
      setEditId(null);
    } else {
      await api.createNote({ title, content });
    }
    setTitle('');
    setContent('');
    load();
  };

  const edit = (n: any) => {
    setEditId(n.id);
    setTitle(n.title);
    setContent(n.content);
  };

  const del = async (id: string) => {
    await api.deleteNote(id);
    if (editId === id) { setEditId(null); setTitle(''); setContent(''); }
    load();
  };

  const togglePin = async (n: any) => {
    await api.updateNote(n.id, { pinned: !n.pinned });
    load();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 dark:text-gray-100">{t('notes.title')}</h1>

      <form onSubmit={submit} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6 space-y-3">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder={t('notes.noteTitle')} required
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder={t('notes.content')}
          rows={4} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        <div className="flex gap-2">
          <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">
            {editId ? t('common.update') : t('common.create')}
          </button>
          {editId && <button type="button" onClick={() => { setEditId(null); setTitle(''); setContent(''); }}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg text-sm">{t('common.cancel')}</button>}
        </div>
      </form>

      <div className="grid grid-cols-2 gap-4">
        {[...notes].sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0)).map((n) => (
          <div key={n.id} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold dark:text-gray-100">{n.title}</h3>
              <div className="flex gap-1">
                <button onClick={() => togglePin(n)}
                  className={`text-xs px-1.5 py-0.5 rounded ${n.pinned ? 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300' : 'text-gray-400 dark:text-gray-500'}`}>
                  {n.pinned ? '★' : '☆'}
                </button>
                <button onClick={() => edit(n)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-primary-600 dark:hover:text-primary-400">{t('common.edit')}</button>
                <button onClick={() => del(n.id)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400">{t('common.del')}</button>
              </div>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap line-clamp-4">{n.content}</p>
            {n.tags?.length > 0 && (
              <div className="flex gap-1 mt-2">
                {n.tags.map((tag: string) => (
                  <span key={tag} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-1.5 py-0.5 rounded">{tag}</span>
                ))}
              </div>
            )}
          </div>
        ))}
        {notes.length === 0 && <p className="text-gray-400 dark:text-gray-500 text-center py-8 col-span-2">{t('notes.noNotes')}</p>}
      </div>
    </div>
  );
}
