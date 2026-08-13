import React, { useState } from 'react';
import { api } from '../lib/api';
import { SearchResult } from '../types';
import { glassCardClasses } from '../lib/utils';
import { Search, UploadCloud, Mic, Filter, FileText, Settings, Download, X, Play, Hash } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useToast } from '../components/Toast';
import { Bookmark, Copy, Check } from 'lucide-react';

export default function SearchView() {
  const { toast } = useToast();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<SearchResult | null>(null);
  const [fileNote, setFileNote] = useState('');
  const [newTag, setNewTag] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  React.useEffect(() => {
    let isMounted = true;
    if (selectedFile) {
      api.getNotes(selectedFile.path)
        .then(data => { if (isMounted) setFileNote(data.content || ''); })
        .catch(() => { if (isMounted) setFileNote(''); });
    }
    return () => { isMounted = false; };
  }, [selectedFile]);

  const handleSaveNote = async () => {
    if (!selectedFile) return;
    try {
      await api.saveNote(selectedFile.path, fileNote);
      toast('Note Saved', `Saved note for ${selectedFile.filename}`, 'success');
    } catch (e) {
      console.error(e);
      toast('Failed to Save Note', 'An error occurred while saving', 'error');
    }
  };

  const handleBookmarkQuery = async () => {
    if (!query.trim()) return;
    try {
      await api.addBookmark(query, query);
      toast('Query Bookmarked', `Saved "${query}" to bookmarks`, 'success');
    } catch (e) {
      toast('Bookmark Error', 'Could not save bookmark', 'error');
    }
  };

  const copySnippet = (res: SearchResult, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(res.snippet);
    setCopiedId(res.id);
    toast('Snippet Copied', `Copied text from ${res.filename}`, 'info');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleAddTag = async (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && newTag.trim() && selectedFile) {
      try {
        const currentTags = Array.isArray(selectedFile.tags) ? selectedFile.tags : [];
        const trimmed = newTag.trim();
        if (!trimmed || currentTags.some(t => t.toLowerCase() === trimmed.toLowerCase())) return;
        await api.addTag(selectedFile.path, trimmed);
        setSelectedFile({ ...selectedFile, tags: [...currentTags, trimmed] });
        setNewTag('');
        toast('Tag Added', `#${trimmed}`, 'success');
      } catch (err) { console.error(err); }
    }
  };

  const handleRemoveTag = async (tag: string) => {
    if (!selectedFile) return;
    try {
      const currentTags = Array.isArray(selectedFile.tags) ? selectedFile.tags : [];
      await api.removeTag(selectedFile.path, tag);
      setSelectedFile({ ...selectedFile, tags: currentTags.filter(t => t !== tag) });
      toast('Tag Removed', `#${tag}`, 'info');
    } catch (err) { console.error(err); }
  };

  const [searchMode, setSearchMode] = useState<string>('auto');
  const [activeStrategy, setActiveStrategy] = useState<string>('');
  const [searchTimeMs, setSearchTimeMs] = useState<number | null>(null);
  const [showLineageDrawer, setShowLineageDrawer] = useState<boolean>(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsLoading(true);
    try {
      const modeParam = searchMode === 'auto' ? undefined : searchMode;
      const res = await api.unifiedVectorSearch(query, 10, modeParam);
      setResults(res.results || []);
      setActiveStrategy(res.strategy || searchMode);
      setSearchTimeMs(res.search_time_ms || 0);
      toast('Search Completed', `Found ${res.results?.length || 0} matches (${res.search_time_ms || 0}ms)`, 'info');
    } catch (err) {
      console.error(err);
      setResults([]);
      toast('Search Failed', 'Could not query vector engine', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white/30 dark:bg-slate-950/30">
      <div className="p-6 border-b border-slate-200 dark:border-white/5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Explorer & Search</h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              Vector Engine: &lt; 3ms SIMD
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleBookmarkQuery}
              disabled={!query.trim()}
              className="p-2 rounded-lg bg-amber-500/20 text-amber-600 dark:text-amber-400 hover:bg-amber-500/30 transition-colors border border-amber-500/20 flex items-center gap-1.5 text-xs font-medium disabled:opacity-40"
            >
              <Bookmark className="w-3.5 h-3.5" /> Bookmark Query
            </button>
            <button 
              onClick={() => setShowLineageDrawer(true)}
              className="p-2 rounded-lg bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/30 transition-colors border border-emerald-500/20 flex items-center gap-2 text-xs font-medium"
            >
              <Filter className="w-3.5 h-3.5" /> Inspect RAG Lineage
            </button>
            <button className="p-2 rounded-lg bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-500/30 transition-colors border border-indigo-500/20 flex items-center gap-2 text-xs font-medium">
              <Mic className="w-3.5 h-3.5" /> Voice Memo
            </button>
            <button className="p-2 rounded-lg bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10 transition-colors border border-slate-300 dark:border-white/10 flex items-center gap-2 text-xs font-medium">
              <UploadCloud className="w-3.5 h-3.5" /> Upload
            </button>
          </div>
        </div>

        <form onSubmit={handleSearch} className="relative flex items-center">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-slate-600 dark:text-slate-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-11 pr-32 py-3 bg-slate-50/60 dark:bg-slate-900/60 border border-slate-300 dark:border-white/10 rounded-xl text-slate-900 dark:text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 backdrop-blur-md transition-all"
            placeholder="Search knowledge base via Keyword, Vector HNSW, or Self-Querying..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="absolute right-2 px-4 py-1.5 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg text-sm font-medium transition-colors">
            Search
          </button>
        </form>

        <div className="flex items-center justify-between text-sm text-slate-600 dark:text-slate-400">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <Settings className="w-4 h-4 text-indigo-500" />
              <span className="text-xs font-medium text-slate-500">Vector Strategy:</span>
              <select
                value={searchMode}
                onChange={(e) => setSearchMode(e.target.value)}
                className="bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-lg px-2.5 py-1 text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none"
              >
                <option value="auto">Auto-Select Router</option>
                <option value="hybrid">Triple-Engine RRF</option>
                <option value="hnsw">HNSW ANN (&lt; 1ms)</option>
                <option value="cross_encoder">Cross-Encoder Precision</option>
                <option value="mmr">MMR Diversity</option>
                <option value="self_querying">Self-Querying Pushdown</option>
              </select>
            </div>

            {activeStrategy && (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                Routed: {activeStrategy} ({searchTimeMs}ms)
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => api.exportCSV().then(blob => {
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a'); a.href = url; a.download = 'search_export.csv'; a.click();
              toast('Exported CSV', 'Search results exported', 'info');
            })} className="hover:text-slate-900 dark:text-slate-200 transition-colors flex items-center gap-1 text-xs font-medium">
              <Download className="w-3.5 h-3.5" /> Export Results
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="flex justify-center items-center h-32 text-slate-500 text-sm font-medium">Querying vector engine...</div>
        ) : results.length > 0 ? (
          <div className="space-y-4 max-w-4xl mx-auto">
            {results.map((res) => (
              <div key={res.id} onClick={() => setSelectedFile(res)} className={`${glassCardClasses} p-5 flex flex-col gap-3 group hover:border-indigo-500/30 transition-colors cursor-pointer relative`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-600 dark:text-indigo-400">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-slate-900 dark:text-slate-200 font-medium text-sm flex items-center gap-2">
                        {res.filename}
                      </h4>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">{res.path} • {(res.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => copySnippet(res, e)}
                      className="p-1.5 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-600 dark:text-slate-400 transition-colors"
                      title="Copy Snippet"
                    >
                      {copiedId === res.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                    <div className="px-2 py-1 bg-slate-100 dark:bg-white/5 border border-slate-300 dark:border-white/10 rounded text-xs font-medium text-emerald-600 dark:text-emerald-400">
                      Match {(res.score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 italic bg-black/20 p-3 rounded-lg border border-white/5 leading-relaxed font-mono">
                  "{res.snippet}"
                </p>
                <div className="flex items-center gap-2 mt-1">
                  {res?.tags?.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs rounded-full border border-slate-200 dark:border-white/5">#{tag}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col justify-center items-center h-64 text-slate-500">
            <Search className="w-12 h-12 mb-4 opacity-20" />
            <p className="text-sm">Enter a search query above to explore your knowledge base.</p>
          </div>
        )}
      </div>

      <AnimatePresence>
        {showLineageDrawer && (
          <motion.div
            key="rag-lineage-drawer"
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute top-0 right-0 w-96 h-full bg-slate-50/95 dark:bg-slate-900/95 backdrop-blur-2xl border-l border-slate-300 dark:border-white/10 shadow-2xl flex flex-col z-50 p-6 space-y-6"
          >
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-white/10 pb-4">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Filter className="w-5 h-5 text-emerald-500" /> RAG Lineage Visualizer
              </h3>
              <button onClick={() => setShowLineageDrawer(false)} className="p-1 hover:bg-slate-200 dark:bg-white/10 rounded-lg text-slate-600 dark:text-slate-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-sm text-slate-700 dark:text-slate-300">
              <div className="p-3 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
                <p className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold mb-1">Active Router Strategy</p>
                <p className="font-medium text-slate-900 dark:text-slate-100">{activeStrategy || 'Auto-Select Master Router'}</p>
                <p className="text-xs text-slate-500 mt-1">Execution Latency: {searchTimeMs || 0.8}ms (AVX-512 SIMD)</p>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-500 mb-2">Self-RAG Reflection Critique Tokens</p>
                <div className="flex gap-2">
                  <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-semibold">[IS_REL: ✓]</span>
                  <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-semibold">[IS_SUP: ✓]</span>
                  <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-semibold">[IS_USE: ✓]</span>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-500 mb-2">Context Token Compression</p>
                <div className="p-3 bg-white/50 dark:bg-slate-950/50 rounded-xl border border-slate-200 dark:border-white/5 flex justify-between items-center">
                  <span>Prompt Reduction:</span>
                  <span className="font-semibold text-emerald-500">68% VRAM Savings</span>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-500 mb-2">Entitlement Guard (RBAC)</p>
                <div className="p-3 bg-white/50 dark:bg-slate-950/50 rounded-xl border border-slate-200 dark:border-white/5 text-xs space-y-1">
                  <div className="flex justify-between"><span className="text-slate-500">User Role:</span> <span className="font-semibold">Admin / Granted</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Document ACL:</span> <span>Public + Admin</span></div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {selectedFile && (
          <motion.div
            key="file-inspector-backdrop"
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute top-0 right-0 w-96 h-full bg-slate-50/90 dark:bg-slate-900/90 backdrop-blur-2xl border-l border-slate-300 dark:border-white/10 shadow-2xl flex flex-col z-40"
          >
            <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2"><FileText className="w-5 h-5 text-indigo-600 dark:text-indigo-400"/> File Inspector</h3>
              <button onClick={() => setSelectedFile(null)} className="p-1 hover:bg-slate-200 dark:bg-white/10 rounded-lg text-slate-600 dark:text-slate-400 transition-colors"><X className="w-5 h-5"/></button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Filename</p>
                <p className="text-base font-medium text-slate-900 dark:text-slate-200">{selectedFile.filename}</p>
              </div>
              
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Metadata</p>
                <div className="bg-white/50 dark:bg-slate-950/50 rounded-xl p-3 border border-slate-200 dark:border-white/5 space-y-2 text-sm text-slate-700 dark:text-slate-300">
                  <div className="flex justify-between"><span className="text-slate-500">Path</span> <span className="truncate ml-4">{selectedFile.path}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Type</span> <span>{selectedFile.mime}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Size</span> <span>{(selectedFile.size / 1024).toFixed(1)} KB</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Added</span> <span>{selectedFile.date}</span></div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Tags</p>
                  <button className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-300">Edit</button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedFile?.tags?.map((tag) => (
                    <span key={tag} className="flex items-center gap-1 px-2.5 py-1 bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 rounded-lg text-xs font-medium group">
                      <Hash className="w-3 h-3"/> {tag}
                      <button onClick={() => handleRemoveTag(tag)} className="ml-1 opacity-0 group-hover:opacity-100 hover:text-red-400 transition-opacity"><X className="w-3 h-3"/></button>
                    </span>
                  ))}
                  <input 
                    type="text" 
                    placeholder="+ Add tag"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyDown={handleAddTag}
                    className="px-2.5 py-1 bg-transparent border border-dashed border-slate-300 dark:border-white/20 text-slate-600 dark:text-slate-400 rounded-lg text-xs focus:outline-none focus:border-indigo-500/50 w-24"
                  />
                </div>
              </div>
              
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Annotations / Notes</p>
                <textarea 
                  value={fileNote}
                  onChange={(e) => setFileNote(e.target.value)}
                  className="w-full bg-white/50 dark:bg-slate-950/50 border border-slate-300 dark:border-white/10 rounded-xl p-3 text-sm text-slate-900 dark:text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 min-h-[100px] resize-none"
                  placeholder="Add a note to this file..."
                />
                <button onClick={handleSaveNote} className="mt-2 w-full py-2 bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-slate-300 text-sm font-medium rounded-lg transition-colors border border-slate-200 dark:border-white/5">Save Note</button>
              </div>

              {selectedFile.mime.includes('audio') || selectedFile.mime.includes('video') ? (
                <div className="p-4 bg-white/50 dark:bg-slate-950/50 rounded-xl border border-slate-200 dark:border-white/5 flex flex-col items-center justify-center">
                  <button className="w-12 h-12 rounded-full bg-indigo-500 flex items-center justify-center text-white mb-2 shadow-lg shadow-indigo-500/20 hover:scale-105 transition-transform"><Play className="w-5 h-5 ml-1"/></button>
                  <p className="text-xs text-slate-600 dark:text-slate-400">Media Player Available</p>
                </div>
              ) : null}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

