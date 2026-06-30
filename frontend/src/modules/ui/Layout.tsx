import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../auth/store';
import { setToken } from '../../api/client';
import { useThemeStore } from '../theme/store';
import { useLangStore, useT } from '../i18n/store';
import { languages } from '../i18n/translations';

const navItems = [
  { path: '/', key: 'dashboard', icon: '◉' },
  { path: '/projects', key: 'projects', icon: '◈' },
  { path: '/tasks', key: 'tasks', icon: '📋' },
  { path: '/notes', key: 'notes', icon: '📝' },
  { path: '/finances', key: 'finances', icon: '💰' },
  { path: '/calendar', key: 'calendar', icon: '📅' },
  { path: '/readings', key: 'readings', icon: '📚' },
  { path: '/ai', key: 'ai', icon: '🤖' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { theme, toggle } = useThemeStore();
  const { lang, setLang } = useLangStore();
  const t = useT();

  const handleLogout = () => {
    setToken(null);
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <aside className="w-60 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-xl font-bold text-primary-600">{t('app.name')}</h1>
        </div>

        <nav className="flex-1 p-2 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === item.path
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {t(`nav.${item.key}`)}
            </Link>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              {t('common.settings')}
            </span>
          </div>

          <div className="flex items-center justify-between px-1">
            <span className="text-xs text-gray-500 dark:text-gray-400">{t('common.theme')}</span>
            <button onClick={toggle}
              className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition">
              {theme === 'light' ? '☀️ ' + t('common.light') : '🌙 ' + t('common.dark')}
            </button>
          </div>

          <div className="flex items-center justify-between px-1">
            <span className="text-xs text-gray-500 dark:text-gray-400">{t('common.language')}</span>
            <select value={lang} onChange={(e) => setLang(e.target.value as any)}
              className="text-xs px-1 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border-0 cursor-pointer">
              {languages.map((l) => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="text-sm">
              <p className="font-medium text-gray-900 dark:text-gray-100">{user?.name}</p>
              <p className="text-gray-500 dark:text-gray-400 text-xs">{user?.email}</p>
            </div>
            <button onClick={handleLogout}
              className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400">
              {t('auth.logout')}
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  );
}
