import React from 'react';
import { useApp } from '../store/AppContext';
import { LayoutDashboard, Search, DatabaseZap, MessageSquare, Settings2, ShieldCheck, Command, Share2, FolderTree } from 'lucide-react';
import { cn } from '../lib/utils';
import { ViewId } from '../types';

export default function Sidebar() {
  const { activeView, setActiveView, setCommandPaletteOpen } = useApp();
  const [imgError, setImgError] = React.useState(false);

  const navItems: { id: ViewId; label: string; icon: React.ElementType }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'workspace', label: 'Workspace', icon: FolderTree },
    { id: 'search', label: 'Explorer', icon: Search },
    { id: 'ingestion', label: 'Ingestion', icon: DatabaseZap },
    { id: 'graph', label: 'Graph', icon: Share2 },
    { id: 'chat', label: 'AI Chat', icon: MessageSquare },
    { id: 'config', label: 'Processes', icon: Settings2 },
    { id: 'settings', label: 'System', icon: ShieldCheck },
  ];

  return (
    <div className="w-64 h-full flex flex-col dark:bg-slate-900/40 bg-white/40 backdrop-blur-xl border-r dark:border-white/5 border-slate-200 p-4 flex-shrink-0">
      <div className="flex items-center gap-3 mb-8 px-2">
        {!imgError && <img src="/assets/uroboros_logo.svg" alt="Uroboros" className="w-8 h-8" onError={() => setImgError(true)} />}
        <h1 className="text-lg font-semibold tracking-wide text-slate-900 dark:text-slate-100">Uroboros</h1>
      </div>

      <nav className="flex-1 space-y-1">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-medium",
                isActive
                  ? "bg-indigo-100 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-white/5"
              )}
              data-tab={item.id}
            >
              <Icon className="w-4 h-4" />
              {item.label}
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400 dark:shadow-[0_0_8px_rgba(129,140,248,0.8)]" />
              )}
            </button>
          );
        })}
      </nav>

      <div className="mt-auto">
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-white/5 transition-all text-sm font-medium border dark:border-white/5 border-slate-200 bg-slate-100/50 dark:bg-slate-800/30"
          data-testid="command-palette-btn"
        >
          <Command className="w-4 h-4" />
          <span>Command Palette</span>
          <span className="ml-auto text-xs opacity-50 border border-slate-300 dark:border-white/10 px-1.5 py-0.5 rounded">⌘K</span>
        </button>
      </div>
    </div>
  );
}
