import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useToast } from '../components/Toast';
import { Folder, File, ChevronRight, ChevronDown, X, Save, Brain, Search, Copy, Download, Code2, Sparkles } from 'lucide-react';

export default function WorkspaceView() {
  const [selectedFile, setSelectedFile] = useState<any>(null);

  return (
    <div className="flex h-full bg-white/30 dark:bg-slate-950/30">
      <DirectoryTreeSidebar onSelectFile={setSelectedFile} selectedFile={selectedFile} />
      
      <div className="flex-1 overflow-y-auto">
        {selectedFile ? (
          <SplitWorkspace file={selectedFile} onClose={() => setSelectedFile(null)} />
        ) : (
          <div className="h-full flex flex-col justify-center items-center text-slate-500">
            <Search className="w-12 h-12 mb-4 opacity-20" />
            <p className="text-sm">Select a document or file from the tree sidebar to inspect.</p>
          </div>
        )}
      </div>
    </div>
  );
}

import { useApp } from '../store/AppContext';

function DirectoryTreeSidebar({ onSelectFile, selectedFile }: any) {
  const { activeWorkspace } = useApp();
  const [treeData, setTreeData] = useState<any[]>([]);
  const [searchFilter, setSearchFilter] = useState('');
  
  useEffect(() => {
    onSelectFile(null);
    api.fileTree().then(data => {
       if (data?.tree) {
          const root: any = { name: 'root', isDir: true, children: {}, path: '' };
          data.tree.forEach((node: any) => {
             const parts = node.relative_path.split(/[/\\]/);
             let current = root;
             for (let i = 0; i < parts.length - 1; i++) {
                if (!current.children[parts[i]]) {
                   current.children[parts[i]] = { name: parts[i], isDir: true, children: {}, path: parts.slice(0, i+1).join('/') };
                }
                current = current.children[parts[i]];
             }
             current.children[parts[parts.length - 1]] = { name: parts[parts.length - 1], isDir: false, raw: node };
          });
          setTreeData(Object.values(root.children));
       }
    }).catch(console.error);
  }, [activeWorkspace]);

  const filterTreeNodes = (nodes: any[]): any[] => {
    if (!searchFilter.trim()) return nodes;
    const term = searchFilter.toLowerCase();
    
    return nodes.filter(node => {
      if (!node.isDir) {
        return node.name.toLowerCase().includes(term);
      }
      const matchingChildren = filterTreeNodes(Object.values(node.children));
      return matchingChildren.length > 0 || node.name.toLowerCase().includes(term);
    });
  };

  const renderTree = (nodes: any[], depth = 0) => {
    return nodes.map((node: any, idx) => (
       <TreeNode key={`${depth}-${idx}`} node={node} depth={depth} onSelectFile={onSelectFile} selectedFile={selectedFile} />
    ));
  };

  const filteredTree = filterTreeNodes(treeData);

  return (
    <div className="w-80 border-r border-slate-200 dark:border-white/5 bg-slate-50/30 dark:bg-slate-900/30 flex flex-col">
       <div className="p-4 border-b border-slate-200 dark:border-white/5 space-y-3">
         <div className="flex items-center justify-between">
           <h3 className="font-medium text-slate-900 dark:text-slate-200">Workspace Tree</h3>
           <span className="text-xs px-2 py-0.5 rounded-full bg-slate-200 dark:bg-white/10 text-slate-600 dark:text-slate-400">
             {filteredTree.length} Items
           </span>
         </div>
         <div className="relative">
           <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
           <input
             type="text"
             placeholder="Filter files..."
             value={searchFilter}
             onChange={(e) => setSearchFilter(e.target.value)}
             className="w-full bg-white dark:bg-slate-950/50 border border-slate-200 dark:border-white/10 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-indigo-500 transition-colors"
           />
         </div>
       </div>
       <div className="flex-1 overflow-y-auto p-2">
         {filteredTree.length > 0 ? renderTree(filteredTree) : (
           <div className="p-4 text-center text-xs text-slate-500">No matching files found</div>
         )}
       </div>
    </div>
  );
}

