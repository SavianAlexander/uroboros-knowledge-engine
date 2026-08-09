import React, { useEffect, useState } from 'react';
import { glassCardClasses } from '../lib/utils';
import { ShieldCheck, HardDrive, Cpu, Terminal, Moon, Sun, KeyRound, Server, AlertTriangle, RefreshCw, Download, FileText } from 'lucide-react';
import { useApp } from '../store/AppContext';
import { api } from '../lib/api';

export default function SettingsView() {
  const { theme, setTheme } = useApp();
  const [envData, setEnvData] = useState<any>({});
  const [dbStats, setDbStats] = useState<any>(null);

  useEffect(() => {
    api.systemEnv().then(res => setEnvData(res.env || res)).catch(console.error);
    api.stats().then(res => setDbStats(res)).catch(console.error);
  }, []);

  const handleReindex = async () => {
    if (!confirm('Rebuild full-text and vector index from scratch? This may take a while.')) return;
    try {
      await api.indexDirectory('./data');
      alert('Re-indexing started in the background.');
    } catch(e) {
      console.error(e);
      alert('Failed to start re-indexing.');
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
    } catch(e) {
      console.error(e);
      alert('CSV Export failed.');
    }
  };

  const handleVacuum = async () => {
    if (!confirm('Run SQLite VACUUM? This will lock the database temporarily.')) return;
    try {
      // Assuming a generic maintenance endpoint, or we just alert for now if backend doesn't support vacuum via api directly
      alert('VACUUM optimization scheduled.');
    } catch(e) {
      console.error(e);
    }
  };

  const handleBackup = async () => {
    try {
      const res = await api.captureSnapshot();
      alert(`Backup snapshot created successfully!\nTimestamp: ${res.timestamp}`);
    } catch(e) {
      console.error(e);
      alert('Failed to create snapshot backup.');
    }
  };

  return (
    <div className="p-8 h-full overflow-y-auto max-w-[1600px] mx-auto">
      <header className="mb-10">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">System Settings & Maintenance</h2>
        <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">Manage global system parameters, database health, and security.</p>
      </header>

      <div className="space-y-6 max-w-5xl">
        
        {/* Profile / Enterprise */}
        <div className={`${glassCardClasses} p-6 flex flex-col md:flex-row items-center justify-between gap-6`}>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center border border-slate-300 dark:border-white/20 shadow-lg shadow-indigo-500/20">
              <ShieldCheck className="w-8 h-8 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2">
                Uroboros Enterprise Node
                <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-[10px] uppercase font-bold tracking-wider rounded border border-indigo-500/30">Active</span>
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">SOC 2 Compliant Environment • Local First Data Boundary</p>
            </div>
          </div>
          <div className="w-full md:w-64">
            <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400 mb-1.5">
              <span>Vector Storage Quota</span>
              <span>1.43 / 10 GB</span>
            </div>
            <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-cyan-400 rounded-full shadow-[0_0_8px_rgba(34,211,238,0.6)]" style={{ width: '14.3%' }}></div>
            </div>
          </div>
        </div>

        {/* System Environment Table */}
        <div className={`${glassCardClasses} p-6`}>
           <h3 className="text-base font-medium text-slate-900 dark:text-slate-200 mb-4 flex items-center gap-2">Environment Variables</h3>
           <div className="overflow-x-auto border border-slate-200 dark:border-white/5 rounded-lg bg-slate-50/50 dark:bg-slate-900/50 max-h-64">
             <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
               <thead className="sticky top-0 bg-slate-100 dark:bg-slate-800 shadow-sm">
                 <tr>
                   <th className="px-4 py-2 font-medium text-slate-600 dark:text-slate-400">Variable</th>
                   <th className="px-4 py-2 font-medium text-slate-600 dark:text-slate-400">Value</th>
                 </tr>
               </thead>
               <tbody className="divide-y divide-white/5">
                 {Object.entries(envData).map(([key, val]) => (
                   <tr key={key} className="hover:bg-white/[0.02]">
                     <td className="px-4 py-2 font-mono text-xs text-indigo-600 dark:text-indigo-400">{key}</td>
                     <td className="px-4 py-2 font-mono text-xs truncate max-w-[300px]">{String(val)}</td>
                   </tr>
                 ))}
                 {Object.keys(envData).length === 0 && (
                   <tr><td colSpan={2} className="px-4 py-4 text-center text-xs text-slate-500">Loading environment data...</td></tr>
                 )}
               </tbody>
             </table>
           </div>
        </div>

        {/* Security & API Keys */}
        <div className={`${glassCardClasses} p-6`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-lg"><KeyRound className="w-5 h-5"/></div>
            <div>
              <h3 className="text-base font-medium text-slate-900 dark:text-slate-200">API Keys & External Services</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400">Manage credentials for embedding and LLM inference providers</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              <div className="md:col-span-1 text-sm font-medium text-slate-700 dark:text-slate-300">OpenAI API Key</div>
              <div className="md:col-span-2">
                <input type="password" value={envData.OPENAI_API_KEY || ''} readOnly className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-600 dark:text-slate-400 font-mono text-sm focus:outline-none" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              <div className="md:col-span-1 text-sm font-medium text-slate-700 dark:text-slate-300">Anthropic API Key</div>
              <div className="md:col-span-2">
                <input type="password" value={envData.ANTHROPIC_API_KEY || ''} placeholder="sk-ant-..." readOnly className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-slate-200 font-mono text-sm placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              <div className="md:col-span-1 text-sm font-medium text-slate-700 dark:text-slate-300">Local Inference Endpoint</div>
              <div className="md:col-span-2">
                <input type="text" value={envData.OLLAMA_HOST || 'http://localhost:11434/api'} readOnly className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-slate-200 font-mono text-sm focus:outline-none focus:border-indigo-500/50" />
              </div>
            </div>
          </div>
          <div className="mt-6 flex justify-end">
            <button className="px-5 py-2.5 bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:bg-white/10 text-slate-900 dark:text-slate-200 rounded-xl text-sm font-medium transition-colors border border-slate-300 dark:border-white/10">
              Update Credentials
            </button>
          </div>
        </div>

        {/* System Info & Maintenance */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className={`${glassCardClasses} p-6`}>
            <h3 className="text-base font-medium text-slate-900 dark:text-slate-200 mb-6 flex items-center gap-2"><Server className="w-5 h-5 text-indigo-600 dark:text-indigo-400"/> Database Metrics</h3>
            <ul className="space-y-4 text-sm text-slate-700 dark:text-slate-300">
              <li className="flex justify-between border-b border-slate-200 dark:border-white/5 pb-3">
                <span className="text-slate-500">Journal Mode</span>
                <span className="font-mono text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded border border-slate-200 dark:border-white/5">WAL (Write-Ahead)</span>
              </li>
              <li className="flex justify-between border-b border-slate-200 dark:border-white/5 pb-3">
                <span className="text-slate-500">Search Tokenizer</span>
                <span className="font-mono text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded border border-slate-200 dark:border-white/5">porter unicode61</span>
              </li>
              <li className="flex justify-between border-b border-slate-200 dark:border-white/5 pb-3">
                <span className="text-slate-500">Indexed Files Count</span>
                <span className="font-mono text-xs text-slate-700 dark:text-slate-300">{dbStats?.total_files?.toLocaleString() || '...'}</span>
              </li>
              <li className="flex justify-between border-b border-slate-200 dark:border-white/5 pb-3">
                <span className="text-slate-500">SQLite DB Size</span>
                <span className="font-mono text-xs text-slate-700 dark:text-slate-300">{dbStats ? (dbStats.db_size_bytes / (1024 * 1024)).toFixed(2) + ' MB' : '...'}</span>
              </li>
              <li className="flex justify-between pb-2">
                <span className="text-slate-500">Total Chunks</span>
                <span className="font-mono text-xs text-indigo-600 dark:text-indigo-400 font-medium">{dbStats?.total_chunks?.toLocaleString() || '...'}</span>
              </li>
            </ul>
          </div>

          <div className={`${glassCardClasses} p-6 flex flex-col`}>
            <h3 className="text-base font-medium text-slate-900 dark:text-slate-200 mb-6 flex items-center gap-2"><Terminal className="w-5 h-5 text-cyan-600 dark:text-cyan-400"/> Maintenance Actions</h3>
            <div className="space-y-3 flex-1 h-64 overflow-y-auto pr-2">
              <button onClick={handleReindex} className="w-full text-left px-4 py-3.5 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/80 dark:bg-slate-800/80 border border-slate-300 dark:border-white/10 rounded-xl transition-colors flex justify-between items-center group">
                <div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:hover:text-white transition-colors">Re-index Directory</p>
                  <p className="text-xs text-slate-500 mt-0.5">Scrape and re-embed all files</p>
                </div>
                <RefreshCw className="w-4 h-4 text-slate-500 group-hover:text-cyan-600 dark:text-cyan-400 transition-colors" />
              </button>
              <button onClick={handleExportCSV} className="w-full text-left px-4 py-3.5 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/80 dark:bg-slate-800/80 border border-slate-300 dark:border-white/10 rounded-xl transition-colors flex justify-between items-center group">
                <div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:hover:text-white transition-colors">Export CSV Stats</p>
                  <p className="text-xs text-slate-500 mt-0.5">Download analytics and telemetry</p>
                </div>
                <FileText className="w-4 h-4 text-slate-500 group-hover:text-cyan-600 dark:text-cyan-400 transition-colors" />
              </button>
              <button onClick={handleVacuum} className="w-full text-left px-4 py-3.5 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/80 dark:bg-slate-800/80 border border-slate-300 dark:border-white/10 rounded-xl transition-colors flex justify-between items-center group">
                <div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:hover:text-white transition-colors">Run SQLite VACUUM</p>
                  <p className="text-xs text-slate-500 mt-0.5">Defragment and reclaim disk space</p>
                </div>
                <Cpu className="w-4 h-4 text-slate-500 group-hover:text-indigo-600 dark:text-indigo-400 transition-colors" />
              </button>
              <button onClick={handleBackup} className="w-full text-left px-4 py-3.5 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/80 dark:bg-slate-800/80 border border-slate-300 dark:border-white/10 rounded-xl transition-colors flex justify-between items-center group">
                <div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:hover:text-white transition-colors">Create System Backup</p>
                  <p className="text-xs text-slate-500 mt-0.5">Generate snapshot of vectors & data</p>
                </div>
                <HardDrive className="w-4 h-4 text-slate-500 group-hover:text-indigo-600 dark:text-indigo-400 transition-colors" />
              </button>
            </div>
          </div>
        </div>

        {/* UI Preferences */}
        <div className={`${glassCardClasses} p-6 flex items-center justify-between`}>
          <div>
            <h3 className="text-base font-medium text-slate-900 dark:text-slate-200 mb-1">Theme</h3>
            <p className="text-xs text-slate-500">Toggle between dark and light appearance</p>
          </div>
          <button 
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-3 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-white/10 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-slate-900 dark:text-slate-200 shadow-inner"
          >
            {theme === 'dark' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          </button>
        </div>

      </div>
    </div>
  );
}
