import React, { Component, useEffect, useState, useRef, lazy, Suspense } from 'react';
import { AppProvider, useApp } from './store/AppContext';
import { ToastProvider } from './components/Toast';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
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
  error?: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    (this as any).state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('React Error Boundary:', error, errorInfo);
  }

  render() {
    const state = (this as any).state as any;
    if (state?.hasError) {
      return (
        <div className="min-h-screen w-full flex items-center justify-center bg-slate-950 text-slate-100 p-6 font-sans">
          <div className="max-w-md w-full p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mx-auto text-xl font-bold">
              !
            </div>
            <h2 className="text-xl font-semibold text-slate-100 font-serif-claude">Application Workspace Error</h2>
            <p className="text-sm text-slate-400">
              An unexpected render exception occurred. Click retry below to reload the workspace view.
            </p>
            {state.error?.message && (
              <p className="text-xs font-mono text-slate-500 bg-slate-950/50 p-2.5 rounded-lg border border-white/5 break-all text-left">
                {state.error.message}
              </p>
            )}
            <button
              onClick={() => {
                (this as any).setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium text-sm transition-colors shadow-lg shadow-emerald-600/20"
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }
    return (this as any).props.children;
  }
}

function AppLayout() {
  const { activeView, theme } = useApp();
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [isWindowDragging, setIsWindowDragging] = useState(false);
  const dragCounter = useRef(0);

  useEffect(() => {
    const handleAuth = () => setIsAuthenticated(false);
    authEvents.addEventListener('unauthorized', handleAuth);
    return () => authEvents.removeEventListener('unauthorized', handleAuth);
  }, []);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.style.backgroundColor = '#0B0F17';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.backgroundColor = '#f8fafc';
    }
  }, [theme]);

  // Global Window Drag & Drop Listeners
  useEffect(() => {
    const handleDragEnter = (e: DragEvent) => {
      e.preventDefault();
      dragCounter.current += 1;
      if (e.dataTransfer && e.dataTransfer.types.includes('Files')) {
        setIsWindowDragging(true);
      }
    };

    const handleDragLeave = (e: DragEvent) => {
      e.preventDefault();
      dragCounter.current -= 1;
      if (dragCounter.current <= 0) {
        setIsWindowDragging(false);
        dragCounter.current = 0;
      }
    };

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      setIsWindowDragging(false);
      dragCounter.current = 0;
      const files = e.dataTransfer?.files;
      if (files && files.length > 0) {
        window.dispatchEvent(new CustomEvent('neuro:global-drop', { detail: { files } }));
      }
    };

    window.addEventListener('dragenter', handleDragEnter);
    window.addEventListener('dragleave', handleDragLeave);
    window.addEventListener('dragover', handleDragOver);
    window.addEventListener('drop', handleDrop);

    return () => {
      window.removeEventListener('dragenter', handleDragEnter);
      window.removeEventListener('dragleave', handleDragLeave);
      window.removeEventListener('dragover', handleDragOver);
      window.removeEventListener('drop', handleDrop);
    };
  }, []);

  const renderView = () => {
    return (
      <Suspense fallback={
        <div className="flex items-center justify-center h-full text-slate-400 text-sm font-medium gap-2">
          <div className="w-5 h-5 border-2 border-emerald-500/80 border-t-transparent rounded-full animate-spin" />
          <span>Loading Experience...</span>
        </div>
      }>
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
      <div className={`flex h-screen w-full overflow-hidden ${theme === 'dark' ? 'text-slate-200 bg-[#0B0F17]' : 'text-slate-900 bg-slate-50'}`}>
        {/* Ambient atmospheric backdrop (Soft Emerald, Wine Red & Mustard Gold) */}
        {theme === 'dark' ? (
          <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
            {/* Top-Left Emerald Ambient Glow */}
            <div className="absolute -top-[20%] -left-[10%] w-[55%] h-[55%] bg-emerald-950/20 blur-[150px] rounded-full mix-blend-screen animate-ambient-slow" />
            {/* Bottom-Right Deep Wine Red Ambient Glow */}
            <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] bg-rose-950/15 blur-[160px] rounded-full mix-blend-screen animate-ambient-slow" />
            {/* Center-Soft Mustard Gold Warm Glow */}
            <div className="absolute top-[35%] left-[30%] w-[35%] h-[35%] bg-amber-950/10 blur-[170px] rounded-full mix-blend-screen" />
          </div>
        ) : (
          <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
            <div className="absolute -top-[15%] -left-[10%] w-[50%] h-[50%] bg-emerald-100/40 blur-[130px] rounded-full mix-blend-multiply" />
            <div className="absolute -bottom-[15%] -right-[10%] w-[45%] h-[45%] bg-rose-100/30 blur-[140px] rounded-full mix-blend-multiply" />
            <div className="absolute top-[40%] left-[35%] w-[30%] h-[30%] bg-amber-100/30 blur-[150px] rounded-full mix-blend-multiply" />
          </div>
        )}

        <div className="relative z-10 flex h-full w-full">
          <Sidebar />
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            <Header />
            <main className="flex-1 relative overflow-hidden dark:bg-slate-950/30 bg-transparent">
              {renderView()}
            </main>
          </div>
        </div>
        <CommandPalette />

        {/* Global Window Drag-and-Drop Dropzone Overlay */}
        {isWindowDragging && (
          <div className="fixed inset-0 z-50 pointer-events-none flex items-center justify-center p-8 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
            <div className="w-full max-w-2xl p-12 rounded-3xl border-2 border-dashed border-emerald-500/60 bg-emerald-950/20 text-center space-y-4 shadow-2xl">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center mx-auto shadow-lg animate-bounce">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div className="space-y-1">
                <h3 className="text-2xl font-bold font-serif-claude text-slate-100">Drop Documents to Ingest</h3>
                <p className="text-sm text-slate-400">PDF, EPUB, DOCX, Markdown, Audio & Text files will be parsed and vectorized automatically.</p>
              </div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-300">
                <span>HNSW Semantic Index Ready</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default function App() {
  return (
    <AppProvider>
      <ToastProvider>
        <ErrorBoundary>
          <AppLayout />
        </ErrorBoundary>
      </ToastProvider>
    </AppProvider>
  );
}
