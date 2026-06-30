import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useT } from '../modules/i18n/store';

const PRIORITIES = ['low', 'medium', 'high', 'urgent'] as const;
const priorityColor: Record<string, string> = {
  low: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
  medium: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
  high: 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300',
  urgent: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
};
const statusColor = (s: string) =>
  s === 'active'
    ? 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300'
    : s === 'paused'
      ? 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300'
      : s === 'completed'
        ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300'
        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400';

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [priority, setPriority] = useState('medium');
  const [category, setCategory] = useState('');
  const [progress, setProgress] = useState(0);
  const [startAt, setStartAt] = useState('');
  const [targetAt, setTargetAt] = useState('');
  const [url, setUrl] = useState('');
  const [editId, setEditId] = useState<string | null>(null);
  const t = useT();

  const load = () => api.listProjects().then((r) => setProjects(r.data || []));

  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setName(''); setDesc(''); setPriority('medium'); setCategory('');
    setProgress(0); setStartAt(''); setTargetAt(''); setUrl('');
    setEditId(null);
  };

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      name,
      description: desc || undefined,
      priority,
      category: category || undefined,
      progress,
      start_at: startAt ? new Date(startAt).toISOString() : undefined,
      target_at: targetAt ? new Date(targetAt).toISOString() : undefined,
      url: url || undefined,
    };
    if (editId) {
      await api.updateProject(editId, data);
    } else {
      await api.createProject(data);
    }
    resetForm();
    load();
  };

  const fillEdit = (p: any) => {
    setEditId(p.id);
    setName(p.name);
    setDesc(p.description || '');
    setPriority(p.priority || 'medium');
    setCategory(p.category || '');
    setProgress(p.progress || 0);
    setStartAt(p.start_at ? new Date(p.start_at).toISOString().slice(0, 10) : '');
    setTargetAt(p.target_at ? new Date(p.target_at).toISOString().slice(0, 10) : '');
    setUrl(p.url || '');
  };

  const toggleArchive = async (p: any) => {
    await api.updateProject(p.id, { status: p.status === 'active' ? 'archived' : 'active' });
    load();
  };

  const del = async (id: string) => {
    await api.deleteProject(id);
    load();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 dark:text-gray-100">{t('projects.title')}</h1>

      <form onSubmit={create} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder={t('projects.name')} required
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
          <input value={category} onChange={(e) => setCategory(e.target.value)} placeholder={t('projects.category')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        </div>
        <input value={desc} onChange={(e) => setDesc(e.target.value)} placeholder={t('projects.description')}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        <div className="grid grid-cols-2 gap-3">
          <select value={priority} onChange={(e) => setPriority(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100">
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>{t(`projects.priority_${p}`)}</option>
            ))}
          </select>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 dark:text-gray-400 w-16">{t('projects.progress')}: {progress}%</span>
            <input type="range" min={0} max={100} value={progress} onChange={(e) => setProgress(parseInt(e.target.value))}
              className="flex-1 accent-primary-600" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <input type="date" value={startAt} onChange={(e) => setStartAt(e.target.value)}
            placeholder={t('projects.startDate')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
          <input type="date" value={targetAt} onChange={(e) => setTargetAt(e.target.value)}
            placeholder={t('projects.targetDate')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        </div>
        <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder={t('projects.url')}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        <div className="flex gap-2">
          <button type="submit"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">
            {editId ? t('common.update') : t('common.create')}
          </button>
          {editId && <button type="button" onClick={resetForm}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg text-sm">{t('common.cancel')}</button>}
        </div>
      </form>

      <div className="space-y-3">
        {projects.map((p) => (
          <div key={p.id} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold dark:text-gray-100">{p.name}</h3>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColor(p.status)}`}>
                    {t(`projects.status_${p.status}`)}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${priorityColor[p.priority || 'medium']}`}>
                    {t(`projects.priority_${p.priority || 'medium'}`)}
                  </span>
                </div>
                {p.description && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{p.description}</p>}
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-400 dark:text-gray-500">
                  {p.category && <span>{p.category}</span>}
                  {p.start_at && <span>{t('projects.startDate')}: {new Date(p.start_at).toLocaleDateString()}</span>}
                  {p.target_at && <span>{t('projects.targetDate')}: {new Date(p.target_at).toLocaleDateString()}</span>}
                  {p.url && <a href={p.url} target="_blank" rel="noopener noreferrer"
                    className="text-primary-600 dark:text-primary-400 hover:underline">{t('projects.link')}</a>}
                  <span>{p.task_count ?? 0} {t('tasks.title').toLowerCase()}</span>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-primary-500 h-2 rounded-full transition-all" style={{ width: `${p.progress || 0}%` }} />
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{p.progress || 0}%</span>
                </div>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <button onClick={() => fillEdit(p)}
                  className="text-xs text-gray-400 dark:text-gray-500 hover:text-primary-600 dark:hover:text-primary-400">{t('common.edit')}</button>
                <button onClick={() => toggleArchive(p)}
                  className="text-xs text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">
                  {p.status === 'active' ? t('common.archive') : t('common.activate')}
                </button>
                <button onClick={() => del(p.id)}
                  className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400">{t('common.delete')}</button>
              </div>
            </div>
          </div>
        ))}
        {projects.length === 0 && <p className="text-gray-400 dark:text-gray-500 text-center py-8">{t('projects.noProjects')}</p>}
      </div>
    </div>
  );
}
