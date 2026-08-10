import React, { useEffect } from 'react';
import { useApp } from '../store/AppContext';
import { Search, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ViewId } from '../types';

export default function CommandPalette() {
  const { isCommandPaletteOpen, setCommandPaletteOpen, setActiveView } = useApp();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'p')) {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
      if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setCommandPaletteOpen]);

  const navigateTo = (view: ViewId) => {
    setActiveView(view);
    setCommandPaletteOpen(false);
  };

  return (
    <AnimatePresence>
      {isCommandPaletteOpen && (
        <motion.div key="command-palette-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-white/60 dark:bg-slate-950/60 backdrop-blur-sm"
            onClick={() => setCommandPaletteOpen(false)}
          />
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            className="relative w-full max-w-xl bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
          >
            <div className="flex items-center px-4 py-3 border-b border-slate-200 dark:border-white/5">
              <Search className="w-5 h-5 text-slate-600 dark:text-slate-400 mr-3" />
              <input 
                autoFocus
                type="text" 
                placeholder="Type a command or search..."
                className="flex-1 bg-transparent border-none outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-500"
              />
              <button onClick={() => setCommandPaletteOpen(false)} className="p-1 rounded-md hover:bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400">
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="p-2 space-y-1 max-h-[60vh] overflow-y-auto">
              <div className="px-3 py-1.5 text-xs font-medium text-slate-500">Navigation</div>
              <button onClick={() => navigateTo('dashboard')} className="w-full text-left px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-indigo-100 dark:hover:bg-indigo-500/20 rounded-lg transition-colors">Go to Dashboard</button>
              <button onClick={() => navigateTo('search')} className="w-full text-left px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-indigo-100 dark:hover:bg-indigo-500/20 rounded-lg transition-colors">Go to Explorer</button>
              <button onClick={() => navigateTo('ingestion')} className="w-full text-left px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-indigo-100 dark:hover:bg-indigo-500/20 rounded-lg transition-colors">Open Ingestion Pipeline</button>
              <button onClick={() => navigateTo('chat')} className="w-full text-left px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-indigo-100 dark:hover:bg-indigo-500/20 rounded-lg transition-colors">New AI Chat Session</button>
            </div>
          </motion.div>
          </motion.div>
      )}
    </AnimatePresence>
  );
}
