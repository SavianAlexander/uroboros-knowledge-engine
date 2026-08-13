import React, { Component, useEffect, useState, lazy, Suspense } from 'react';
import { AppProvider, useApp } from './store/AppContext';
import Sidebar from './components/Sidebar';
import CommandPalette from './components/CommandPalette';
import DashboardView from './views/DashboardView';
import { authEvents } from './lib/api';

const WorkspaceView = lazy(() => import('./views/WorkspaceView'));
const SearchView = lazy(() => import('./views/SearchView'));
const IngestionView = lazy(() => import('./views/IngestionView'));
const GraphView = lazy(() => import('./views/GraphView'));
const ChatView = lazy(() => import('./views/ChatView'));
const ConfigView = lazy(() => import('./views/ConfigView'));
const SettingsView = lazy(() => import('./views/SettingsView'));
const LoginView = lazy(() => import('./views/LoginView'));

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    (this as any).state = { hasError: false };
  }

  static getDerivedStateFromError(_: Error): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('React Error Boundary:', error, errorInfo);
  }

  render() {
    const state = (this as any).state as ErrorBoundaryState;
    if (state?.hasError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Something went wrong</h2>
          <button onClick={() => (this as any).setState({ hasError: false })}>Retry</button>
        </div>
      );
    }
    return (this as any).props.children;
  }
}

function AppLayout() {
  const { activeView, theme } = useApp();
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Assume true until 401

  useEffect(() => {
    const handleAuth = () => setIsAuthenticated(false);
    authEvents.addEventListener('unauthorized', handleAuth);
    return () => authEvents.removeEventListener('unauthorized', handleAuth);
  }, []);

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
    return (
      <Suspense fallback={<div className="flex items-center justify-center h-full text-slate-400 text-sm font-medium">Loading View...</div>}>
        {(() => {
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
        })()}
      </Suspense>
    );
  };

  return (
    <>
      {!isAuthenticated && <LoginView onLogin={() => { setIsAuthenticated(true); window.location.reload(); }} />}
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
    </>
  );
}

export default function App() {
  return (
    <AppProvider>
      <ErrorBoundary>
        <AppLayout />
      </ErrorBoundary>
    </AppProvider>
  );
}
