import React, { useEffect } from 'react';
import { AppProvider, useApp } from './store/AppContext';
import Sidebar from './components/Sidebar';
import CommandPalette from './components/CommandPalette';
import DashboardView from './views/DashboardView';
import WorkspaceView from './views/WorkspaceView';
import SearchView from './views/SearchView';
import IngestionView from './views/IngestionView';
import GraphView from './views/GraphView';
import ChatView from './views/ChatView';
import ConfigView from './views/ConfigView';
import SettingsView from './views/SettingsView';

function AppLayout() {
  const { activeView, theme } = useApp();

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.style.backgroundColor = '#020617';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.backgroundColor = '#f1f5f9';
    }
  }, [theme]);

  const renderView = () => {
    switch (activeView) {
      case 'dashboard': return <DashboardView />;
      case 'workspace': return <WorkspaceView />;
      case 'search': return <SearchView />;
      case 'ingestion': return <IngestionView />;
      case 'graph': return <GraphView />;
      case 'chat': return <ChatView />;
      case 'config': return <ConfigView />;
      case 'settings': return <SettingsView />;
      default: return <DashboardView />;
    }
  };

  return (
    <div className={`flex h-screen w-full overflow-hidden font-sans ${theme === 'dark' ? 'text-slate-200 bg-slate-950' : 'text-slate-900 bg-slate-50'}`} style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      {theme === 'dark' ? (
        <div className="fixed inset-0 pointer-events-none z-0">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-900/20 blur-[120px] rounded-full mix-blend-screen" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-900/20 blur-[120px] rounded-full mix-blend-screen" />
        </div>
      ) : (
        <div className="fixed inset-0 pointer-events-none z-0">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-100/50 blur-[120px] rounded-full mix-blend-multiply" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-100/50 blur-[120px] rounded-full mix-blend-multiply" />
        </div>
      )}
      <div className="relative z-10 flex h-full w-full">
        <Sidebar />
        <main className="flex-1 relative overflow-hidden dark:bg-slate-950/20 bg-transparent">
          {renderView()}
        </main>
      </div>
      <CommandPalette />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppLayout />
    </AppProvider>
  );
}
