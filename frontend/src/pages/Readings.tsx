import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useT } from '../modules/i18n/store';

const types = ['book', 'article', 'video', 'link', 'idea'];
const statuses = ['unread', 'reading', 'completed', 'archived'];

export default function Readings() {
  const [items, setItems] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [type, setType] = useState('book');
  const [author, setAuthor] = useState('');
  const [url, setUrl] = useState('');
  const [editId, setEditId] = useState<string | null>(null);
  const t = useT();

  const load = () => api.listReadings().then((r) => setItems(r.data || []));

  useEffect(() => { load(); }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const data = { title, type, author: author || undefined, url: url || undefined };
    if (editId) {
      await api.updateReading(editId, data);
      setEditId(null);
    } else {
      await api.createReading(data);
    }
    setTitle('');
    setType('book');
    setAuthor('');
    setUrl('');
    load();
  };

  const edit = (item: any) => {
    setEditId(item.id);
    setTitle(item.title);
    setType(item.type);
    setAuthor(item.author || '');
    setUrl(item.url || '');
  };

  const updateStatus = async (item: any, status: string) => {
    await api.updateReading(item.id, { status });
    load();
  };

  const del = async (id: string) => {
    await api.deleteReading(id);
    if (editId === id) { setEditId(null); setTitle(''); }
    load();
  };

  const typeIcon: Record<string, string> = { book: '📖', article: '📄', video: '🎬', link: '🔗', idea: '💡' };
  const statusDot: Record<string, string> = { unread: 'bg-gray-300 dark:bg-gray-600', reading: 'bg-blue-500', completed: 'bg-green-500', archived: 'bg-yellow-500' };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 dark:text-gray-100">{t('readings.title')}</h1>

      <form onSubmit={submit} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6 space-y-3">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder={t('readings.title_')} required
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        <div className="grid grid-cols-3 gap-2">
          <select value={type} onChange={(e) => setType(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100">
            {types.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <input value={author} onChange={(e) => setAuthor(e.target.value)} placeholder={t('readings.author')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
          <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder={t('readings.url')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        </div>
        <div className="flex gap-2">
          <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">
            {editId ? t('common.update') : t('common.add')}
          </button>
          {editId && <button type="button" onClick={() => { setEditId(null); setTitle(''); setType('book'); setAuthor(''); setUrl(''); }}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg text-sm">{t('common.cancel')}</button>}
        </div>
      </form>

      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.id} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xl">{typeIcon[item.type] || '📄'}</span>
              <div>
                <p className="font-medium dark:text-gray-100">{item.title}</p>
                <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>{item.type}</span>
                  {item.author && <span>&middot; {item.author}</span>}
                  {item.url && <a href={item.url} target="_blank" className="text-primary-600 dark:text-primary-400 hover:underline">Link</a>}
                  <span className={`w-1.5 h-1.5 rounded-full ${statusDot[item.status] || 'bg-gray-300'} inline-block`} />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <select value={item.status} onChange={(e) => updateStatus(item, e.target.value)}
                className="text-xs border border-gray-300 dark:border-gray-600 rounded px-1 py-0.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100">
                {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
              <button onClick={() => edit(item)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-primary-600 dark:hover:text-primary-400 ml-2">{t('common.edit')}</button>
              <button onClick={() => del(item.id)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400">{t('common.del')}</button>
            </div>
          </div>
        ))}
        {items.length === 0 && <p className="text-gray-400 dark:text-gray-500 text-center py-8">{t('readings.noReadings')}</p>}
      </div>
    </div>
  );
}
