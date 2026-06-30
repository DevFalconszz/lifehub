import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { useT } from '../modules/i18n/store';

export default function Dashboard() {
  const [data, setData] = useState<any>({});
  const t = useT();

  useEffect(() => {
    Promise.all([
      api.listProjects(),
      api.listTasks(),
      api.listNotes(),
      api.listTransactions('month=6&year=2026'),
      api.listEvents(),
      api.listReadings(),
      api.getFinanceSummary(6, 2026).catch(() => null),
    ]).then(([projects, tasks, notes, transactions, events, readings, summary]) => {
      setData({ projects, tasks, notes, transactions, events, readings, summary });
    });
  }, []);

  const cards = [
    { label: t('nav.projects'), value: data.projects?.data?.length ?? 0, path: '/projects', color: 'bg-blue-500' },
    { label: t('nav.tasks'), value: data.tasks?.data?.length ?? 0, path: '/tasks', color: 'bg-green-500' },
    { label: t('nav.notes'), value: data.notes?.data?.length ?? 0, path: '/notes', color: 'bg-purple-500' },
    { label: t('nav.finances'), value: data.transactions?.data?.length ?? 0, path: '/finances', color: 'bg-yellow-500' },
    { label: t('nav.calendar'), value: data.events?.data?.length ?? 0, path: '/calendar', color: 'bg-pink-500' },
    { label: t('nav.readings'), value: data.readings?.data?.length ?? 0, path: '/readings', color: 'bg-indigo-500' },
  ];

  const summary = data.summary;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 dark:text-gray-100">{t('dashboard.title')}</h1>

      <div className="grid grid-cols-3 gap-4 mb-8">
        {cards.map((card) => (
          <Link key={card.label} to={card.path}
            className={`${card.color} text-white p-4 rounded-lg hover:opacity-90 transition`}>
            <p className="text-3xl font-bold">{card.value}</p>
            <p className="text-sm opacity-80">{card.label}</p>
          </Link>
        ))}
      </div>

      {summary && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow mb-6">
          <h2 className="font-semibold mb-3 dark:text-gray-100">{t('dashboard.monthlySummary')}</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-green-600 dark:text-green-400 text-2xl font-bold">R$ {summary.income?.toFixed(2)}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard.income')}</p>
            </div>
            <div>
              <p className="text-red-600 dark:text-red-400 text-2xl font-bold">R$ {summary.expense?.toFixed(2)}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard.expenses')}</p>
            </div>
            <div>
              <p className={`text-2xl font-bold ${summary.balance >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                R$ {summary.balance?.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard.balance')}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {data.tasks?.data && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <h2 className="font-semibold mb-2 dark:text-gray-100">{t('dashboard.recentTasks')}</h2>
            {data.tasks.data.slice(0, 5).map((t: any) => (
              <div key={t.id} className="flex items-center gap-2 py-1 text-sm">
                <span className={`w-2 h-2 rounded-full ${t.status === 'done' ? 'bg-green-500' : t.priority === 'high' ? 'bg-red-500' : 'bg-gray-300 dark:bg-gray-600'}`} />
                <span className={`${t.status === 'done' ? 'line-through text-gray-400 dark:text-gray-500' : 'dark:text-gray-200'}`}>{t.title}</span>
              </div>
            ))}
          </div>
        )}

        {data.events?.data && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <h2 className="font-semibold mb-2 dark:text-gray-100">{t('dashboard.upcomingEvents')}</h2>
            {data.events.data.slice(0, 5).map((e: any) => (
              <div key={e.id} className="py-1 text-sm">
                <p className="font-medium dark:text-gray-200">{e.title}</p>
                <p className="text-gray-500 dark:text-gray-400 text-xs">{new Date(e.start_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