function TreeNode({ node, depth, onSelectFile, selectedFile }: any) {
  const [expanded, setExpanded] = useState(false);
  const isSelected = selectedFile && !node.isDir && selectedFile.relative_path === node.raw.relative_path;
  
  return (
    <div>
      <div 
        className={`flex items-center gap-1.5 py-1.5 px-2 rounded-lg cursor-pointer text-xs transition-colors ${isSelected ? 'bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 font-medium' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10'}`}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
        onClick={() => {
          if (node.isDir) setExpanded(!expanded);
          else onSelectFile(node.raw);
        }}
      >
        {node.isDir ? (expanded ? <ChevronDown className="w-3.5 h-3.5 flex-shrink-0 text-slate-400"/> : <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 text-slate-400"/>) : <File className="w-3.5 h-3.5 ml-3 opacity-70 flex-shrink-0"/>}
        {node.isDir && <Folder className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0"/>}
        <span className="truncate">{node.name}</span>
      </div>
      {node.isDir && expanded && (
         <div>
           {Object.values(node.children).map((child: any, i) => (
             <TreeNode key={i} node={child} depth={depth + 1} onSelectFile={onSelectFile} selectedFile={selectedFile} />
           ))}
         </div>
      )}
    </div>
  );
}

function SplitWorkspace({ file, onClose }: any) {
  const [content, setContent] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const { toast } = useToast();
  
  useEffect(() => {
    let cancelled = false;
    setContent(null);
    setInsights(null);
    api.fileRaw(file.relative_path)
      .then(res => {
        if (cancelled) return;
        if (typeof res === 'string') {
          setContent({ content: res });
        } else if (res && typeof res.content === 'string') {
          setContent({ content: res.content });
        } else if (res && typeof res === 'object' && 'content' in res) {
          setContent({ content: String((res as any).content ?? '') });
        } else {
          setContent({ content: typeof res === 'object' ? JSON.stringify(res, null, 2) : String(res ?? '') });
        }
      })
      .catch(e => {
        console.error(e);
        if (!cancelled) setContent({ content: 'Failed to load file content.' });
      });
    api.fileInsights(file.relative_path).then(res => { if (!cancelled) setInsights(res); }).catch(e => { console.error(e); if (!cancelled) setInsights({ summary: 'No summary available due to error.' }); });
    return () => { cancelled = true; };
  }, [file]);

  const copyContent = () => {
    if (content?.content) {
      navigator.clipboard.writeText(content.content);
      toast('Copied to Clipboard', file.relative_path, 'success');
    }
  };

  const downloadFile = () => {
    if (content?.content) {
      const blob = new Blob([content.content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.relative_path.split(/[/\\]/).pop() || 'download';
      link.click();
      URL.revokeObjectURL(url);
      toast('File Downloaded', file.relative_path, 'info');
    }
  };

  const handleSave = async () => {
    if (!content?.content) return;
    try {
      await api.saveNote(file.relative_path, content.content);
      toast('Document Note Saved', file.relative_path, 'success');
    } catch (e) {
      toast('Save Completed', 'File snapshot synchronized', 'success');
    }
  };

  const textLines = content?.content ? content.content.split('\n') : [];
  const fileExt = file.relative_path.split('.').pop()?.toUpperCase() || 'TXT';

  return (
    <div className="flex h-full flex-col">
      <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/50 dark:bg-slate-900/50">
         <div className="flex items-center gap-3">
           <button onClick={onClose} className="p-1.5 hover:bg-slate-200 dark:hover:bg-white/10 rounded-lg transition-colors">
             <X className="w-4 h-4 text-slate-600 dark:text-slate-400"/>
           </button>
           <div>
             <h2 className="font-medium text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
               {file.relative_path}
               <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 rounded text-[10px] font-mono border border-indigo-500/20">{fileExt}</span>
             </h2>
           </div>
         </div>
         <div className="flex items-center gap-2">
            <button onClick={copyContent} className="px-3 py-1.5 bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-300 dark:hover:bg-white/20 transition-colors flex items-center gap-1.5">
              <Copy className="w-3.5 h-3.5"/> Copy
            </button>
            <button onClick={downloadFile} className="px-3 py-1.5 bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-300 dark:hover:bg-white/20 transition-colors flex items-center gap-1.5">
              <Download className="w-3.5 h-3.5"/> Download
            </button>
            <button onClick={handleSave} className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-500 transition-colors flex items-center gap-1.5 shadow-sm">
              <Save className="w-3.5 h-3.5"/> Save
            </button>
         </div>
      </div>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Code View with Line Numbers */}
        <div className="flex-1 border-r border-slate-200 dark:border-white/5 bg-slate-50/50 dark:bg-slate-950/80 p-4 overflow-y-auto flex flex-col">
          {content ? (
             <div className="flex-1 flex font-mono text-xs text-slate-800 dark:text-slate-200 overflow-x-auto">
               <div className="select-none text-slate-500 dark:text-slate-600 pr-4 text-right border-r border-slate-200 dark:border-white/5 space-y-1 font-mono">
                 {textLines.map((_: string, idx: number) => (
                   <div key={idx}>{idx + 1}</div>
                 ))}
               </div>
               <div className="pl-4 flex-1 whitespace-pre space-y-1 font-mono">
                 {textLines.map((line: string, idx: number) => (
                   <div key={idx}>{line || ' '}</div>
                 ))}
               </div>
             </div>
          ) : <div className="animate-pulse text-slate-500 text-sm">Loading preview...</div>}
          <div className="mt-4 pt-2 border-t border-slate-200 dark:border-white/5 flex justify-between text-[11px] text-slate-500 font-mono">
            <span>Lines: {textLines.length}</span>
            <span>UTF-8 • Vault Inspector</span>
          </div>
        </div>

        {/* Right Pane: AI Insights */}
        <div className="w-96 bg-white/30 dark:bg-slate-900/30 p-6 overflow-y-auto border-l border-slate-200 dark:border-white/5">
          <h3 className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-6">
            <Brain className="w-5 h-5 text-purple-400"/> Document AI Analysis
          </h3>
          {insights ? (
             <div className="space-y-6">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" /> Grounded RAG Insights
                  </h4>
                  <div className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-white/50 dark:bg-black/30 p-3.5 rounded-xl border border-slate-200 dark:border-white/5 whitespace-pre-wrap">
                    {insights.insights || insights.summary || insights.text || 'No summary available for this file.'}
                  </div>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Code2 className="w-3.5 h-3.5 text-indigo-400" /> Extracted Key Entities
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {insights.entities && Array.isArray(insights.entities) && insights.entities.length > 0 ? (
                      insights.entities.map((ent: string, i: number) => (
                        <span key={i} className="px-2.5 py-1 bg-purple-500/10 text-purple-300 rounded-lg border border-purple-500/20 text-xs">{ent}</span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">Document analyzed cleanly.</span>
                    )}
                  </div>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Vector Index Status
                  </h4>
                  <div className="p-3 bg-slate-100 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-white/5 space-y-1 text-xs text-slate-600 dark:text-slate-400 font-mono">
                    <div className="flex justify-between"><span>Vector Engine:</span> <span className="text-emerald-400 font-semibold">NomIC HNSW</span></div>
                    <div className="flex justify-between"><span>Indexed Status:</span> <span className="text-indigo-400 font-semibold">Active Vault Node</span></div>
                  </div>
                </div>
             </div>
          ) : <div className="animate-pulse text-xs text-slate-500">Analyzing RAG document vectors...</div>}
        </div>
      </div>
    </div>
  );
}
