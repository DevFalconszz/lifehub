import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useT } from '../modules/i18n/store';

const now = new Date();
const currentMonth = now.getMonth() + 1;
const currentYear = now.getFullYear();

export default function Finances() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [budgets, setBudgets] = useState<any[]>([]);
  const [month, setMonth] = useState(currentMonth);
  const [year, setYear] = useState(currentYear);
  const [desc, setDesc] = useState('');
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('expense');
  const [category, setCategory] = useState('');
  const [budgetCat, setBudgetCat] = useState('');
  const [budgetLimit, setBudgetLimit] = useState('');
  const t = useT();

  const load = () => {
    const params = `month=${month}&year=${year}`;
    Promise.all([
      api.listTransactions(params).then((r) => setTransactions(r.data || [])),
      api.getFinanceSummary(month, year).then(setSummary).catch(() => setSummary(null)),
      api.getBudgets(month, year).then((r) => setBudgets(r.data || [])).catch(() => setBudgets([])),
    ]);
  };

  useEffect(() => { load(); }, [month, year]);

  const addTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createTransaction({ description: desc, amount: parseFloat(amount), type, category: category || undefined });
    setDesc('');
    setAmount('');
    setCategory('');
    load();
  };

  const deleteTx = async (id: string) => {
    await api.deleteTransaction(id);
    load();
  };

  const setBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.setBudget({ category: budgetCat || 'general', limit: parseFloat(budgetLimit), month, year });
    setBudgetCat('');
    setBudgetLimit('');
    load();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 dark:text-gray-100">{t('finances.title')}</h1>

      <div className="flex gap-2 items-center mb-6">
        <select value={month} onChange={(e) => setMonth(parseInt(e.target.value))}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
          {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
            <option key={m} value={m}>{new Date(2000, m - 1).toLocaleString('default', { month: 'long' })}</option>
          ))}
        </select>
        <select value={year} onChange={(e) => setYear(parseInt(e.target.value))}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
          {[currentYear - 1, currentYear, currentYear + 1].map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      {summary && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg text-center">
            <p className="text-green-700 dark:text-green-400 text-2xl font-bold">R$ {summary.income?.toFixed(2)}</p>
            <p className="text-sm text-green-600 dark:text-green-400">{t('dashboard.income')}</p>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg text-center">
            <p className="text-red-700 dark:text-red-400 text-2xl font-bold">R$ {summary.expense?.toFixed(2)}</p>
            <p className="text-sm text-red-600 dark:text-red-400">{t('dashboard.expenses')}</p>
          </div>
          <div className={`${summary.balance >= 0 ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-red-50 dark:bg-red-900/20'} p-4 rounded-lg text-center`}>
            <p className={`text-2xl font-bold ${summary.balance >= 0 ? 'text-blue-700 dark:text-blue-400' : 'text-red-700 dark:text-red-400'}`}>
              R$ {summary.balance?.toFixed(2)}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('dashboard.balance')}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h2 className="font-semibold mb-3 dark:text-gray-100">{t('finances.addTransaction')}</h2>
          <form onSubmit={addTransaction} className="space-y-2">
            <input value={desc} onChange={(e) => setDesc(e.target.value)} placeholder={t('finances.description')} required
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
            <input type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder={t('finances.amount')} required
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
            <select value={type} onChange={(e) => setType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100">
              <option value="expense">{t('finances.expense')}</option>
              <option value="income">{t('finances.income')}</option>
            </select>
            <input value={category} onChange={(e) => setCategory(e.target.value)} placeholder={t('finances.category') + ' (' + t('common.optional') + ')'}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
            <button type="submit" className="w-full py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">{t('common.add')}</button>
          </form>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h2 className="font-semibold mb-3 dark:text-gray-100">{t('finances.setBudget')}</h2>
          <form onSubmit={setBudget} className="space-y-2">
            <input value={budgetCat} onChange={(e) => setBudgetCat(e.target.value)} placeholder={t('finances.category') + " ('" + t('finances.general').toLowerCase() + "')"}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
            <input type="number" step="0.01" value={budgetLimit} onChange={(e) => setBudgetLimit(e.target.value)} placeholder={t('finances.limit')} required
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
            <button type="submit" className="w-full py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">{t('finances.setBudget')}</button>
          </form>
          {budgets.length > 0 && (
            <div className="mt-4 space-y-2">
              {budgets.map((b: any) => {
                const spent = transactions.filter((t: any) => t.type === 'expense' && (t.category || 'general') === b.category)
                  .reduce((s: number, t: any) => s + t.amount, 0);
                const pct = b.limit > 0 ? (spent / b.limit) * 100 : 0;
                return (
                  <div key={b.id} className="text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium dark:text-gray-200">{b.category}</span>
                      <span className="dark:text-gray-300">R$ {spent.toFixed(2)} / R$ {b.limit.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-1.5 mt-1">
                      <div className={`h-1.5 rounded-full ${pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                        style={{ width: `${Math.min(pct, 100)}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow mt-6">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-semibold dark:text-gray-100">{t('finances.transactions')}</h2>
        </div>
        {transactions.map((tx: any) => (
          <div key={tx.id} className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50">
            <div>
              <p className="font-medium text-sm dark:text-gray-200">{tx.description}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">{tx.category} &middot; {new Date(tx.date).toLocaleDateString()}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`font-semibold ${tx.type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {tx.type === 'income' ? '+' : '-'}R$ {tx.amount.toFixed(2)}
              </span>
              <button onClick={() => deleteTx(tx.id)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400">{t('common.del')}</button>
            </div>
          </div>
        ))}
        {transactions.length === 0 && <p className="text-center text-gray-400 dark:text-gray-500 py-4">{t('finances.noTransactions')}</p>}
      </div>
    </div>
  );
}
