import React, { useState } from 'react';
import { useApp } from '../store/AppContext';
import { LayoutDashboard, Search, DatabaseZap, MessageSquare, Settings2, ShieldCheck, Command, Share2, FolderTree, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '../lib/utils';
import { ViewId } from '../types';

export default function Sidebar() {
  const { activeView, setActiveView, setCommandPaletteOpen, activeWorkspace, setActiveWorkspace } = useApp();
  const [imgError, setImgError] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

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
    <div className={cn(
      "h-full flex flex-col dark:bg-slate-900/40 bg-white/40 backdrop-blur-xl border-r dark:border-white/5 border-slate-200 p-4 flex-shrink-0 transition-all duration-300 relative",
      collapsed ? "w-20 items-center px-2" : "w-64"
    )}>
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-6 bg-slate-900 border border-white/10 rounded-full p-1 text-slate-400 hover:text-white transition-colors z-20 shadow-lg"
        title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
      >
        {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      <div className="flex flex-col gap-2 mb-6 px-2 w-full">
        <div className={cn("flex items-center gap-3", collapsed && "justify-center")}>
          {!imgError && <img src="/assets/uroboros_logo.svg" alt="Uroboros" className="w-8 h-8" onError={() => setImgError(true)} />}
          {!collapsed && <h1 className="text-lg font-semibold tracking-wide text-slate-900 dark:text-slate-100">Uroboros</h1>}
        </div>
        {!collapsed && (
          <select
            value={activeWorkspace}
            onChange={(e) => setActiveWorkspace(e.target.value)}
            className="w-full text-xs px-2 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 focus:outline-none cursor-pointer"
            data-testid="workspace-select"
          >
            <option value="Default">🌐 Default Workspace</option>
            <option value="Personal">👤 Personal Notes</option>
            <option value="Enterprise">🏢 Enterprise Docs</option>
            <option value="Codebase">💻 Source Codebase</option>
          </select>
        )}
      </div>

      <nav className="flex-1 space-y-1 w-full">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-medium",
                collapsed && "justify-center px-0",
                isActive
                  ? "bg-indigo-100 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-white/5"
              )}
              title={collapsed ? item.label : undefined}
              data-tab={item.id}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
              {isActive && !collapsed && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400 dark:shadow-[0_0_8px_rgba(129,140,248,0.8)]" />
              )}
            </button>
          );
        })}
      </nav>

      <div className="mt-auto w-full">
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className={cn(
            "w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-white/5 transition-all text-sm font-medium border dark:border-white/5 border-slate-200 bg-slate-100/50 dark:bg-slate-800/30",
            collapsed && "justify-center px-0"
          )}
          title="Command Palette (Ctrl+K)"
          data-testid="command-palette-btn"
        >
          <Command className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Command Palette</span>}
          {!collapsed && <span className="ml-auto text-xs opacity-50 border border-slate-300 dark:border-white/10 px-1.5 py-0.5 rounded">⌘K</span>}
        </button>
      </div>
    </div>
  );
}
