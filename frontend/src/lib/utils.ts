import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Reusable glass panel classes
export const glassClasses = "dark:bg-slate-900/60 bg-white/80 backdrop-blur-xl border dark:border-white/10 border-slate-200 shadow-xl rounded-2xl";
export const glassCardClasses = "dark:bg-slate-800/40 bg-white/80 backdrop-blur-md border dark:border-white/5 border-slate-200 shadow-lg rounded-xl";
export const glassButtonClasses = "dark:bg-white/5 bg-slate-100 dark:hover:bg-white/10 hover:bg-slate-200 border dark:border-white/10 border-slate-200 transition-colors backdrop-blur-sm rounded-lg text-slate-900 dark:text-slate-200";
export const textGradientClasses = "bg-gradient-to-r from-indigo-500 via-cyan-500 to-emerald-500 dark:from-indigo-400 dark:via-cyan-400 dark:to-emerald-400 bg-clip-text text-transparent";
