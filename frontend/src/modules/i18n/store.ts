import { create } from 'zustand';
import { translations, type Lang } from './translations';
import type { Translations } from './translations';

const stored = (typeof window !== 'undefined' ? localStorage.getItem('lang') : null) as Lang | null;
const initial: Lang = stored || 'en';

export const useLangStore = create<{
  lang: Lang;
  t: () => Translations;
  setLang: (l: Lang) => void;
}>()((set, get) => ({
  lang: initial,
  t: () => translations[get().lang] || translations.en,
  setLang: (l) => {
    localStorage.setItem('lang', l);
    set({ lang: l });
  },
}));

export function useT() {
  const lang = useLangStore((s) => s.lang);
  return (path: string) => {
    const keys = path.split('.');
    let obj: any = translations[lang] || translations.en;
    for (const key of keys) {
      if (obj && typeof obj === 'object' && key in obj) obj = obj[key];
      else return path;
    }
    return typeof obj === 'string' ? obj : path;
  };
}
