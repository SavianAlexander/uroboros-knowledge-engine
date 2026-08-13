import React, { useState } from 'react';
import { api } from '../lib/api';
import { glassCardClasses } from '../lib/utils';
import { Wrench, Database, Download, Gauge, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { useToast } from './Toast';

export default function SystemControlsCard() {
  const { toast } = useToast();
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);
  const [benchmarkResult, setBenchmarkResult] = useState<any>(null);

  const handleMaintenance = async () => {
    setLoadingAction('maintenance');
    setMessage(null);
    try {
      const res = await api.systemMaintenance();
      setMessage({ text: res.message || 'Database maintenance completed successfully.', type: 'success' });
      toast('Defrag & Clean Complete', res.message || 'WAL checkpointed successfully', 'success');
    } catch (e: any) {
      setMessage({ text: e.message || 'Maintenance failed.', type: 'error' });
      toast('Maintenance Error', e.message || 'Operation failed', 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleBackup = async () => {
    setLoadingAction('backup');
    setMessage(null);
    try {
      const res = await api.systemBackup();
      if (res.status === 'success') {
        const msg = `Backup snapshot created: ${res.backup_file} (${(res.size_bytes / 1024).toFixed(1)} KB)`;
        setMessage({ text: msg, type: 'success' });
        toast('Snapshot Backup Created', res.backup_file, 'success');
      } else {
        setMessage({ text: res.message || 'Backup failed.', type: 'error' });
        toast('Backup Failed', res.message || 'Snapshot error', 'error');
      }
    } catch (e: any) {
      setMessage({ text: e.message || 'Backup failed.', type: 'error' });
      toast('Backup Failed', e.message || 'Error occurred', 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleExportGraphML = async () => {
    setLoadingAction('exportGraph');
    try {
      const blob = await api.exportGraphML();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge_graph_${new Date().toISOString().slice(0, 10)}.graphml`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setMessage({ text: 'GraphML XML exported successfully.', type: 'success' });
      toast('GraphML Exported', 'Downloaded knowledge_graph.graphml', 'info');
    } catch (e: any) {
      setMessage({ text: e.message || 'Export failed.', type: 'error' });
      toast('Export Error', e.message || 'Could not export GraphML', 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleRunBenchmark = async () => {
    setLoadingAction('benchmark');
    setMessage(null);
    try {
      const res = await api.searchBenchmark('accounting standards');
      setBenchmarkResult(res);
      const msg = `Benchmark Complete: RRF Hybrid ${res.rrf_hybrid_latency_ms}ms | Vector ${res.vector_cosine_latency_ms}ms`;
      setMessage({ text: msg, type: 'success' });
      toast('Benchmark Complete', `RRF Hybrid ${res.rrf_hybrid_latency_ms}ms`, 'success');
    } catch (e: any) {
      setMessage({ text: e.message || 'Benchmark failed.', type: 'error' });
      toast('Benchmark Error', e.message || 'Execution error', 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className={`${glassCardClasses} p-6 space-y-4`}>
      <div className="flex justify-between items-center border-b border-slate-200 dark:border-white/10 pb-4">
        <div>
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2">
            <Wrench className="w-5 h-5 text-indigo-500" />
            System Control & Operations
          </h3>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
            1-click WAL maintenance, atomic backups, GraphML exports, and latency benchmarking.
          </p>
        </div>
      </div>

      {message && (
        <div className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
          message.type === 'success'
            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
            : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
        }`}>
          {message.type === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
        <button
          onClick={handleMaintenance}
          disabled={loadingAction !== null}
          className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-100 dark:bg-slate-800/60 hover:bg-indigo-500/10 hover:border-indigo-500/30 border border-slate-200 dark:border-white/5 transition-all text-xs font-medium text-slate-700 dark:text-slate-300 gap-2 disabled:opacity-50"
        >
          {loadingAction === 'maintenance' ? <RefreshCw className="w-5 h-5 animate-spin text-indigo-500" /> : <Wrench className="w-5 h-5 text-indigo-500" />}
          <span>Defrag & Clean</span>
        </button>

        <button
          onClick={handleBackup}
          disabled={loadingAction !== null}
          className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-100 dark:bg-slate-800/60 hover:bg-emerald-500/10 hover:border-emerald-500/30 border border-slate-200 dark:border-white/5 transition-all text-xs font-medium text-slate-700 dark:text-slate-300 gap-2 disabled:opacity-50"
        >
          {loadingAction === 'backup' ? <RefreshCw className="w-5 h-5 animate-spin text-emerald-500" /> : <Database className="w-5 h-5 text-emerald-500" />}
          <span>Snapshot Backup</span>
        </button>

        <button
          onClick={handleExportGraphML}
          disabled={loadingAction !== null}
          className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-100 dark:bg-slate-800/60 hover:bg-cyan-500/10 hover:border-cyan-500/30 border border-slate-200 dark:border-white/5 transition-all text-xs font-medium text-slate-700 dark:text-slate-300 gap-2 disabled:opacity-50"
        >
          {loadingAction === 'exportGraph' ? <RefreshCw className="w-5 h-5 animate-spin text-cyan-500" /> : <Download className="w-5 h-5 text-cyan-500" />}
          <span>GraphML Export</span>
        </button>

        <button
          onClick={handleRunBenchmark}
          disabled={loadingAction !== null}
          className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-100 dark:bg-slate-800/60 hover:bg-amber-500/10 hover:border-amber-500/30 border border-slate-200 dark:border-white/5 transition-all text-xs font-medium text-slate-700 dark:text-slate-300 gap-2 disabled:opacity-50"
        >
          {loadingAction === 'benchmark' ? <RefreshCw className="w-5 h-5 animate-spin text-amber-500" /> : <Gauge className="w-5 h-5 text-amber-500" />}
          <span>Latency Benchmark</span>
        </button>
      </div>

      {benchmarkResult && (
        <div className="mt-4 p-4 rounded-xl bg-slate-900/80 border border-white/10 text-xs text-slate-300 space-y-2">
          <div className="flex justify-between items-center font-semibold text-slate-100">
            <span>⚡ Search Channel Latency Metrics</span>
            <span className="text-indigo-400">Query: "{benchmarkResult.query}"</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-center pt-1">
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
              <p className="text-[10px] text-indigo-400 uppercase tracking-wider font-semibold">RRF Hybrid Latency</p>
              <p className="text-base font-bold text-indigo-200">{benchmarkResult.rrf_hybrid_latency_ms} ms</p>
              <p className="text-[10px] text-slate-400">{benchmarkResult.total_rrf_hits} hits found</p>
            </div>
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <p className="text-[10px] text-cyan-400 uppercase tracking-wider font-semibold">NomIC Vector Latency</p>
              <p className="text-base font-bold text-cyan-200">{benchmarkResult.vector_cosine_latency_ms} ms</p>
              <p className="text-[10px] text-slate-400">{benchmarkResult.total_vector_hits} hits found</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
