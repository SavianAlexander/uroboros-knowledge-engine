import React, { useState } from 'react';
import { useApp } from '../store/AppContext';
import { 
  LayoutDashboard, 
  Search, 
  DatabaseZap, 
  MessageSquare, 
  Settings2, 
  ShieldCheck, 
  Command, 
  Share2, 
  FolderTree, 
  ChevronLeft, 
  ChevronRight,
  Sparkles,
  Layers,
  Database,
  ClipboardCheck
} from 'lucide-react';
import { cn } from '../lib/utils';
import { ViewId } from '../types';

interface NavGroup {
  label: string;
  items: { id: ViewId; label: string; icon: React.ElementType; badge?: string; badgeColor?: 'gold' | 'emerald' | 'wine' }[];
}

export default function Sidebar() {
  const { activeView, setActiveView, setCommandPaletteOpen, activeWorkspace } = useApp();
  const [imgError, setImgError] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  const navGroups: NavGroup[] = [
    {
      label: 'INTELLIGENCE & WORKSPACE',
      items: [
        { id: 'chat', label: 'AI Chat Studio', icon: MessageSquare, badge: 'RAG', badgeColor: 'gold' },
        { id: 'workspace', label: 'Workspace Explorer', icon: FolderTree },
        { id: 'search', label: 'Search & Filtering', icon: Search },
      ]
    },
    {
      label: 'ENGINE & TELEMETRY',
      items: [
        { id: 'dashboard', label: 'System Analytics', icon: LayoutDashboard },
        { id: 'ingestion', label: 'Ingestion Pipeline', icon: DatabaseZap, badge: 'HNSW', badgeColor: 'emerald' },
        { id: 'graph', label: '3D Knowledge Graph', icon: Share2 },
      ]
    },
    {
      label: 'SYSTEM & STRATEGY',
      items: [
        { id: 'architecture', label: 'Architecture & Diagrams', icon: Layers, badge: 'SOC2', badgeColor: 'emerald' },
        { id: 'config', label: 'Processes & Sync', icon: Settings2 },
        { id: 'settings', label: 'System Settings', icon: ShieldCheck },
      ]
    }
  ];

  const getBadgeClass = (color?: 'gold' | 'emerald' | 'wine') => {
    switch (color) {
      case 'gold': return 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30';
      case 'wine': return 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30';
      case 'emerald':
      default: return 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30';
    }
  };

  return (
    <aside className={cn(
      "h-full flex flex-col dark:bg-slate-900/60 bg-white/70 backdrop-blur-xl border-r dark:border-white/5 border-slate-200/80 p-3.5 flex-shrink-0 transition-all duration-300 relative z-20 select-none",
      collapsed ? "w-20 items-center px-2" : "w-64"
    )}>
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-full p-1 text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors z-30 shadow-md hover:scale-105 active:scale-95"
        title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        aria-label="Toggle Sidebar"
      >
        {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      {/* Brand Header */}
      <div className={cn(
        "flex items-center gap-3 mb-6 px-2 w-full pt-1",
        collapsed && "justify-center px-0"
      )}>
        <div className="relative flex items-center justify-center">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-800 flex items-center justify-center shadow-md shadow-emerald-900/30 text-white font-serif font-bold text-lg border border-emerald-400/30">
            {!imgError ? (
              <img 
                src="/assets/uroboros_logo.svg" 
                alt="Uroboros" 
                className="w-5 h-5 object-contain" 
                onError={() => setImgError(true)} 
              />
            ) : (
              <span>U</span>
            )}
          </div>
          <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-white dark:ring-slate-900" />
        </div>

        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-base font-semibold tracking-tight text-slate-900 dark:text-slate-100 font-serif-claude">
              Uroboros
            </span>
            <span className="text-[10px] uppercase font-semibold tracking-widest text-emerald-600 dark:text-emerald-400 -mt-0.5">
              Knowledge Engine
            </span>
          </div>
        )}
      </div>

      {/* Navigation Groups */}
      <nav className="flex-1 space-y-6 w-full overflow-y-auto overflow-x-hidden pr-0.5">
        {navGroups.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1">
            {!collapsed && (
              <h2 className="px-2.5 text-[10px] font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase mb-1">
                {group.label}
              </h2>
            )}
            {group.items.map(item => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium relative group",
                    collapsed && "justify-center px-0 py-2.5",
                    isActive
                      ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-semibold shadow-xs border border-emerald-500/20"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-white/5"
                  )}
                  title={collapsed ? item.label : undefined}
                  data-tab={item.id}
                >
                  <Icon className={cn(
                    "w-4 h-4 shrink-0 transition-transform group-hover:scale-110",
                    isActive ? "text-emerald-600 dark:text-emerald-400" : "text-slate-500 dark:text-slate-400"
                  )} />
                  
                  {!collapsed && (
                    <span className="truncate flex-1 text-left">{item.label}</span>
                  )}

                  {!collapsed && item.badge && (
                    <span className={cn("text-[9px] font-mono px-1.5 py-0.2 rounded-md border", getBadgeClass(item.badgeColor))}>
                      {item.badge}
                    </span>
                  )}

                  {isActive && (
                    <div className="absolute right-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer Controls & Quick Command Palette */}
      <div className="mt-auto pt-3 border-t border-slate-200/80 dark:border-white/5 space-y-2 w-full">
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className={cn(
            "w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-white/5 transition-all text-xs font-medium border border-slate-200/60 dark:border-white/5 bg-slate-50/50 dark:bg-slate-800/20 shadow-xs group",
            collapsed && "justify-center px-0"
          )}
          title="Command Palette (Ctrl+K)"
          data-testid="command-palette-btn"
        >
          <Command className="w-3.5 h-3.5 text-slate-500 group-hover:text-emerald-500 transition-colors shrink-0" />
          {!collapsed && <span className="flex-1 text-left">Command Menu</span>}
          {!collapsed && (
            <kbd className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 text-slate-500 shadow-2xs">
              ⌘K
            </kbd>
          )}
        </button>

        {/* Workspace Quick Status */}
        {!collapsed && (
          <div className="px-3 py-2 rounded-xl bg-slate-100/60 dark:bg-slate-800/40 border border-slate-200/60 dark:border-white/5 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1.5 truncate">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="truncate font-medium">{activeWorkspace || 'Default'}</span>
            </span>
            <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400">v2.4</span>
          </div>
        )}
      </div>
    </aside>
  );
}
