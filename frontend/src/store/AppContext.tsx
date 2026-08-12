import React, { createContext, useContext, useState, ReactNode } from 'react';
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
  const [activeView, setActiveView] = useState<ViewId>('dashboard');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [searchQuery, setSearchQuery] = useState('');
  const [isCommandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [activeWorkspace, setActiveWorkspace] = useState('Default');

  return (
    <AppContext.Provider value={{
      activeView, setActiveView,
      theme, setTheme,
      searchQuery, setSearchQuery,
      isCommandPaletteOpen, setCommandPaletteOpen,
      activeWorkspace, setActiveWorkspace
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
