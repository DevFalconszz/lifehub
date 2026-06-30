import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, setToken } from '../api/client';
import { useAuthStore } from '../modules/auth/store';
import { useT } from '../modules/i18n/store';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const t = useT();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.register({ name, email, password });
      setToken(res.access_token);
      setUser(res.user);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-center mb-6 text-primary-600">{t('app.name')}</h1>
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('auth.register')}</h2>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <input type="text" placeholder={t('auth.name')} value={name} required
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500" />
          <input type="email" placeholder={t('auth.email')} value={email} required
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500" />
          <input type="password" placeholder={t('auth.password')} value={password} required
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500" />
          <button type="submit"
            className="w-full py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
            {t('auth.registerBtn')}
          </button>
          <p className="text-sm text-center text-gray-500 dark:text-gray-400">
            {t('auth.signInLink')} <Link to="/login" className="text-primary-600">{t('auth.signInHere')}</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
