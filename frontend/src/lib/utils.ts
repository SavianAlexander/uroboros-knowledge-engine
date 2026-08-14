import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Reusable luxury glass panel & surface classes (Soothing Emerald, Warm Charcoal Slate, Wine Red & Mustard Gold)
export const glassClasses = "dark:bg-slate-900/70 bg-white/90 backdrop-blur-xl border dark:border-white/[0.07] border-slate-200/80 shadow-xl rounded-2xl";
export const glassCardClasses = "dark:bg-slate-900/50 bg-white/85 backdrop-blur-md border dark:border-white/[0.06] border-slate-200/70 shadow-sm rounded-2xl transition-all duration-200 hover:border-slate-700/60 dark:hover:border-white/12";
export const glassButtonClasses = "dark:bg-white/5 bg-slate-100/80 dark:hover:bg-white/10 hover:bg-slate-200/60 border dark:border-white/10 border-slate-200 hover:border-slate-400 dark:hover:border-white/20 transition-all backdrop-blur-sm rounded-xl text-slate-700 dark:text-slate-200";

export const emeraldButtonClasses = "bg-emerald-600 hover:bg-emerald-500 text-emerald-950 font-semibold shadow-xs transition-all rounded-xl active:scale-[0.98]";
export const goldButtonClasses = "bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold shadow-xs transition-all rounded-xl active:scale-[0.98]";
export const wineButtonClasses = "bg-rose-600 hover:bg-rose-500 text-white font-semibold shadow-xs transition-all rounded-xl active:scale-[0.98]";

export const emeraldBadgeClasses = "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300/90 border border-emerald-500/20 px-2.5 py-0.5 rounded-full text-xs font-medium tracking-wide";
export const goldBadgeClasses = "bg-amber-500/10 text-amber-700 dark:text-amber-300/90 border border-amber-500/20 px-2.5 py-0.5 rounded-full text-xs font-medium tracking-wide";
export const wineBadgeClasses = "bg-rose-500/10 text-rose-700 dark:text-rose-300/90 border border-rose-500/20 px-2.5 py-0.5 rounded-full text-xs font-medium tracking-wide";
export const slateBadgeClasses = "bg-slate-100 dark:bg-slate-800/60 text-slate-600 dark:text-slate-300 border border-slate-200/80 dark:border-white/5 px-2.5 py-0.5 rounded-full text-xs font-medium tracking-wide";

export const textGradientClasses = "bg-gradient-to-r from-emerald-400 via-teal-300 to-amber-300 bg-clip-text text-transparent";

// ponytail: zero-dependency debounce helper with optional leading edge support
export function debounce<T extends (...args: any[]) => void>(func: T, wait: number, immediate: boolean = false): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  return function(...args: Parameters<T>) {
    const callNow = immediate && !timeout;
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => {
      timeout = null;
      if (!immediate) func(...args);
    }, wait);
    if (callNow) func(...args);
  };
}
