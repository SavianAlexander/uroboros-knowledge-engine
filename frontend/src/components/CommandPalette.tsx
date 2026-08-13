import React, { useEffect, useState } from 'react';
import { useApp } from '../store/AppContext';
import { Search, X, LayoutDashboard, FolderTree, DatabaseZap, Share2, MessageSquare, Settings2, ShieldCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ViewId } from '../types';

export default function CommandPalette() {
  const { isCommandPaletteOpen, setCommandPaletteOpen, setActiveView } = useApp();
  const [filter, setFilter] = useState('');

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
    setSearchTerm('');
  };

  return (
    <AnimatePresence>
      {isCommandPaletteOpen && (
        <motion.div key="command-palette-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          <motion.div 
            key="command-palette-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-md"
            onClick={() => setCommandPaletteOpen(false)}
          />
          
          <motion.div 
            key="command-palette-dialog"
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            className="relative w-full max-w-xl bg-slate-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col z-10"
          >
            <div className="flex items-center px-4 py-3 border-b border-white/10">
              <Search className="w-5 h-5 text-slate-400 mr-3 shrink-0" />
              <input 
                autoFocus
                type="text" 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Type a command or search workspace..."
                className="flex-1 bg-transparent border-none outline-none text-slate-100 placeholder:text-slate-500 text-sm"
              />
              <button onClick={() => setCommandPaletteOpen(false)} className="p-1 rounded-md hover:bg-white/10 text-slate-400 hover:text-white transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="p-2 space-y-1 max-h-[60vh] overflow-y-auto">
              {filteredCommands.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-slate-500">No commands found matching "{searchTerm}"</div>
              ) : (
                filteredCommands.map((cmd, idx) => {
                  const Icon = cmd.icon;
                  const isSelected = idx === selectedIndex;
                  return (
                    <button
                      key={cmd.id}
                      onClick={() => navigateTo(cmd.id)}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={`w-full text-left px-3 py-2.5 rounded-xl transition-all flex items-center justify-between text-sm ${
                        isSelected 
                          ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' 
                          : 'text-slate-300 hover:bg-white/5'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-indigo-400'}`} />
                        <span className="font-medium">{cmd.title}</span>
                      </div>
                      <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${
                        isSelected ? 'bg-indigo-500/40 border-indigo-400/30 text-indigo-100' : 'bg-slate-800 border-white/5 text-slate-400'
                      }`}>
                        {cmd.category}
                      </span>
                    </button>
                  );
                })
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
