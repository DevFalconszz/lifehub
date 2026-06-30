import { create } from 'zustand';

type Theme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
  toggle: () => void;
  setTheme: (t: Theme) => void;
}

const stored = (typeof window !== 'undefined' ? localStorage.getItem('theme') : null) as Theme | null;
const prefersDark = typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches;
const initial: Theme = stored || (prefersDark ? 'dark' : 'light');

if (typeof document !== 'undefined') {
  if (initial === 'dark') document.documentElement.classList.add('dark');
  else document.documentElement.classList.remove('dark');
}

export const useThemeStore = create<ThemeState>()((set) => ({
  theme: initial,
  toggle: () =>
    set((state) => {
      const next = state.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', next);
      if (next === 'dark') document.documentElement.classList.add('dark');
      else document.documentElement.classList.remove('dark');
      return { theme: next };
    }),
  setTheme: (t) => {
    localStorage.setItem('theme', t);
    if (t === 'dark') document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
    set({ theme: t });
  },
}));
