import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useT } from '../modules/i18n/store';
import CalendarGrid from '../modules/ui/CalendarGrid';

export default function Calendar() {
  const [events, setEvents] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [startAt, setStartAt] = useState('');
  const [endAt, setEndAt] = useState('');
  const [description, setDescription] = useState('');
  const [allDay, setAllDay] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const t = useT();

  const load = () => api.listEvents().then((r) => setEvents(r.data || []));

  useEffect(() => { load(); }, []);

  const selectedEvents = selectedDate
    ? events.filter((ev) => {
        const d = new Date(ev.start_at);
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
        return key === selectedDate;
      })
    : [];

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const data = { title, description: description || undefined, start_at: new Date(startAt).toISOString(), end_at: endAt ? new Date(endAt).toISOString() : undefined, all_day: allDay };
    if (editId) {
      await api.updateEvent(editId, data);
      setEditId(null);
    } else {
      await api.createEvent(data);
    }
    setTitle('');
    setDescription('');
    setStartAt('');
    setEndAt('');
    setAllDay(false);
    load();
  };

  const edit = (ev: any) => {
    setEditId(ev.id);
    setTitle(ev.title);
    setDescription(ev.description || '');
    setStartAt(new Date(ev.start_at).toISOString().slice(0, 16));
    setEndAt(ev.end_at ? new Date(ev.end_at).toISOString().slice(0, 16) : '');
    setAllDay(ev.all_day);
  };

  const del = async (id: string) => {
    await api.deleteEvent(id);
    if (editId === id) { setEditId(null); setTitle(''); setDescription(''); setStartAt(''); setEndAt(''); setAllDay(false); }
    load();
  };

  const handleSelectDate = (dateStr: string) => {
    setSelectedDate(dateStr);
    setStartAt(`${dateStr}T00:00`);
    setEndAt('');
    setAllDay(false);
    setEditId(null);
    setTitle('');
    setDescription('');
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 dark:text-gray-100">{t('calendar.title')}</h1>

      <div className="mb-6">
        <CalendarGrid
          year={year}
          month={month}
          events={events}
          selectedDate={selectedDate}
          onSelect={handleSelectDate}
          onMonthChange={(y, m) => { setYear(y); setMonth(m); }}
        />
      </div>

      <form onSubmit={submit} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6 space-y-3">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder={t('calendar.eventTitle')} required
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder={t('calendar.description')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 resize-none" />
        <div className="grid grid-cols-2 gap-2">
          <input type="datetime-local" value={startAt} onChange={(e) => setStartAt(e.target.value)} required
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
          <input type="datetime-local" value={endAt} onChange={(e) => setEndAt(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
        </div>
        <label className="flex items-center gap-2 text-sm dark:text-gray-300">
          <input type="checkbox" checked={allDay} onChange={(e) => setAllDay(e.target.checked)}
            className="accent-primary-600" />
          {t('calendar.allDay')}
        </label>
        <div className="flex gap-2">
          <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">
            {editId ? t('common.update') : t('common.create')}
          </button>
          {editId && <button type="button" onClick={() => { setEditId(null); setTitle(''); setDescription(''); setStartAt(''); setEndAt(''); setAllDay(false); }}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg text-sm">{t('common.cancel')}</button>}
        </div>
      </form>

      {selectedDate && (
        <div className="mb-4">
          <h3 className="font-semibold text-sm text-gray-500 dark:text-gray-400 mb-2">
            {new Date(selectedDate + 'T12:00:00').toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </h3>
          {selectedEvents.length === 0 && (
            <p className="text-gray-400 dark:text-gray-500 text-sm py-2">{t('calendar.noEvents')}</p>
          )}
          <div className="space-y-2">
            {selectedEvents.map((ev: any) => (
              <div key={ev.id} className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow flex items-center justify-between">
                <div>
                  <p className="font-medium dark:text-gray-100">{ev.title}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {ev.all_day ? t('calendar.allDay') : `${new Date(ev.start_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${ev.end_at ? new Date(ev.end_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}`}
                  </p>
                  {ev.description && (
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 line-clamp-2">{ev.description}</p>
                  )}
                </div>
                <div className="flex gap-1">
                  <button onClick={() => edit(ev)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-primary-600 dark:hover:text-primary-400">{t('common.edit')}</button>
                  <button onClick={() => del(ev.id)} className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400">{t('common.del')}</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
