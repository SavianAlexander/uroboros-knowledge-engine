import React, { useState, useEffect } from 'react';
import { useApp } from '../store/AppContext';
import { Search, Moon, Sun, Plus, ShieldCheck, Sparkles, Database, Layers, CheckCircle2 } from 'lucide-react';
import { api } from '../lib/api';

export default function Header() {
  const { 
    activeView, 
    setActiveView, 
    theme, 
    setTheme, 
    setCommandPaletteOpen, 
    activeWorkspace, 
    setActiveWorkspace 
  } = useApp();

  const [systemHealthy, setSystemHealthy] = useState<boolean>(true);
  const [docCount, setDocCount] = useState<number | null>(null);

  useEffect(() => {
    api.health()
      .then(res => setSystemHealthy(res?.status === 'ok' || res?.status === 'healthy' || !res?.status?.includes('Error')))
      .catch(() => setSystemHealthy(false));

    api.stats()
      .then(res => setDocCount(res?.total_files || null))
      .catch(() => {});
  }, [activeWorkspace]);

  const viewTitles: Record<string, { title: string; subtitle: string }> = {
    dashboard: { title: 'System Analytics', subtitle: 'Real-time telemetry & operational overview' },
    workspace: { title: 'Workspace Explorer', subtitle: 'Hierarchical file tree & document workstation' },
    search: { title: 'Search & Discovery', subtitle: 'Hybrid RRF, vector similarity & FTS5 full-text' },
    ingestion: { title: 'Ingestion Pipeline', subtitle: 'Live document parsing & HNSW vectorization' },
    graph: { title: 'Knowledge Graph', subtitle: '3D conceptual network & semantic entity mapping' },
    chat: { title: 'AI Chat Studio', subtitle: 'RAG conversational intelligence & live artifacts' },
    config: { title: 'Processes & Strategy', subtitle: 'Database snapshots, P2P sync & token strategies' },
    settings: { title: 'System Settings', subtitle: 'Provider credentials, maintenance & security' },
  };

  const currentMeta = viewTitles[activeView] || { title: 'Workspace', subtitle: 'Uroboros Knowledge Engine' };

  return (
    <header className="h-16 border-b border-slate-200/80 dark:border-white/5 bg-white/60 dark:bg-slate-900/60 backdrop-blur-xl px-6 flex items-center justify-between flex-shrink-0 z-30 transition-colors">
      {/* Left: View Title & Subtitle */}
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-base font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude tracking-tight">
            {currentMeta.title}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
            {currentMeta.subtitle}
          </p>
        </div>
      </div>

      {/* Center: Command Palette Trigger */}
      <div className="flex-1 max-w-md mx-6 hidden md:block">
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100/70 dark:bg-slate-800/40 hover:bg-slate-200/60 dark:hover:bg-slate-800/80 text-slate-500 dark:text-slate-400 text-xs transition-all shadow-sm group"
        >
          <span className="flex items-center gap-2.5">
            <Search className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform" />
            <span>Search docs, vault files, or type a command...</span>
          </span>
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-white dark:bg-slate-700/60 border border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-300 shadow-xs">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right: Workspace badge, Health, Theme Toggle, Actions */}
      <div className="flex items-center gap-3">
        {/* Workspace Pill */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-xs text-emerald-800 dark:text-emerald-300 font-medium">
          <Database className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          <span>{activeWorkspace || 'Default Vault'}</span>
          {docCount !== null && (
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono">
              {docCount} docs
            </span>
          )}
        </div>

        {/* Live Engine Status Pulse */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-white/5 text-xs">
          <span className={`w-2 h-2 rounded-full ${systemHealthy ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]'}`} />
          <span className="text-slate-600 dark:text-slate-300 text-[11px] font-medium hidden sm:inline">
            {systemHealthy ? 'Engine Online' : 'Degraded'}
          </span>
        </div>

        {/* Quick New Chat Button */}
        {activeView !== 'chat' && (
          <button
            onClick={() => setActiveView('chat')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-sm transition-all hover:shadow-emerald-600/20 active:scale-95"
            title="Start new AI conversation"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New Chat</span>
          </button>
        )}

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-lg border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
          aria-label="Toggle Theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
        </button>
      </div>
    </header>
  );
}
