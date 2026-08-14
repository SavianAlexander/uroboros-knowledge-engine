import React, { useEffect, useState } from 'react';
import { glassCardClasses, emeraldButtonClasses, emeraldBadgeClasses, goldBadgeClasses, wineBadgeClasses } from '../lib/utils';
import { ShieldCheck, HardDrive, Cpu, Terminal, Moon, Sun, KeyRound, Server, AlertTriangle, RefreshCw, Download, FileText, Sparkles, Database } from 'lucide-react';
import { useToast } from '../components/Toast';
import { api } from '../lib/api';
import { useApp } from '../store/AppContext';

export default function SettingsView() {
  const { toast } = useToast();
  const { theme, setTheme } = useApp();
  const [envData, setEnvData] = useState<any>({});
  const [dbStats, setDbStats] = useState<any>(null);

  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [ollamaHost, setOllamaHost] = useState('');

  useEffect(() => {
    const savedOpenAI = localStorage.getItem('uroboros_openai_key') || '';
    const savedAnthropic = localStorage.getItem('uroboros_anthropic_key') || '';
    const savedOllama = localStorage.getItem('uroboros_ollama_host') || '';

    if (savedOpenAI) setOpenaiKey(savedOpenAI);
    if (savedAnthropic) setAnthropicKey(savedAnthropic);
    if (savedOllama) setOllamaHost(savedOllama);

    api.systemEnv().then(res => {
      const data = res.env || res;
      setEnvData(data);
      if (data.OPENAI_API_KEY && !savedOpenAI) setOpenaiKey(data.OPENAI_API_KEY);
      if (data.ANTHROPIC_API_KEY && !savedAnthropic) setAnthropicKey(data.ANTHROPIC_API_KEY);
      if (data.OLLAMA_HOST && !savedOllama) setOllamaHost(data.OLLAMA_HOST);
    }).catch(console.error);

    api.stats().then(res => setDbStats(res)).catch(console.error);
  }, []);

  const handleReindex = async () => {
    toast('Re-indexing Scheduled', 'Rebuilding vector indices in background', 'info');
    try {
      await api.indexDirectory('./data');
      toast('Re-indexing Started', 'Scanning database vault', 'success');
    } catch(e: any) {
      toast('Re-indexing Error', e.message || 'Operation failed', 'error');
    }
  };

  const handleExportCSV = async () => {
    try {
      const blob = await api.exportCSV();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'uroboros_stats_export.csv';
      a.click();
      window.URL.revokeObjectURL(url);
      toast('CSV Exported', 'Telemetry stats saved to CSV', 'info');
    } catch(e: any) {
      toast('Export Failed', e.message || 'CSV export failed', 'error');
    }
  };

  const handleVacuum = async () => {
    try {
      await api.systemMaintenance();
      toast('VACUUM Complete', 'SQLite pages defragmented successfully', 'success');
    } catch(e) {
      console.error(e);
      toast('VACUUM Failed', 'Database maintenance failed', 'error');
    }
  };

  const handleBackup = async () => {
    try {
      const res = await api.captureSnapshot();
      toast('Backup Complete', `Snapshot: ${res.timestamp || 'Created'}`, 'success');
    } catch(e: any) {
      toast('Backup Failed', e.message || 'Snapshot error', 'error');
    }
  };

  const handleUpdateCredentials = () => {
    localStorage.setItem('uroboros_openai_key', openaiKey);
    localStorage.setItem('uroboros_anthropic_key', anthropicKey);
    localStorage.setItem('uroboros_ollama_host', ollamaHost);
    toast('Credentials Saved', 'LLM Provider keys persisted to user settings', 'success');
  };

  return (
    <div className="p-8 h-full overflow-y-auto max-w-[1600px] mx-auto space-y-6 font-sans">
      <header className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">
          Platform Settings & Security
        </h2>
        <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">
          Manage API keys, local Ollama endpoints, database vacuuming, and system theme preferences.
        </p>
      </header>

      <div className="space-y-6 max-w-5xl">
        {/* LLM API Credentials */}
        <div className={`${glassCardClasses} p-6 space-y-5`}>
          <div className="flex justify-between items-center border-b border-slate-200/80 dark:border-white/10 pb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
                <KeyRound className="w-4 h-4 text-emerald-500" /> AI Provider API Credentials
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Configure cloud and local neural reasoning engines.</p>
            </div>
            <button
              onClick={handleUpdateCredentials}
              className={`px-4 py-1.5 ${emeraldButtonClasses} text-xs font-semibold`}
            >
              Save Credentials
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                Anthropic API Key (Claude Sonnet / Opus)
              </label>
              <input
                type="password"
                value={anthropicKey}
                onChange={(e) => setAnthropicKey(e.target.value)}
                placeholder="sk-ant-api03-..."
                className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3.5 py-2 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50 font-mono shadow-2xs"
              />
            </div>

            <div>
              <label className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                OpenAI API Key (GPT-4o / Embeddings)
              </label>
              <input
                type="password"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-proj-..."
                className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3.5 py-2 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50 font-mono shadow-2xs"
              />
            </div>

            <div>
              <label className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                Local Ollama Host Endpoint
              </label>
              <input
                type="text"
                value={ollamaHost || 'http://127.0.0.1:11434'}
                onChange={(e) => setOllamaHost(e.target.value)}
                placeholder="http://127.0.0.1:11434"
                className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3.5 py-2 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50 font-mono shadow-2xs"
              />
            </div>
          </div>
        </div>

        {/* Database Operations & Maintenance */}
        <div className={`${glassCardClasses} p-6 space-y-5`}>
          <div className="border-b border-slate-200/80 dark:border-white/10 pb-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
              <Database className="w-4 h-4 text-teal-500" /> Database Integrity & Maintenance
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Execute low-level SQLite WAL optimizations and vacuuming routines.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={handleVacuum}
              className="p-4 bg-slate-100/70 dark:bg-slate-900/60 hover:bg-emerald-500/10 hover:border-emerald-500/40 border border-slate-200/80 dark:border-white/10 rounded-xl text-left transition-all group shadow-2xs"
            >
              <div className="p-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg w-fit mb-2 group-hover:scale-110 transition-transform">
                <RefreshCw className="w-4 h-4" />
              </div>
              <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">VACUUM & Clean</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">Reclaim fragmented disk pages.</p>
            </button>

            <button
              onClick={handleBackup}
              className="p-4 bg-slate-100/70 dark:bg-slate-900/60 hover:bg-teal-500/10 hover:border-teal-500/40 border border-slate-200/80 dark:border-white/10 rounded-xl text-left transition-all group shadow-2xs"
            >
              <div className="p-2 bg-teal-500/10 text-teal-600 dark:text-teal-400 rounded-lg w-fit mb-2 group-hover:scale-110 transition-transform">
                <HardDrive className="w-4 h-4" />
              </div>
              <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">Snapshot Backup</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">Create an atomic database backup.</p>
            </button>

            <button
              onClick={handleExportCSV}
              className="p-4 bg-slate-100/70 dark:bg-slate-900/60 hover:bg-amber-500/10 hover:border-amber-500/40 border border-slate-200/80 dark:border-white/10 rounded-xl text-left transition-all group shadow-2xs"
            >
              <div className="p-2 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-lg w-fit mb-2 group-hover:scale-110 transition-transform">
                <Download className="w-4 h-4" />
              </div>
              <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">Export CSV Dump</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">Export all telemetry metrics.</p>
            </button>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="p-6 rounded-2xl border border-rose-500/30 bg-rose-500/5 dark:bg-rose-950/20 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-semibold text-xs uppercase tracking-wider font-serif-claude">
            <AlertTriangle className="w-4 h-4" /> Danger Zone
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">Re-index Entire Knowledge Vault</p>
              <p className="text-[11px] text-slate-500 mt-0.5">Drop and regenerate all HNSW embeddings and FTS5 indices.</p>
            </div>
            <button
              onClick={handleReindex}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-rose-600/20 transition-colors"
            >
              Rebuild All Indices
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
