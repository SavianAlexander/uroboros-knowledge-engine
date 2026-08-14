import React, { useEffect, useState } from 'react';
import { useApp } from '../store/AppContext';
import { Search, X, LayoutDashboard, FolderTree, DatabaseZap, Share2, MessageSquare, Settings2, ShieldCheck, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ViewId } from '../types';

interface CommandItem {
  id: ViewId;
  title: string;
  category: string;
  icon: React.ElementType;
}

export default function CommandPalette() {
  const { isCommandPaletteOpen, setCommandPaletteOpen, setActiveView } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const commands: CommandItem[] = [
    { id: 'dashboard', title: 'Open Analytics & Telemetry', category: 'Overview', icon: LayoutDashboard },
    { id: 'workspace', title: 'Open Document & PDF Studio', category: 'Workspace', icon: FolderTree },
    { id: 'search', title: 'Semantic Search & Discovery', category: 'Search', icon: Search },
    { id: 'chat', title: 'AI Assistant & Split Canvas', category: 'Intelligence', icon: MessageSquare },
    { id: 'ingestion', title: 'File Ingestion & Neural Pipeline', category: 'Data', icon: DatabaseZap },
    { id: 'graph', title: '3D Knowledge Graph Cluster', category: 'Visualization', icon: Share2 },
    { id: 'config', title: 'Workflow Rules & Orchestration', category: 'System', icon: Settings2 },
    { id: 'settings', title: 'Platform Settings & Snapshots', category: 'System', icon: ShieldCheck },
  ];

  const filteredCommands = commands.filter(cmd =>
    cmd.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cmd.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [searchTerm]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'p')) {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
      if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
      }
      if (isCommandPaletteOpen) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setSelectedIndex(prev => (prev + 1) % (filteredCommands.length || 1));
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % (filteredCommands.length || 1));
        } else if (e.key === 'Enter' && filteredCommands[selectedIndex]) {
          e.preventDefault();
          navigateTo(filteredCommands[selectedIndex].id);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandPaletteOpen, setCommandPaletteOpen, filteredCommands, selectedIndex]);

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
            className="absolute inset-0 bg-black/70 backdrop-blur-md"
            onClick={() => setCommandPaletteOpen(false)}
          />
          
          <motion.div 
            key="command-palette-dialog"
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 1, y: 0 }}
            className="relative w-full max-w-xl bg-slate-900/95 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col z-10 font-sans"
          >
            <div className="flex items-center px-4 py-3.5 border-b border-slate-800">
              <Search className="w-4 h-4 text-emerald-400 mr-3 shrink-0" />
              <input 
                autoFocus
                type="text" 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Jump to a view or command (e.g. chat, graph, search)..."
                className="flex-1 bg-transparent border-none outline-none text-slate-100 placeholder:text-slate-500 text-xs font-sans"
              />
              <button onClick={() => setCommandPaletteOpen(false)} className="p-1 rounded-md hover:bg-white/10 text-slate-400 hover:text-white transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="p-2 space-y-1 max-h-[60vh] overflow-y-auto">
              {filteredCommands.length === 0 ? (
                <div className="px-4 py-8 text-center text-xs text-slate-500 font-sans">No matching commands found</div>
              ) : (
                filteredCommands.map((cmd, idx) => {
                  const Icon = cmd.icon;
                  const isSelected = idx === selectedIndex;
                  return (
                    <button
                      key={cmd.id}
                      onClick={() => navigateTo(cmd.id)}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={`w-full text-left px-3.5 py-2.5 rounded-xl transition-all flex items-center justify-between text-xs ${
                        isSelected 
                          ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/20 font-semibold' 
                          : 'text-slate-300 hover:bg-white/5'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-emerald-400'}`} />
                        <span className="font-serif-claude text-sm">{cmd.title}</span>
                      </div>
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${
                        isSelected ? 'bg-emerald-500/40 border-emerald-400/40 text-emerald-100' : 'bg-slate-800 border-white/5 text-slate-400'
                      }`}>
                        {cmd.category}
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            <div className="px-4 py-2 bg-slate-950/80 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span>Navigate with ↑ ↓ and Enter</span>
              <span>ESC to dismiss</span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
