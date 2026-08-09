import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { Folder, File, ChevronRight, ChevronDown, X, Save, Brain, Search } from 'lucide-react';

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
            <p>Select a file from the workspace tree to view it.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function DirectoryTreeSidebar({ onSelectFile, selectedFile }: any) {
  const [treeData, setTreeData] = useState<any[]>([]);
  
  useEffect(() => {
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
  }, []);

  const renderTree = (nodes: any[], depth = 0) => {
    return nodes.map((node: any, idx) => (
       <TreeNode key={`${depth}-${idx}`} node={node} depth={depth} onSelectFile={onSelectFile} selectedFile={selectedFile} />
    ));
  };

  return (
    <div className="w-72 border-r border-slate-200 dark:border-white/5 bg-slate-50/30 dark:bg-slate-900/30 flex flex-col">
       <div className="p-4 border-b border-slate-200 dark:border-white/5">
         <h3 className="font-medium text-slate-900 dark:text-slate-200">Workspace</h3>
       </div>
       <div className="flex-1 overflow-y-auto p-2">
         {renderTree(treeData)}
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
        className={`flex items-center gap-1.5 py-1.5 px-2 rounded-lg cursor-pointer text-sm transition-colors ${isSelected ? 'bg-indigo-500/20 text-indigo-700 dark:text-indigo-300' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10'}`}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
        onClick={() => {
          if (node.isDir) setExpanded(!expanded);
          else onSelectFile(node.raw);
        }}
      >
        {node.isDir ? (expanded ? <ChevronDown className="w-4 h-4 flex-shrink-0"/> : <ChevronRight className="w-4 h-4 flex-shrink-0"/>) : <File className="w-4 h-4 ml-4 opacity-70 flex-shrink-0"/>}
        {node.isDir && <Folder className="w-4 h-4 text-indigo-400 flex-shrink-0"/>}
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
  
  useEffect(() => {
    let cancelled = false;
    setContent(null);
    setInsights(null);
    api.fileRaw(file.relative_path).then(res => { if (!cancelled) setContent(res); }).catch(e => { console.error(e); if (!cancelled) setContent('Failed to load file content.'); });
    api.fileInsights(file.relative_path).then(res => { if (!cancelled) setInsights(res); }).catch(e => { console.error(e); if (!cancelled) setInsights({ error: true }); });
    return () => { cancelled = true; };
  }, [file]);

  return (
    <div className="flex h-full flex-col">
      <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/50 dark:bg-slate-900/50">
         <div className="flex items-center gap-3">
           <button onClick={onClose} className="p-1 hover:bg-slate-200 dark:hover:bg-white/10 rounded"><X className="w-5 h-5 text-slate-600 dark:text-slate-400"/></button>
           <h2 className="font-medium text-slate-900 dark:text-slate-100">{file.relative_path}</h2>
         </div>
         <div className="flex items-center gap-2">
            <button className="px-3 py-1.5 bg-indigo-500 text-white rounded-lg text-sm hover:bg-indigo-600 flex items-center gap-1"><Save className="w-4 h-4"/> Save</button>
         </div>
      </div>
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Preview */}
        <div className="flex-1 border-r border-slate-200 dark:border-white/5 bg-slate-50/50 dark:bg-slate-950/50 p-6 overflow-y-auto">
          {content ? (
             <textarea 
               className="w-full h-full bg-transparent resize-none outline-none font-mono text-sm text-slate-800 dark:text-slate-200"
               value={content.content || ''}
               readOnly
             />
          ) : <div className="animate-pulse text-slate-500">Loading preview...</div>}
        </div>
        {/* Right Pane: AI Insights */}
        <div className="w-96 bg-white/30 dark:bg-slate-900/30 p-6 overflow-y-auto border-l border-slate-200 dark:border-white/5">
          <h3 className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-6"><Brain className="w-5 h-5 text-purple-500"/> Document AI</h3>
          {insights ? (
             <div className="space-y-6">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Summary</h4>
                  <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed bg-white/50 dark:bg-black/20 p-3 rounded-lg border border-slate-200 dark:border-white/5">{insights.summary || 'No summary available.'}</p>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Extracted Entities</h4>
                  <div className="flex flex-wrap gap-2">
                    {insights.entities?.length ? insights.entities.map((ent: string, i: number) => (
                      <span key={i} className="px-2 py-1 bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded border border-purple-500/20 text-xs">{ent}</span>
                    )) : <span className="text-sm text-slate-500">None detected.</span>}
                  </div>
                </div>
             </div>
          ) : <div className="animate-pulse text-sm text-slate-500">Analyzing document...</div>}
        </div>
      </div>
    </div>
  );
}
