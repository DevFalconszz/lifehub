import { useMemo } from 'react';

interface CalendarEvent {
  id: string;
  title: string;
  start_at: string;
  end_at?: string;
  all_day: boolean;
}

interface Props {
  year: number;
  month: number;
  events: CalendarEvent[];
  selectedDate: string | null;
  onSelect: (dateStr: string) => void;
  onMonthChange: (year: number, month: number) => void;
}

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function buildCalendar(year: number, month: number) {
  const first = new Date(year, month - 1, 1);
  const last = new Date(year, month, 0);
  const startDay = first.getDay();
  const daysInMonth = last.getDate();
  const daysInPrev = new Date(year, month - 1, 0).getDate();

  const cells: { day: number; monthOffset: number }[] = [];

  for (let i = startDay - 1; i >= 0; i--) {
    cells.push({ day: daysInPrev - i, monthOffset: -1 });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d, monthOffset: 0 });
  }
  const remaining = 42 - cells.length;
  for (let d = 1; d <= remaining; d++) {
    cells.push({ day: d, monthOffset: 1 });
  }

  return cells;
}

function toDateStr(year: number, month: number, day: number) {
  return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

export default function CalendarGrid({ year, month, events, selectedDate, onSelect, onMonthChange }: Props) {
  const cells = useMemo(() => buildCalendar(year, month), [year, month]);

  const eventsByDate = useMemo(() => {
    const map = new Map<string, CalendarEvent[]>();
    for (const ev of events) {
      const d = new Date(ev.start_at);
      const key = toDateStr(d.getFullYear(), d.getMonth() + 1, d.getDate());
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(ev);
    }
    return map;
  }, [events]);

  const todayStr = toDateStr(new Date().getFullYear(), new Date().getMonth() + 1, new Date().getDate());

  const prev = () => {
    if (month === 1) onMonthChange(year - 1, 12);
    else onMonthChange(year, month - 1);
  };
  const next = () => {
    if (month === 12) onMonthChange(year + 1, 1);
    else onMonthChange(year, month + 1);
  };

  const monthName = new Date(year, month - 1).toLocaleString('default', { month: 'long' });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <button onClick={prev} className="px-2 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
          &larr;
        </button>
        <h2 className="font-semibold text-lg dark:text-gray-100 capitalize">
          {monthName} {year}
        </h2>
        <button onClick={next} className="px-2 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
          &rarr;
        </button>
      </div>

      <div className="grid grid-cols-7 gap-1 text-center mb-2">
        {weekDays.map((d) => (
          <div key={d} className="text-xs font-medium text-gray-500 dark:text-gray-400 py-1">{d}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {cells.map((cell, i) => {
          const dateStr = toDateStr(
            cell.monthOffset === 0 ? year : cell.monthOffset === -1 && month === 1 ? year - 1 : cell.monthOffset === 1 && month === 12 ? year + 1 : year,
            cell.monthOffset === 0 ? month : cell.monthOffset === -1 && month === 1 ? 12 : cell.monthOffset === -1 ? month - 1 : cell.monthOffset === 1 && month === 12 ? 1 : month + 1,
            cell.day,
          );
          const isToday = dateStr === todayStr;
          const isSelected = dateStr === selectedDate;
          const isOtherMonth = cell.monthOffset !== 0;
          const dayEvents = eventsByDate.get(dateStr) || [];
          const hasEvent = dayEvents.length > 0;

          return (
            <button
              key={i}
              onClick={() => onSelect(dateStr)}
              className={`relative flex flex-col items-center justify-center py-1.5 rounded-lg text-sm transition-colors
                ${isOtherMonth ? 'text-gray-300 dark:text-gray-600' : 'text-gray-900 dark:text-gray-100'}
                ${isSelected ? 'bg-primary-100 dark:bg-primary-900/40 ring-2 ring-primary-500' : ''}
                ${!isSelected && isToday ? 'bg-blue-50 dark:bg-blue-900/20 font-bold' : ''}
                ${!isSelected && !isToday && !isOtherMonth ? 'hover:bg-gray-100 dark:hover:bg-gray-700' : ''}
              `}
            >
              <span>{cell.day}</span>
              {hasEvent && (
                <span className="flex gap-0.5 mt-0.5">
                  {dayEvents.slice(0, 3).map((_, ei) => (
                    <span key={ei} className="w-1 h-1 rounded-full bg-primary-500" />
                  ))}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
