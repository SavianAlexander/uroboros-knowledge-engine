import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Reusable luxury glass panel & surface classes (Emerald, Slate, Wine Red & Mustard Gold)
export const glassClasses = "dark:bg-slate-900/75 bg-white/90 backdrop-blur-xl border dark:border-white/10 border-slate-200/80 shadow-xl rounded-2xl";
export const glassCardClasses = "dark:bg-slate-900/50 bg-white/85 backdrop-blur-md border dark:border-white/5 border-slate-200/70 shadow-lg rounded-xl transition-all duration-200 hover:border-emerald-500/30 dark:hover:border-emerald-500/30";
export const glassButtonClasses = "dark:bg-white/5 bg-slate-100/80 dark:hover:bg-emerald-500/10 hover:bg-emerald-50 border dark:border-white/10 border-slate-200 hover:border-emerald-500/40 dark:hover:border-emerald-500/40 transition-all backdrop-blur-sm rounded-lg text-slate-800 dark:text-slate-200";

export const emeraldButtonClasses = "bg-emerald-600 hover:bg-emerald-500 text-white font-medium shadow-md shadow-emerald-900/20 hover:shadow-emerald-500/25 transition-all rounded-lg active:scale-[0.98]";
export const goldButtonClasses = "bg-amber-600 hover:bg-amber-500 text-white font-medium shadow-md shadow-amber-900/20 hover:shadow-amber-500/25 transition-all rounded-lg active:scale-[0.98]";
export const wineButtonClasses = "bg-rose-900 hover:bg-rose-800 text-white font-medium shadow-md shadow-rose-950/20 hover:shadow-rose-800/25 transition-all rounded-lg active:scale-[0.98]";

export const emeraldBadgeClasses = "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 px-2.5 py-0.5 rounded-full text-xs font-medium";
export const goldBadgeClasses = "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 px-2.5 py-0.5 rounded-full text-xs font-medium";
export const wineBadgeClasses = "bg-rose-950/40 text-rose-400 dark:text-rose-300 border border-rose-800/30 px-2.5 py-0.5 rounded-full text-xs font-medium";
export const slateBadgeClasses = "bg-slate-100 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/5 px-2.5 py-0.5 rounded-full text-xs font-medium";

export const textGradientClasses = "bg-gradient-to-r from-emerald-500 via-teal-400 to-amber-400 dark:from-emerald-400 dark:via-teal-300 dark:to-amber-300 bg-clip-text text-transparent";

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
