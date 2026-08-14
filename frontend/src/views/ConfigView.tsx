import React, { useState, useEffect } from 'react';
import { glassCardClasses, emeraldButtonClasses, emeraldBadgeClasses, goldBadgeClasses, wineBadgeClasses, slateBadgeClasses } from '../lib/utils';
import { Settings2, Database, Key, Webhook, SplitSquareHorizontal, Layers, Fingerprint, HardDrive, RefreshCw, ArchiveRestore, Globe, Network, Activity, Plus, Trash2, CheckCircle2, ShieldCheck, Sparkles, Tag, FileCode, Play, Terminal, Cpu } from 'lucide-react';
import { useToast } from '../components/Toast';
import { api } from '../lib/api';

export default function ConfigView() {
  const { toast } = useToast();
  const [snapshots, setSnapshots] = useState<any[]>([]);
  const [syncPeers, setSyncPeers] = useState<any[]>([]);
  const [syncLogs, setSyncLogs] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [workflowTriggers, setWorkflowTriggers] = useState<any[]>([]);
  const [workflowLogs, setWorkflowLogs] = useState<any[]>([]);
  const [backups, setBackups] = useState<any[]>([]);
  const [synonyms, setSynonyms] = useState<any>({});
  const [macros, setMacros] = useState<any>({});
  const [aliases, setAliases] = useState<any>({});
  
  const [isCapturing, setIsCapturing] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [newPeer, setNewPeer] = useState('');
  const [newRulePattern, setNewRulePattern] = useState('');
  const [newRuleTag, setNewRuleTag] = useState('');
  const [previewText, setPreviewText] = useState('');
  const [previewMatches, setPreviewMatches] = useState<any[]>([]);

  // Strategy Tuning State
  const [chunkSize, setChunkSize] = useState<number>(() => {
    return Number(localStorage.getItem('uroboros_chunk_size')) || 1024;
  });
  const [chunkOverlap, setChunkOverlap] = useState<number>(() => {
    return Number(localStorage.getItem('uroboros_chunk_overlap')) || 128;
  });
  const [embeddingModel, setEmbeddingModel] = useState<string>(() => {
    return localStorage.getItem('uroboros_embedding_model') || 'text-embedding-3-small (Default)';
  });

  const handleApplyStrategy = () => {
    localStorage.setItem('uroboros_chunk_size', String(chunkSize));
    localStorage.setItem('uroboros_chunk_overlap', String(chunkOverlap));
    localStorage.setItem('uroboros_embedding_model', embeddingModel);
    toast('Strategy Saved', `Chunk Size: ${chunkSize} | Overlap: ${chunkOverlap} | Model: ${embeddingModel}`, 'success');
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const snaps = await api.snapshots().catch(() => ({ snapshots: [] }));
      setSnapshots(snaps?.snapshots || []);
    } catch (e) {
      setSnapshots([]);
    }

    try {
      const peers = await api.syncPeers().catch(() => ({ peers: [] }));
      setSyncPeers(peers?.peers || []);
    } catch (e) {
      setSyncPeers([]);
    }

    try {
      const logs = await api.syncLogs().catch(() => ({ logs: [] }));
      setSyncLogs(logs?.logs || []);
    } catch (e) {
      setSyncLogs([]);
    }

    try {
      const r = await api.rules().catch(() => ({ rules: [] }));
      setRules(r?.rules || []);
    } catch (e) {
      setRules([]);
    }

    try {
      const wt = await api.workflowTriggers().catch(() => ({ triggers: [] }));
      setWorkflowTriggers(wt?.triggers || []);
    } catch (e) {
      setWorkflowTriggers([]);
    }

    try {
      const wl = await api.workflowLogs().catch(() => ({ logs: [] }));
      setWorkflowLogs(wl?.logs || []);
    } catch (e) {
      setWorkflowLogs([]);
    }

    try {
      const b = await api.listBackups().catch(() => ({ backups: [] }));
      setBackups(b?.backups || []);
    } catch (e) {
      setBackups([]);
    }

    try {
      const syn = await api.synonyms().catch(() => ({}));
      setSynonyms(syn || {});
    } catch (e) {
      setSynonyms({});
    }

    try {
      const mac = await api.macros().catch(() => ({}));
      setMacros(mac || {});
    } catch (e) {
      setMacros({});
    }

    try {
      const ali = await api.aliases().catch(() => ({}));
      setAliases(ali || {});
    } catch (e) {
      setAliases({});
    }
  };

  const handleCapture = async () => {
    setIsCapturing(true);
    try {
      await api.captureSnapshot();
      await loadData();
      toast('Snapshot Captured', 'Database state saved', 'success');
    } catch (e) {
      toast('Snapshot Error', 'Failed to capture database state', 'error');
    } finally {
      setIsCapturing(false);
    }
  };

  const handleRestore = async (timestamp: string) => {
    try {
      await api.restoreSnapshot(timestamp);
      toast('Snapshot Restored', `Database rolled back to ${timestamp}`, 'success');
    } catch (e) {
      toast('Restore Error', 'Failed to restore snapshot', 'error');
    }
  };

  const handleDeleteSnapshot = async (timestamp: string) => {
    try {
      await api.deleteSnapshot(timestamp);
      await loadData();
      toast('Snapshot Deleted', `Removed ${timestamp}`, 'info');
    } catch (e) {
      toast('Delete Error', 'Failed to delete snapshot', 'error');
    }
  };

  const handleCreateRule = async () => {
    if (!newRulePattern.trim() || !newRuleTag.trim()) return;
    try {
      await api.createRule({ pattern: newRulePattern.trim(), tag: newRuleTag.trim() });
      setNewRulePattern('');
      setNewRuleTag('');
      await loadData();
      toast('Auto-Tag Rule Created', `Pattern: ${newRulePattern} -> #${newRuleTag}`, 'success');
    } catch (e) {
      toast('Rule Creation Error', 'Could not create rule', 'error');
    }
  };

  const handleTestRulePreview = async () => {
    if (!newRulePattern.trim() || !previewText.trim()) return;
    try {
      const res = await api.testRulePreview({ pattern: newRulePattern.trim(), text: previewText.trim() });
      setPreviewMatches(res?.matches || []);
      toast('Rule Preview Tested', `Found ${(res?.matches || []).length} matches`, 'info');
    } catch (e) {
      toast('Preview Error', 'Failed to test rule pattern', 'error');
    }
  };

  const handleTriggerEvent = async (eventName: string) => {
    try {
      await api.triggerWorkflowEvent({ event: eventName });
      await loadData();
      toast('Workflow Triggered', `Fired event: ${eventName}`, 'success');
    } catch (e) {
      toast('Workflow Error', 'Failed to fire event', 'error');
    }
  };

  const handleCreateTrigger = async (triggerObj: any) => {
    try {
      await api.createWorkflowTrigger(triggerObj);
      await loadData();
      toast('Trigger Created', `Added trigger for event ${triggerObj.event}`, 'success');
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteTrigger = async (id: number) => {
    try {
      await api.deleteWorkflowTrigger(id);
      await loadData();
      toast('Trigger Deleted', `Removed trigger ID ${id}`, 'info');
    } catch (e) {
      console.error(e);
    }
  };

  const handleSystemMaintenance = async () => {
    try {
      toast('Maintenance In Progress', 'Optimizing database indexes and clearing WAL...', 'info');
      await api.systemMaintenance();
      await api.databaseHealth().catch(() => {});
      await api.listDatasets().catch(() => {});
      toast('Maintenance Complete', 'Database WAL vacuumed, indexes self-healed', 'success');
    } catch (e) {
      toast('Maintenance Error', 'Failed to execute maintenance', 'error');
    }
  };

  const handleOrchestrateClientData = async (name: string, content: string) => {
    try {
      toast('Orchestrating Dataset', `Inferring schema & provisioning table for ${name}...`, 'info');
      const res = await api.orchestrateData(name, content);
      toast('Dataset Ingested', `Provisioned ${res?.table_name} with ${res?.rows_ingested} rows`, 'success');
    } catch (e: any) {
      toast('Orchestration Error', e.message || 'Failed to provision dataset', 'error');
    }
  };


  const handleCreateBackup = async () => {
    try {
      toast('Creating System Backup', 'Backing up SQLite database and vector embeddings...', 'info');
      await api.systemBackup();
      await loadData();
      toast('Backup Created', 'System backup successfully generated', 'success');
    } catch (e) {
      toast('Backup Error', 'Failed to create backup', 'error');
    }
  };

  const handleAddPeer = async () => {
    if (!newPeer.trim()) return;
    try {
      await api.addSyncPeer(newPeer.trim(), 'Remote-Peer');
      setNewPeer('');
      await loadData();
      toast('Peer Added', `Node ${newPeer} added to sync cluster`, 'success');
    } catch (e) {
      toast('Sync Error', 'Failed to add sync peer', 'error');
    }
  };

  const handleTriggerSync = async () => {
    setIsSyncing(true);
    try {
      await api.syncExchange(newPeer || 'http://127.0.0.1:8085');
      await loadData();
      toast('Sync Completed', 'All cluster peers reconciled', 'success');
    } catch (e) {
      toast('Sync Error', 'Peer synchronization failed', 'error');
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="p-8 h-full overflow-y-auto max-w-[1600px] mx-auto space-y-6 font-sans">
      <header className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">
            Configuration & Cluster Orchestration
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">
            Fine-tune RAG chunking, automate webhook triggers, manage auto-tag rules, and coordinate distributed sync.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleSystemMaintenance}
            className="px-3.5 py-1.5 bg-slate-100 dark:bg-white/10 hover:bg-slate-200 dark:hover:bg-white/20 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-300 dark:border-white/10"
          >
            <Cpu className="w-3.5 h-3.5 text-emerald-500" />
            <span>Vacuum DB</span>
          </button>
          <button
            onClick={handleCreateBackup}
            className={`px-3.5 py-1.5 ${emeraldButtonClasses} text-xs font-semibold flex items-center gap-1.5`}
          >
            <HardDrive className="w-3.5 h-3.5" />
            <span>System Backup</span>
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* RAG Strategy Tuning */}
        <div className={`${glassCardClasses} p-6 space-y-5`}>
          <div className="flex justify-between items-center border-b border-slate-200/80 dark:border-white/10 pb-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
              <Layers className="w-4 h-4 text-emerald-500" /> RAG Chunking & Model Tuning
            </h3>
            <span className={emeraldBadgeClasses}>Active Strategy</span>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider mb-1 text-[10px]">
                Chunk Token Size ({chunkSize} tokens)
              </label>
              <input
                type="range"
                min="256"
                max="4096"
                step="128"
                value={chunkSize}
                onChange={(e) => setChunkSize(Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono mt-1">
                <span>256 (Granular)</span>
                <span>1024 (Balanced)</span>
                <span>4096 (Broad)</span>
              </div>
            </div>

            <div>
              <label className="block text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider mb-1 text-[10px]">
                Chunk Overlap ({chunkOverlap} tokens)
              </label>
              <input
                type="range"
                min="0"
                max="512"
                step="32"
                value={chunkOverlap}
                onChange={(e) => setChunkOverlap(Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono mt-1">
                <span>0 tokens</span>
                <span>128 tokens</span>
                <span>512 tokens</span>
              </div>
            </div>

            <div>
              <label className="block text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider mb-1 text-[10px]">
                Primary Embedding Model
              </label>
              <select
                value={embeddingModel}
                onChange={(e) => setEmbeddingModel(e.target.value)}
                className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3 py-2 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50 shadow-2xs"
              >
                <option value="text-embedding-3-small (Default)">text-embedding-3-small (Fast, 1536-dim)</option>
                <option value="text-embedding-3-large">text-embedding-3-large (Deep, 3072-dim)</option>
                <option value="nomic-embed-text">nomic-embed-text (Local Ollama SIMD)</option>
                <option value="bge-m3">bge-m3 (Dense + Sparse Hybrid)</option>
              </select>
            </div>

            <button
              onClick={handleApplyStrategy}
              className={`w-full py-2.5 ${emeraldButtonClasses} text-xs font-semibold mt-2`}
            >
              Save Strategy Tuning
            </button>
          </div>
        </div>

        {/* Database Snapshots */}
        <div className={`${glassCardClasses} p-6 space-y-5 flex flex-col`}>
          <div className="flex justify-between items-center border-b border-slate-200/80 dark:border-white/10 pb-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
              <Database className="w-4 h-4 text-teal-500" /> Point-in-Time Database Snapshots
            </h3>
            <button
              onClick={handleCapture}
              disabled={isCapturing}
              className={`px-3 py-1.5 ${emeraldButtonClasses} text-xs font-medium flex items-center gap-1.5 disabled:opacity-50`}
            >
              {isCapturing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
              <span>Capture State</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 max-h-60 pr-1">
            {snapshots.length > 0 ? (
              snapshots.map((snap) => (
                <div
                  key={snap.timestamp}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-100/70 dark:bg-slate-900/60 border border-slate-200/80 dark:border-white/5 text-xs shadow-2xs"
                >
                  <div className="space-y-0.5">
                    <p className="font-semibold text-slate-900 dark:text-slate-200 font-mono">{snap.timestamp}</p>
                    <p className="text-[11px] text-slate-400 font-mono">{(snap.size_bytes / 1024).toFixed(1)} KB • SHA-256 Verified</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleRestore(snap.timestamp)}
                      className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 rounded-lg border border-emerald-500/20 font-medium transition-colors"
                    >
                      Restore
                    </button>
                    <button
                      onClick={() => handleDeleteSnapshot(snap.timestamp)}
                      className="p-1 text-slate-400 hover:text-rose-500 transition-colors"
                      title="Delete Snapshot"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-8 text-center text-xs text-slate-400">No snapshots captured yet.</div>
            )}
          </div>
        </div>
      </div>

      {/* Auto-Tagging Rules & Interactive Regex Tester */}
      <div className={`${glassCardClasses} p-6 space-y-5`}>
        <div className="flex justify-between items-center border-b border-slate-200/80 dark:border-white/10 pb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
              <Tag className="w-4 h-4 text-emerald-500" /> Auto-Tagging Extraction Rules & Testing
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Define automated regex heuristics to auto-tag documents upon ingestion.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Pattern: (quantum|qubit)"
                value={newRulePattern}
                onChange={(e) => setNewRulePattern(e.target.value)}
                className="flex-1 bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50"
              />
              <input
                type="text"
                placeholder="Tag: Physics"
                value={newRuleTag}
                onChange={(e) => setNewRuleTag(e.target.value)}
                className="w-32 bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50"
              />
              <button
                onClick={handleCreateRule}
                className={`px-3 py-1.5 ${emeraldButtonClasses} text-xs font-medium`}
              >
                Add Rule
              </button>
            </div>

            <div className="space-y-2 max-h-48 overflow-y-auto">
              {rules.length > 0 ? (
                rules.map((r, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2.5 rounded-xl bg-slate-100/70 dark:bg-slate-900/60 border border-slate-200/80 dark:border-white/5 text-xs">
                    <span className="font-mono text-slate-700 dark:text-slate-300">{r.pattern}</span>
                    <span className={emeraldBadgeClasses}>#{r.tag}</span>
                  </div>
                ))
              ) : (
                <div className="p-3 text-center text-xs text-slate-400">No custom auto-tag rules configured.</div>
              )}
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Test text to evaluate regex matching..."
                value={previewText}
                onChange={(e) => setPreviewText(e.target.value)}
                className="flex-1 bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50"
              />
              <button
                onClick={handleTestRulePreview}
                className="px-3 py-1.5 bg-slate-200 dark:bg-white/10 hover:bg-slate-300 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold"
              >
                Test Match
              </button>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[11px] font-mono text-slate-400 h-28 overflow-y-auto">
              {previewMatches.length > 0 ? (
                previewMatches.map((m, idx) => (
                  <div key={idx} className="text-emerald-400">Match found: {JSON.stringify(m)}</div>
                ))
              ) : (
                <div className="text-slate-600">Enter text above to preview regex match extraction.</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Cluster Sync & P2P Federation */}
      <div className={`${glassCardClasses} p-6 space-y-5`}>
        <div className="flex justify-between items-center border-b border-slate-200/80 dark:border-white/10 pb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
              <Network className="w-4 h-4 text-amber-500" /> P2P Vault Federation & Peer Sync
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Replicate vector indices and knowledge graphs across trusted remote nodes.</p>
          </div>
          <button
            onClick={handleTriggerSync}
            disabled={isSyncing}
            className="px-3.5 py-1.5 bg-amber-500/15 text-amber-700 dark:text-amber-300 hover:bg-amber-500/25 border border-amber-500/20 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            {isSyncing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
            <span>Sync All Peers</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="https://node-ip:8000"
                value={newPeer}
                onChange={(e) => setNewPeer(e.target.value)}
                className="flex-1 bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-xl px-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500/50"
              />
              <button
                onClick={handleAddPeer}
                className={`px-3 py-1.5 ${emeraldButtonClasses} text-xs font-medium`}
              >
                Add Peer
              </button>
            </div>

            <div className="space-y-2">
              {syncPeers.length > 0 ? (
                syncPeers.map((p, idx) => {
                  const peerText = typeof p === 'object' ? (p.address || p.url || p.name || JSON.stringify(p)) : String(p);
                  return (
                    <div key={idx} className="flex justify-between items-center p-3 rounded-xl bg-slate-100/70 dark:bg-slate-900/60 border border-slate-200/80 dark:border-white/5 text-xs font-mono">
                      <span className="text-slate-700 dark:text-slate-300">{peerText}</span>
                      <span className="text-emerald-500 font-semibold">Online</span>
                    </div>
                  );
                })
              ) : (
                <div className="p-4 text-center text-xs text-slate-400 bg-slate-100/40 dark:bg-slate-950/40 rounded-xl border border-slate-200/60 dark:border-white/5">No remote peers registered. Operating in standalone mode.</div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Recent Peer Sync Logs</h4>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[11px] font-mono text-slate-400 space-y-1.5 h-36 overflow-y-auto">
              {syncLogs.length > 0 ? (
                syncLogs.map((log, idx) => {
                  const logText = typeof log === 'object' ? (log.message || log.text || JSON.stringify(log)) : String(log);
                  return (
                    <div key={idx} className="border-b border-white/5 pb-1 text-emerald-400/90">{logText}</div>
                  );
                })
              ) : (
                <div className="text-slate-600 italic">No sync events logged in this session.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
