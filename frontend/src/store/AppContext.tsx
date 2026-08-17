import React, { createContext, useContext, useState, useEffect, useMemo, useCallback, ReactNode } from 'react';
import { ViewId, AppState } from '../types';

interface AppContextType extends AppState {
  setActiveView: (view: ViewId) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setSearchQuery: (query: string) => void;
  setCommandPaletteOpen: (isOpen: boolean) => void;
  setActiveWorkspace: (workspace: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [activeView, setActiveViewState] = useState<ViewId>(() => {
    const hash = window.location.hash.replace(/^#\/?/, '').split('?')[0];
    if (['dashboard', 'workspace', 'search', 'ingestion', 'graph', 'chat', 'config', 'settings', 'architecture'].includes(hash)) {
      return hash as ViewId;
    }
    return 'dashboard';
  });

  const [theme, setThemeState] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('uroboros_theme') as 'dark' | 'light') || 'dark';
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [isCommandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [activeWorkspace, setActiveWorkspaceState] = useState(() => {
    return localStorage.getItem('uroboros_workspace') || 'Default';
  });

  const setActiveView = useCallback((v: ViewId) => {
    setActiveViewState(v);
    window.location.hash = `#/${v}`;
  }, []);

  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.replace(/^#\/?/, '').split('?')[0];
      if (['dashboard', 'workspace', 'search', 'ingestion', 'graph', 'chat', 'config', 'settings', 'architecture'].includes(hash)) {
        setActiveViewState(hash as ViewId);
      }
    };
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, []);

  const setTheme = useCallback((t: 'dark' | 'light') => {
    setThemeState(t);
    localStorage.setItem('uroboros_theme', t);
  }, []);

  const setActiveWorkspace = useCallback((w: string) => {
    setActiveWorkspaceState(w);
    localStorage.setItem('uroboros_workspace', w);
  }, []);

  const contextValue = useMemo(() => ({
    activeView, setActiveView,
    theme, setTheme,
    searchQuery, setSearchQuery,
    isCommandPaletteOpen, setCommandPaletteOpen,
    activeWorkspace, setActiveWorkspace
  }), [
    activeView, setActiveView,
    theme, setTheme,
    searchQuery,
    isCommandPaletteOpen,
    activeWorkspace, setActiveWorkspace
  ]);

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
