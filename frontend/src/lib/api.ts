import { cachedFetch } from './cache';

const BASE_URL = '/api';

export const authEvents = new EventTarget();

const getAuthHeaders = () => {
  const key = localStorage.getItem('uroboros_api_key');
  const ws = localStorage.getItem('uroboros_workspace') || 'Default';
  return {
    ...(key ? { 'Authorization': `Bearer ${key}` } : {}),
    'X-Workspace': ws
  };
};

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const method = options?.method || 'GET';

  const doFetch = async () => {
    let res: Response;
    const customHeaders: Record<string, string> = {};
    if (options?.headers) {
      if (options.headers instanceof Headers) {
        options.headers.forEach((value, key) => { customHeaders[key] = value; });
      } else if (Array.isArray(options.headers)) {
        options.headers.forEach(([key, value]) => { customHeaders[key] = value; });
      } else {
        Object.assign(customHeaders, options.headers);
      }
    }

    try {
      res = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
          ...customHeaders,
        },
      });
    } catch (e) {
      throw new Error('Network error or server unreachable');
    }

    if (res.status === 401 || res.status === 403) {
      authEvents.dispatchEvent(new Event('unauthorized'));
    }

    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`);
    }

    let data;
    try {
      data = await res.json();
    } catch (e) {
      throw new Error('Malformed JSON response');
    }
    return data;
  };

  if (method === 'GET') {
    return cachedFetch(endpoint, doFetch, 3000); // 3-second deduplication
  }
  return doFetch();
}

export const api = {
  fetchAPI: fetchAPI,
  // Health & Stats
  health: () => fetchAPI<any>('/health'),
  stats: () => fetchAPI<any>('/stats'),

  // Dashboard Analytics
  storage: () => fetchAPI<any>('/analytics/storage'),
  tags: () => fetchAPI<any>('/analytics/tags'),
  searchActivity: () => fetchAPI<any>('/analytics/search-activity'),
  recentSearches: () => fetchAPI<any>('/search/history'),
  fileTree: () => fetchAPI<any>('/file/tree'),

  // Vector Engine
  vectorMetrics: () => fetchAPI<any>('/vector/metrics'),
  unifiedVectorSearch: (query: string, limit: number = 10, mode?: string) =>
    fetchAPI<any>(`/vector/search/unified?query=${encodeURIComponent(query)}&limit=${limit}${mode ? `&mode=${mode}` : ''}`),

  // Search
  search: (query: string, mode: string, threshold: number) =>
    fetchAPI<any>(`/search?query=${encodeURIComponent(query)}&mode=${mode}&threshold=${threshold}`),
  autocomplete: (prefix: string) =>
    fetchAPI<any>(`/search/autocomplete?prefix=${encodeURIComponent(prefix)}`),
  validateQuery: (query: string) =>
    fetchAPI<any>('/search/validate', { method: 'POST', body: JSON.stringify({ query }) }),

  // Graph
  graphData: () => fetchAPI<any>('/graph/data'),
  graphWikilinks: () => fetchAPI<any>('/graph/wikilinks'),
  graphClusters: () => fetchAPI<any>('/graph/clusters'),

  // Chat & RAG
  chatSessions: () => fetchAPI<any[]>('/chat/sessions'),
  getChatSession: (id: string) => fetchAPI<any>(`/chat/sessions/${id}`),
  createChatSession: (title: string) =>
    fetchAPI<any>('/chat/sessions', { method: 'POST', body: JSON.stringify({ title }) }),
  deleteChatSession: (id: string) =>
    fetchAPI<any>(`/chat/sessions/${id}`, { method: 'DELETE' }),
  ragStream: (message: string, session_id?: string, options?: RequestInit & { web_search?: boolean; temperature?: number; model?: string }) => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json', ...getAuthHeaders() };
    if (options?.headers) {
      if (options.headers instanceof Headers) {
        options.headers.forEach((v, k) => { headers[k] = v; });
      } else if (Array.isArray(options.headers)) {
        options.headers.forEach(([k, v]) => { headers[k] = v; });
      } else {
        Object.assign(headers, options.headers);
      }
    }
    const { web_search, temperature, model, ...fetchOptions } = options || {};
    return fetch(`${BASE_URL}/chat/stream`, {
      method: 'POST',
      ...fetchOptions,
      headers,
      body: JSON.stringify({ message, session_id, web_search, temperature, model })
    });
  },


  // Files
  fileRaw: (path: string) => fetchAPI<any>(`/file/raw?path=${encodeURIComponent(path)}`),
  fileInsights: (path: string) => fetchAPI<any>(`/file/insights?path=${encodeURIComponent(path)}`),
  pdfInfo: (path: string) => fetchAPI<any>(`/file/pdf/info?path=${encodeURIComponent(path)}`),
  fileEntities: (path: string) => fetchAPI<any>(`/file/entities?path=${encodeURIComponent(path)}`),
  termInsight: (term: string, context?: string, path?: string) =>
    fetchAPI<any>('/intelligence/term-insight', { method: 'POST', body: JSON.stringify({ term, context, path }) }),
  upload: (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return fetch(`${BASE_URL}/upload`, { method: 'POST', headers: { ...getAuthHeaders() }, body: fd }).then(r => r.json());
  },
  deleteFile: (filepath: string) =>
    fetchAPI<any>('/file/delete', { method: 'POST', body: JSON.stringify({ filepath }) }),
  renameFile: (filepath: string, new_name: string) =>
    fetchAPI<any>('/file/rename', { method: 'POST', body: JSON.stringify({ filepath, new_name }) }),

  // Tags
  addTag: (filepath: string, tag: string) =>
    fetchAPI<any>('/file/tag', { method: 'POST', body: JSON.stringify({ filepath, tag }) }),
  removeTag: (filepath: string, tag: string) =>
    fetchAPI<any>('/file/tag', { method: 'DELETE', body: JSON.stringify({ filepath, tag }) }),
  suggestedTags: (filepath: string) =>
    fetchAPI<any>(`/suggested_tags?path=${encodeURIComponent(filepath)}`),

  // Config & Processes
  rules: () => fetchAPI<any>('/rules'),
  createRule: (rule: any) => fetchAPI<any>('/rules', { method: 'POST', body: JSON.stringify(rule) }),
  testRulePreview: (rule: any) => fetchAPI<any>('/rules/test-preview', { method: 'POST', body: JSON.stringify(rule) }),
  synonyms: () => fetchAPI<any>('/synonyms'),
  macros: () => fetchAPI<any>('/macros'),
  aliases: () => fetchAPI<any>('/aliases'),
  syncPeers: () => fetchAPI<any>('/sync/peers'),
  addSyncPeer: (url: string, name: string) => fetchAPI<any>('/sync/peers', { method: 'POST', body: JSON.stringify({ url, name }) }),
  syncExchange: (peer_url: string) =>
    fetchAPI<any>('/sync/exchange', { method: 'POST', body: JSON.stringify({ peer_url }) }),
  syncLogs: () => fetchAPI<any>('/sync/logs'),
  
  // Workflows
  workflowTriggers: () => fetchAPI<any>('/workflows/triggers'),
  createWorkflowTrigger: (trigger: any) => fetchAPI<any>('/workflows/triggers', { method: 'POST', body: JSON.stringify(trigger) }),
  deleteWorkflowTrigger: (id: number) => fetchAPI<any>(`/workflows/triggers/${id}`, { method: 'DELETE' }),
  triggerWorkflowEvent: (event: any) => fetchAPI<any>('/workflows/trigger-event', { method: 'POST', body: JSON.stringify(event) }),
  workflowLogs: () => fetchAPI<any>('/workflows/logs'),

  // Snapshots
  snapshots: () => fetchAPI<any>('/snapshots'),
  captureSnapshot: () => fetchAPI<any>('/snapshots', { method: 'POST' }),
  restoreSnapshot: (timestamp: string) =>
    fetchAPI<any>('/snapshots/restore', { method: 'POST', body: JSON.stringify({ timestamp }) }),
  deleteSnapshot: (timestamp: string) =>
    fetchAPI<any>(`/snapshots/${timestamp}`, { method: 'DELETE' }),

  // Settings
  systemEnv: () => fetchAPI<any>('/system/env'),
  indexDirectory: (directory: string) =>
    fetchAPI<any>('/index', { method: 'POST', body: JSON.stringify({ directory }) }),

  // Bookmarks
  bookmarks: () => fetchAPI<any>('/bookmarks'),
  addBookmark: (query: string, label: string) =>
    fetchAPI<any>('/bookmarks/add', { method: 'POST', body: JSON.stringify({ query, label }) }),
  deleteBookmark: (id: number) =>
    fetchAPI<any>(`/bookmarks/delete`, { method: 'POST', body: JSON.stringify({ id }) }),

  // Export
  exportCSV: () => fetch(`${BASE_URL}/export`, { headers: { ...getAuthHeaders() } }).then(r => r.blob()),
  exportPDF: () => fetch(`${BASE_URL}/report/export`, { headers: { ...getAuthHeaders() } }).then(r => r.blob()),

  // Notes
  getNotes: (filepath: string) => fetchAPI<any>(`/notes?path=${encodeURIComponent(filepath)}`),
  saveNote: (filepath: string, content: string) =>
    fetchAPI<any>('/notes', { method: 'POST', body: JSON.stringify({ filepath, content }) }),

  // System Maintenance, Backup, GraphML Export & Benchmark
  systemMaintenance: () => fetchAPI<any>('/system/maintenance', { method: 'POST' }),
  systemBackup: () => fetchAPI<any>('/system/backup', { method: 'POST' }),
  listBackups: () => fetchAPI<any>('/system/backups'),
  searchBenchmark: (query: string = 'accounting standards') => fetchAPI<any>(`/search/benchmark?query=${encodeURIComponent(query)}`),
  exportGraphML: () => fetch(`${BASE_URL}/graph/export`, { headers: { ...getAuthHeaders() } }).then(r => r.blob()),
  exportVaultJSON: () => fetchAPI<any>('/export/vault/json'),
};
