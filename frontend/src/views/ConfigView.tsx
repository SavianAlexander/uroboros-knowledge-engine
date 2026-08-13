import React, { useState, useEffect } from 'react';
import { glassCardClasses } from '../lib/utils';
import { Settings2, Database, Key, Webhook, SplitSquareHorizontal, Layers, Fingerprint, HardDrive, RefreshCw, ArchiveRestore, Globe, Network, Activity } from 'lucide-react';
import { api } from '../lib/api';

export default function ConfigView() {
  const [snapshots, setSnapshots] = useState<any[]>([]);
  const [syncPeers, setSyncPeers] = useState<any[]>([]);
  const [syncLogs, setSyncLogs] = useState<any[]>([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [newPeer, setNewPeer] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const snaps = await api.snapshots().catch(() => ({ snapshots: [] }));
      setSnapshots(snaps?.snapshots || []);
    } catch (e) {
      console.error('Error loading snapshots:', e);
      setSnapshots([]);
    }

    try {
      const peers = await api.syncPeers().catch(() => ({ peers: [] }));
      setSyncPeers(peers?.peers || []);
    } catch (e) {
      console.error('Error loading sync peers:', e);
      setSyncPeers([]);
    }

    try {
      const logs = await api.syncLogs().catch(() => ({ logs: [] }));
      setSyncLogs(logs?.logs || []);
    } catch (e) {
      console.error('Error loading sync logs:', e);
      setSyncLogs([]);
    }
  };

  const handleCapture = async () => {
    setIsCapturing(true);
    try {
      await api.captureSnapshot();
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsCapturing(false);
    }
  };

  const handleRestore = async (timestamp: string) => {
    if (!confirm('Are you sure you want to restore this snapshot? Current data will be overwritten.')) return;
    try {
      await api.restoreSnapshot(timestamp);
      alert('Snapshot restored successfully.');
    } catch (e) {
      console.error(e);
      alert('Failed to restore snapshot.');
    }
  };

  const handleDeleteSnapshot = async (timestamp: string) => {
    if (!confirm('Delete this snapshot?')) return;
    try {
      await api.deleteSnapshot(timestamp);
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSync = async (peer_url: string) => {
    setIsSyncing(true);
    try {
      await api.syncExchange(peer_url);
      await loadData();
    } catch (e) {
      console.error(e);
      alert('Sync failed. Check peer connection.');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleAddPeer = async () => {
    if (!newPeer) return;
    try {
      await api.addSyncPeer(newPeer, newPeer);
      setNewPeer('');
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 h-full overflow-y-auto max-w-[1600px] mx-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Configuration & Processes</h2>
        <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">Configure advanced RAG strategies, data integrations, database snapshots, and peer synchronization.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* DB Snapshot Vault */}
        <div className={`${glassCardClasses} p-6 flex flex-col`}>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg"><HardDrive className="w-5 h-5"/></div>
              <div>
                <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200">Database Snapshot Vault</h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Manage and restore SQLite WAL snapshots</p>
              </div>
            </div>
            <button 
              onClick={handleCapture} 
              disabled={isCapturing}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isCapturing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ArchiveRestore className="w-4 h-4" />}
              Capture Snapshot
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto border border-slate-200 dark:border-white/5 rounded-xl bg-slate-50/30 dark:bg-slate-900/30 max-h-64">
            {snapshots.length === 0 ? (
               <div className="p-6 text-center text-sm text-slate-500">No snapshots available.</div>
            ) : (
               <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
                 <thead className="sticky top-0 bg-slate-100 dark:bg-slate-900 shadow-sm">
                   <tr>
                     <th className="px-4 py-2 font-medium text-slate-600 dark:text-slate-400">Timestamp</th>
                     <th className="px-4 py-2 font-medium text-slate-600 dark:text-slate-400">File</th>
                     <th className="px-4 py-2 font-medium text-slate-600 dark:text-slate-400 text-right">Actions</th>
                   </tr>
                 </thead>
                 <tbody className="divide-y divide-white/5">
                   {snapshots.map(s => (
                     <tr key={s.timestamp} className="hover:bg-white/[0.02]">
                       <td className="px-4 py-2 font-mono text-xs">{s.timestamp}</td>
                       <td className="px-4 py-2 text-xs truncate max-w-[150px]">{s.filename}</td>
                       <td className="px-4 py-2 text-right">
                         <button onClick={() => handleRestore(s.timestamp)} className="text-blue-500 hover:text-blue-400 text-xs mr-3 font-medium">Restore</button>
                         <button onClick={() => handleDeleteSnapshot(s.timestamp)} className="text-red-500 hover:text-red-400 text-xs font-medium">Delete</button>
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
            )}
          </div>
        </div>

        {/* P2P LAN Sync */}
        <div className={`${glassCardClasses} p-6 flex flex-col`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-rose-500/10 text-rose-600 dark:text-rose-400 rounded-lg"><Network className="w-5 h-5"/></div>
            <div>
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200">P2P LAN Synchronization</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Exchange CRDT deltas with trusted peer nodes</p>
            </div>
          </div>
          
          <div className="flex gap-2 mb-4">
             <input 
                type="text" 
                value={newPeer} 
                onChange={e => setNewPeer(e.target.value)} 
                placeholder="http://192.168.1.X:8080" 
                aria-label="Peer URL"
                className="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-lg text-sm text-slate-900 dark:text-slate-200 px-3 outline-none focus:border-rose-500/50"
             />
             <button onClick={handleAddPeer} className="px-4 py-2 bg-slate-200 dark:bg-white/10 rounded-lg text-sm font-medium hover:bg-slate-300 dark:hover:bg-white/20 transition-colors">Add Peer</button>
          </div>

          <div className="flex-1 overflow-y-auto border border-slate-200 dark:border-white/5 rounded-xl bg-slate-50/30 dark:bg-slate-900/30 max-h-64">
            {syncPeers.length === 0 ? (
               <div className="p-6 text-center text-sm text-slate-500">No peers configured.</div>
            ) : (
               <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
                 <tbody className="divide-y divide-white/5">
                   {syncPeers.map(p => (
                     <tr key={p.id} className="hover:bg-white/[0.02]">
                       <td className="px-4 py-3 font-mono text-xs text-slate-500 dark:text-slate-400">{p.url}</td>
                       <td className="px-4 py-3 text-right">
                         <button 
                            onClick={() => handleSync(p.url)} 
                            disabled={isSyncing}
                            className="flex items-center gap-1.5 ml-auto text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 text-xs font-medium bg-rose-500/10 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                         >
                            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
                            Sync Now
                         </button>
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Chunking & Embedding Strategy */}
        <div className={`${glassCardClasses} p-6 flex flex-col`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-lg"><SplitSquareHorizontal className="w-5 h-5"/></div>
            <div>
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200">Chunking & Embedding Strategy</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Tune how documents are split and embedded</p>
            </div>
          </div>
          
          <div className="space-y-5">
            <div>
              <label htmlFor="semantic-chunk-size" className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block">Semantic Chunk Size</label>
              <div className="flex items-center gap-3">
                <input id="semantic-chunk-size" type="range" min="256" max="2048" step="128" defaultValue="1024" onChange={() => {}} className="flex-1 accent-purple-500" />
                <span className="text-sm text-slate-600 dark:text-slate-400 w-16 text-right font-mono bg-slate-50 dark:bg-slate-900 px-2 py-1 rounded border border-slate-200 dark:border-white/5">1024</span>
              </div>
              <p className="text-[10px] text-slate-500 mt-1">Target token count per vector node</p>
            </div>

            <div>
              <label htmlFor="chunk-overlap" className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block">Chunk Overlap</label>
              <div className="flex items-center gap-3">
                <input id="chunk-overlap" type="range" min="0" max="512" step="32" defaultValue="128" onChange={() => {}} className="flex-1 accent-purple-500" />
                <span className="text-sm text-slate-600 dark:text-slate-400 w-16 text-right font-mono bg-slate-50 dark:bg-slate-900 px-2 py-1 rounded border border-slate-200 dark:border-white/5">128</span>
              </div>
              <p className="text-[10px] text-slate-500 mt-1">Token overlap between adjacent chunks to preserve context</p>
            </div>

            <div>
              <label htmlFor="embedding-model" className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block">Embedding Model</label>
              <select id="embedding-model" onChange={() => {}} className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-lg text-sm text-slate-900 dark:text-slate-200 p-2.5 outline-none focus:border-purple-500/50">
                <option>text-embedding-3-small (Default)</option>
                <option>text-embedding-3-large</option>
                <option>nomic-embed-text-v1.5</option>
                <option>bge-m3 (Multilingual)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Auto-Tag Rules Engine (Updated) */}
        <div className={`${glassCardClasses} p-6 flex flex-col`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-lg"><Settings2 className="w-5 h-5"/></div>
            <div>
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200">Metadata Extraction Rules</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Automatically assign tags based on parsing.</p>
            </div>
          </div>
          
          <div className="flex-1 overflow-x-auto border border-slate-200 dark:border-white/5 rounded-xl bg-slate-50/30 dark:bg-slate-900/30">
            <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/5 bg-slate-50/50 dark:bg-slate-900/50">
                  <th className="px-4 py-3 font-medium text-slate-600 dark:text-slate-400">Target Tag</th>
                  <th className="px-4 py-3 font-medium text-slate-600 dark:text-slate-400">Match Strategy</th>
                  <th className="px-4 py-3 text-right font-medium text-slate-600 dark:text-slate-400">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <tr className="hover:bg-white/[0.02]">
                  <td className="px-4 py-3"><span className="px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded text-xs font-medium border border-indigo-500/20">invoice</span></td>
                  <td className="px-4 py-3 text-xs text-slate-600 dark:text-slate-400">Regex Match</td>
                  <td className="px-4 py-3 text-right">
                    <button className="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:text-indigo-400 text-xs font-medium transition-colors">Edit</button>
                  </td>
                </tr>
                <tr className="hover:bg-white/[0.02]">
                  <td className="px-4 py-3"><span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs font-medium border border-emerald-500/20">confidential</span></td>
                  <td className="px-4 py-3 text-xs text-slate-600 dark:text-slate-400 flex items-center gap-1"><Layers className="w-3 h-3 text-emerald-600 dark:text-emerald-400"/> LLM Zero-Shot</td>
                  <td className="px-4 py-3 text-right">
                    <button className="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:text-indigo-400 text-xs font-medium transition-colors">Edit</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <button className="mt-4 py-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-500/20 border border-indigo-500/20 rounded-xl text-sm font-medium transition-colors w-full px-6">
            + Create New Rule
          </button>
        </div>

        {/* Search & Data Managers */}
        <div className={`${glassCardClasses} p-6 flex flex-col col-span-1 md:col-span-2`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-lg"><Database className="w-5 h-5"/></div>
            <div>
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200">Search & Data Managers</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Manage FTS Synonyms, Query Macros, and Tag Aliases.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
             <div className="border border-slate-200 dark:border-white/5 rounded-xl bg-slate-50/50 dark:bg-slate-900/50 p-4 flex flex-col">
                <h4 className="text-sm font-medium text-slate-900 dark:text-slate-200 mb-2">FTS Synonyms</h4>
                <p className="text-xs text-slate-500 mb-4 flex-1">Map custom vocabularies to unified search terms.</p>
                <button className="w-full py-2 bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 rounded-lg text-xs font-medium transition-colors border border-amber-500/20">Manage Synonyms</button>
             </div>
             
             <div className="border border-slate-200 dark:border-white/5 rounded-xl bg-slate-50/50 dark:bg-slate-900/50 p-4 flex flex-col">
                <h4 className="text-sm font-medium text-slate-900 dark:text-slate-200 mb-2">Query Macros</h4>
                <p className="text-xs text-slate-500 mb-4 flex-1">Define shortcut templates for complex search queries.</p>
                <button className="w-full py-2 bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 rounded-lg text-xs font-medium transition-colors border border-amber-500/20">Manage Macros</button>
             </div>
             
             <div className="border border-slate-200 dark:border-white/5 rounded-xl bg-slate-50/50 dark:bg-slate-900/50 p-4 flex flex-col">
                <h4 className="text-sm font-medium text-slate-900 dark:text-slate-200 mb-2">Tag Aliases</h4>
                <p className="text-xs text-slate-500 mb-4 flex-1">Group multiple variant tags under a canonical alias.</p>
                <button className="w-full py-2 bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 rounded-lg text-xs font-medium transition-colors border border-amber-500/20">Manage Tag Aliases</button>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}

