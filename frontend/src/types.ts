export type ViewId = 'dashboard' | 'workspace' | 'search' | 'ingestion' | 'graph' | 'chat' | 'config' | 'settings' | 'architecture';

export interface AppState {
  activeView: ViewId;
  theme: 'dark' | 'light';
  searchQuery: string;
  isCommandPaletteOpen: boolean;
  activeWorkspace: string;
}

// API Types
export interface HealthStats {
  status: string;
  uptime: string;
  version: string;
}

export interface StorageAnalytics {
  distribution: { mime: string; bytes: number }[];
  totalBytes: number;
}

export interface FileNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
  mime?: string;
}

export interface SearchResult {
  id: string;
  filename: string;
  path: string;
  mime: string;
  score: number;
  snippet: string;
  tags: string[];
  size: number;
  date: string;
}

export interface GraphNode {
  id: string;
  label: string;
  category: string;
}

export interface GraphLink {
  source: string;
  target: string;
  type: string;
}

export interface ChatSession {
  id: string;
  title: string;
  updatedAt: string;
  messages?: any[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ title?: string; path?: string; url?: string; snippet?: string; citation?: string; confidence_score?: number }>;
  metrics?: {
    model?: string;
    tier?: string;
    tokens_generated?: number;
    tokens_per_sec?: number;
    duration_sec?: number;
  };
}

