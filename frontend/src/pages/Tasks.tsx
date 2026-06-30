import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useT } from '../modules/i18n/store';

const statuses = ['todo', 'in_progress', 'done', 'cancelled'];
const priorities = ['low', 'medium', 'high', 'urgent'];

export default function Tasks() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [projectId, setProjectId] = useState('');
  const [priority, setPriority] = useState('medium');
  const t = useT();

  const load = () => Promise.all([
    api.listTasks().then((r) => setTasks(r.data || [])),
    api.listProjects().then((r) => setProjects(r.data || [])),
  ]);

  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;
    await api.createTask({ title, project_id: projectId, priority });
    setTitle('');
    load();
  };

  const updateStatus = async (t: any, status: string) => {
    await api.updateTask(t.project_id, t.id, { status });
    load();
  };

  const del = async (t: any) => {
    await api.deleteTask(t.project_id, t.id);
    load();
  };

  const statusDot = (s: string) => {
    const colors: Record<string, string> = { todo: 'bg-gray-300 dark:bg-gray-600', in_progress: 'bg-blue-500', done: 'bg-green-500', cancelled: 'bg-red-300 dark:bg-red-700' };
    return <span className={`w-2 h-2 rounded-full ${colors[s] || 'bg-gray-300'} inline-block mr-2`} />;
  };

  const priorityBadge = (p: string) => {
    const colors: Record<string, string> = {
      low: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300',
      medium: 'bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300',
      high: 'bg-orange-100 dark:bg-orange-900/40 text-orange-800 dark:text-orange-300',
      urgent: 'bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300',
    };
    return <span className={`text-xs px-1.5 py-0.5 rounded ${colors[p]}`}>{p}</span>;
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 dark:text-gray-100">{t('tasks.title')}</h1>

      <form onSubmit={create} className="flex gap-2 mb-6 flex-wrap">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder={t('tasks.taskTitle')} required
          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm min-w-[200px] bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100" />
        <select value={projectId} onChange={(e) => setProjectId(e.target.value)} required
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
          <option value="">{t('tasks.selectProject')}</option>
          {projects.filter((p) => p.status === 'active').map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <select value={priority} onChange={(e) => setPriority(e.target.value)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
          {priorities.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">{t('common.add')}</button>
      </form>

      <div className="space-y-2">
        {tasks.map((task) => {
          const project = projects.find((p) => p.id === task.project_id);
          return (
            <div key={task.id} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow flex items-center justify-between">
              <div className="flex items-center gap-3">
                {statusDot(task.status)}
                <div>
                  <span className={`${task.status === 'done' ? 'line-through text-gray-400 dark:text-gray-500' : 'font-medium dark:text-gray-100'}`}>{task.title}</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-400 dark:text-gray-500">{project?.name}</span>
                    {priorityBadge(task.priority)}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <select value={task.status} onChange={(e) => updateStatus(task, e.target.value)}
                  className="text-xs border border-gray-300 dark:border-gray-600 rounded px-1 py-0.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100">
                  {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
                <button onClick={() => del(task)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 ml-2">{t('common.del')}</button>
              </div>
            </div>
          );
        })}
        {tasks.length === 0 && <p className="text-gray-400 dark:text-gray-500 text-center py-8">{t('tasks.noTasks')}</p>}
      </div>
    </div>
  );
}
