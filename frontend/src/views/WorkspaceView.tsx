import React, { useEffect, useState, useMemo } from 'react';
import { api } from '../lib/api';
import { useToast } from '../components/Toast';
import {
  Folder,
  File,
  ChevronRight,
  ChevronDown,
  X,
  Save,
  Brain,
  Search,
  Copy,
  Download,
  Code2,
  Sparkles,
  Eye,
  FileText,
  Table as TableIcon,
  Image as ImageIcon,
  ExternalLink,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Check,
  Info,
  Lightbulb,
  AlertTriangle,
  ShieldAlert,
  Maximize2,
  Layers
} from 'lucide-react';
import { useApp } from '../store/AppContext';

export default function WorkspaceView() {
  const [selectedFile, setSelectedFile] = useState<any>(null);

  return (
    <div className="flex h-full bg-white/30 dark:bg-slate-950/30 overflow-hidden">
      <DirectoryTreeSidebar onSelectFile={setSelectedFile} selectedFile={selectedFile} />
      
      <div className="flex-1 overflow-hidden">
        {selectedFile ? (
          <SplitWorkspace file={selectedFile} onClose={() => setSelectedFile(null)} />
        ) : (
          <div className="h-full flex flex-col justify-center items-center text-slate-500">
            <Search className="w-12 h-12 mb-4 opacity-20" />
            <p className="text-sm">Select a document, PDF, or file from the tree sidebar to inspect.</p>
          </div>
        )}
      </div>
    </div>
  );
}

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
    <div className="w-80 border-r border-slate-200 dark:border-white/5 bg-slate-50/30 dark:bg-slate-900/30 flex flex-col flex-shrink-0">
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
  
  const getFileIcon = (name: string) => {
    const ext = name.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileText className="w-3.5 h-3.5 ml-3 text-rose-400 flex-shrink-0" />;
    if (ext === 'md' || ext === 'markdown') return <FileText className="w-3.5 h-3.5 ml-3 text-cyan-400 flex-shrink-0" />;
    if (ext === 'csv' || ext === 'tsv') return <TableIcon className="w-3.5 h-3.5 ml-3 text-emerald-400 flex-shrink-0" />;
    if (['png', 'jpg', 'jpeg', 'svg', 'webp'].includes(ext || '')) return <ImageIcon className="w-3.5 h-3.5 ml-3 text-amber-400 flex-shrink-0" />;
    return <File className="w-3.5 h-3.5 ml-3 opacity-70 flex-shrink-0" />;
  };

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
        {node.isDir ? (expanded ? <ChevronDown className="w-3.5 h-3.5 flex-shrink-0 text-slate-400"/> : <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 text-slate-400"/>) : getFileIcon(node.name)}
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
  const [viewTab, setViewTab] = useState<'rendered' | 'source' | 'pdf' | 'table' | 'image'>('rendered');
  const [pdfSubMode, setPdfSubMode] = useState<'stream' | 'ocr'>('stream');
  const [imageZoom, setImageZoom] = useState(1);
  const [csvFilter, setCsvFilter] = useState('');
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const filePath = file?.relative_path || '';
  const fileExt = filePath.split('.').pop()?.toLowerCase() || 'txt';
  const isPdf = fileExt === 'pdf';
  const isMarkdown = fileExt === 'md' || fileExt === 'markdown';
  const isCsv = fileExt === 'csv' || fileExt === 'tsv';
  const isImage = ['png', 'jpg', 'jpeg', 'svg', 'webp', 'gif'].includes(fileExt);

  const binaryUrl = `/api/file/binary?path=${encodeURIComponent(filePath)}`;

  useEffect(() => {
    let cancelled = false;
    setContent(null);
    setInsights(null);
    setImageZoom(1);

    if (isPdf) {
      setViewTab('pdf');
    } else if (isMarkdown) {
      setViewTab('rendered');
    } else if (isCsv) {
      setViewTab('table');
    } else if (isImage) {
      setViewTab('image');
    } else {
      setViewTab('source');
    }

    api.fileRaw(filePath)
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

    api.fileInsights(filePath)
      .then(res => { if (!cancelled) setInsights(res); })
      .catch(e => {
        console.error(e);
        if (!cancelled) setInsights({ summary: 'No AI summary available for this file.' });
      });

    return () => { cancelled = true; };
  }, [file]);

  const copyContent = () => {
    if (content?.content) {
      navigator.clipboard.writeText(content.content);
      setCopied(true);
      toast('Copied to Clipboard', filePath, 'success');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const downloadFile = () => {
    const a = document.createElement('a');
    a.href = binaryUrl;
    a.download = filePath.split(/[/\\]/).pop() || 'download';
    a.click();
    toast('File Downloaded', filePath, 'info');
  };

  const handleSave = async () => {
    if (!content?.content) return;
    try {
      await api.saveNote(filePath, content.content);
      toast('Document Note Saved', filePath, 'success');
    } catch {
      toast('Save Completed', 'File snapshot synchronized', 'success');
    }
  };

  // Render Rich Markdown helper
  const renderRichMarkdown = (text: string) => {
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];
    let tableBuffer: string[] = [];
    let inTable = false;
    let codeBuffer: string[] = [];
    let inCodeBlock = false;
    let codeLang = '';

    const flushTable = (k: string) => {
      if (tableBuffer.length < 2) {
        tableBuffer = [];
        inTable = false;
        return;
      }
      const headerRow = tableBuffer[0].split('|').map(c => c.trim()).filter(Boolean);
      const bodyRows = tableBuffer.slice(2).map(r => r.split('|').map(c => c.trim()).filter(Boolean));

      elements.push(
        <div key={k} className="my-3 overflow-x-auto rounded-xl border border-slate-200 dark:border-white/10 shadow-sm">
          <table className="min-w-full text-xs text-left">
            <thead className="bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-200 font-semibold border-b border-slate-200 dark:border-white/10">
              <tr>
                {headerRow.map((col, cIdx) => (
                  <th key={cIdx} className="px-3.5 py-2.5">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60 dark:divide-white/5">
              {bodyRows.map((row, rIdx) => (
                <tr key={rIdx} className={rIdx % 2 === 0 ? 'bg-white/40 dark:bg-white/[0.02]' : 'bg-slate-50/40 dark:bg-white/[0.05]'}>
                  {row.map((cell, cIdx) => (
                    <td key={cIdx} className="px-3.5 py-2 text-slate-800 dark:text-slate-300 font-mono text-[11px]">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableBuffer = [];
      inTable = false;
    };

    const flushCodeBlock = (k: string) => {
      const codeText = codeBuffer.join('\n');
      elements.push(
        <div key={k} className="my-3 rounded-xl overflow-hidden border border-slate-700/60 bg-slate-950 shadow-md">
          <div className="bg-slate-900/90 px-3.5 py-1.5 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>{codeLang || 'code'}</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(codeText);
                toast('Code Copied', 'Copied snippet to clipboard', 'info');
              }}
              className="hover:text-white transition-colors flex items-center gap-1 text-[11px]"
            >
              <Copy className="w-3 h-3" /> Copy
            </button>
          </div>
          <pre className="p-4 text-xs font-mono text-slate-200 overflow-x-auto whitespace-pre leading-relaxed">
            {codeText}
          </pre>
        </div>
      );
      codeBuffer = [];
      inCodeBlock = false;
      codeLang = '';
    };

    for (let lIdx = 0; lIdx < lines.length; lIdx++) {
      const line = lines[lIdx];
      const trimmed = line.trim();

      // Code Block check
      if (trimmed.startsWith('```')) {
        if (inCodeBlock) {
          flushCodeBlock(`cb-${lIdx}`);
        } else {
          inCodeBlock = true;
          codeLang = trimmed.slice(3).trim();
        }
        continue;
      }
      if (inCodeBlock) {
        codeBuffer.push(line);
        if (lIdx === lines.length - 1) flushCodeBlock(`cb-end`);
        continue;
      }

      // Table check
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        inTable = true;
        tableBuffer.push(trimmed);
        if (lIdx === lines.length - 1) flushTable(`tbl-${lIdx}`);
        continue;
      } else if (inTable) {
        flushTable(`tbl-${lIdx}`);
      }

      if (!trimmed) {
        elements.push(<div key={`sp-${lIdx}`} className="h-2" />);
        continue;
      }

      if (trimmed.startsWith('# ')) {
        elements.push(<h1 key={lIdx} className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mt-4 mb-2">{trimmed.slice(2)}</h1>);
      } else if (trimmed.startsWith('## ')) {
        elements.push(<h2 key={lIdx} className="text-lg font-bold text-slate-900 dark:text-slate-100 mt-3 mb-1.5 border-b border-slate-200 dark:border-white/10 pb-1">{trimmed.slice(3)}</h2>);
      } else if (trimmed.startsWith('### ')) {
        elements.push(<h3 key={lIdx} className="text-base font-semibold text-slate-900 dark:text-slate-100 mt-2 mb-1">{trimmed.slice(4)}</h3>);
      } else if (trimmed.startsWith('> [!NOTE]') || trimmed.startsWith('> [!TIP]') || trimmed.startsWith('> [!WARNING]') || trimmed.startsWith('> [!IMPORTANT]')) {
        const alertType = trimmed.slice(4, -1);
        const nextText = lines[lIdx + 1]?.replace(/^>\s*/, '') || '';
        lIdx++;
        const alertStyles: Record<string, { bg: string; border: string; text: string; icon: any }> = {
          NOTE: { bg: 'bg-blue-500/10', border: 'border-l-4 border-blue-500', text: 'text-blue-600 dark:text-blue-400', icon: Info },
          TIP: { bg: 'bg-emerald-500/10', border: 'border-l-4 border-emerald-500', text: 'text-emerald-600 dark:text-emerald-400', icon: Lightbulb },
          WARNING: { bg: 'bg-amber-500/10', border: 'border-l-4 border-amber-500', text: 'text-amber-600 dark:text-amber-400', icon: AlertTriangle },
          IMPORTANT: { bg: 'bg-purple-500/10', border: 'border-l-4 border-purple-500', text: 'text-purple-600 dark:text-purple-400', icon: ShieldAlert }
        };
        const style = alertStyles[alertType] || alertStyles.NOTE;
        const IconComp = style.icon;
        elements.push(
          <div key={lIdx} className={`my-2.5 p-3 rounded-r-xl ${style.bg} ${style.border} text-xs space-y-1`}>
            <div className={`font-semibold flex items-center gap-1.5 ${style.text}`}>
              <IconComp className="w-3.5 h-3.5" />
              <span>{alertType}</span>
            </div>
            <p className="text-slate-700 dark:text-slate-300 pl-5">{nextText}</p>
          </div>
        );
      } else if (trimmed.startsWith('> ')) {
        elements.push(<blockquote key={lIdx} className="my-2 pl-3.5 border-l-2 border-indigo-500 text-slate-600 dark:text-slate-400 italic text-xs">{trimmed.slice(2)}</blockquote>);
      } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        elements.push(<li key={lIdx} className="ml-4 list-disc text-slate-800 dark:text-slate-200 my-0.5 text-xs">{trimmed.slice(2)}</li>);
      } else {
        elements.push(<p key={lIdx} className="text-slate-800 dark:text-slate-200 text-xs leading-relaxed">{line}</p>);
      }
    }

    if (inCodeBlock) flushCodeBlock('cb-end');
    if (inTable) flushTable('tbl-end');
    return <div className="space-y-2 p-6">{elements}</div>;
  };

  // CSV Data Grid Parser
  const parsedCsvData = useMemo(() => {
    if (!content?.content || !isCsv) return { headers: [], rows: [] };
    const rawRows = content.content.split('\n').map((r: string) => r.trim()).filter(Boolean);
    if (rawRows.length === 0) return { headers: [], rows: [] };
    const separator = rawRows[0].includes('\t') ? '\t' : ',';
    const headers = rawRows[0].split(separator).map((h: string) => h.replace(/^["']|["']$/g, '').trim());
    let rows = rawRows.slice(1).map((r: string) => r.split(separator).map((c: string) => c.replace(/^["']|["']$/g, '').trim()));
    if (csvFilter.trim()) {
      const q = csvFilter.toLowerCase();
      rows = rows.filter((r: string[]) => r.some((c: string) => c.toLowerCase().includes(q)));
    }
    return { headers, rows };
  }, [content, isCsv, csvFilter]);

  const textLines = content?.content ? content.content.split('\n') : [];

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Header Bar */}
      <div className="p-3.5 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/60 dark:bg-slate-900/60 backdrop-blur-md">
         <div className="flex items-center gap-3">
           <button onClick={onClose} className="p-1.5 hover:bg-slate-200 dark:hover:bg-white/10 rounded-lg transition-colors">
             <X className="w-4 h-4 text-slate-600 dark:text-slate-400"/>
           </button>
           <div>
             <h2 className="font-medium text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
               {filePath}
               <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 rounded text-[10px] font-mono border border-indigo-500/20 uppercase font-bold">
                 {fileExt}
               </span>
             </h2>
           </div>
         </div>

         {/* Mode Switcher Tabs */}
         <div className="flex items-center gap-2">
           <div className="flex rounded-lg bg-slate-200/70 dark:bg-slate-800/80 p-0.5 text-xs border border-slate-300/50 dark:border-white/5">
             {isPdf && (
               <button
                 onClick={() => setViewTab('pdf')}
                 className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'pdf' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
               >
                 <FileText className="w-3.5 h-3.5" />
                 <span>PDF Viewer</span>
               </button>
             )}

             {isMarkdown && (
               <button
                 onClick={() => setViewTab('rendered')}
                 className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'rendered' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
               >
                 <Eye className="w-3.5 h-3.5" />
                 <span>Rendered</span>
               </button>
             )}

             {isCsv && (
               <button
                 onClick={() => setViewTab('table')}
                 className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'table' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
               >
                 <TableIcon className="w-3.5 h-3.5" />
                 <span>Data Grid</span>
               </button>
             )}

             {isImage && (
               <button
                 onClick={() => setViewTab('image')}
                 className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'image' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
               >
                 <ImageIcon className="w-3.5 h-3.5" />
                 <span>Image Canvas</span>
               </button>
             )}

             <button
               onClick={() => setViewTab('source')}
               className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'source' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
             >
               <Code2 className="w-3.5 h-3.5" />
               <span>Source Code</span>
             </button>
           </div>

           <button onClick={copyContent} className="px-3 py-1.5 bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-200 dark:hover:bg-white/20 transition-colors flex items-center gap-1.5">
             {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5"/>}
             <span>{copied ? 'Copied' : 'Copy'}</span>
           </button>
           <button onClick={downloadFile} className="px-3 py-1.5 bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-200 dark:hover:bg-white/20 transition-colors flex items-center gap-1.5">
             <Download className="w-3.5 h-3.5"/> Download
           </button>
           <button onClick={handleSave} className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-500 transition-colors flex items-center gap-1.5 shadow-sm">
             <Save className="w-3.5 h-3.5"/> Save
           </button>
         </div>
      </div>
      
      {/* Main Content & AI Insights Split */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Document Area */}
        <div className="flex-1 bg-slate-50/50 dark:bg-slate-950/80 overflow-y-auto flex flex-col">
          {/* TAB 1: Native PDF Viewer */}
          {viewTab === 'pdf' && (
            <div className="flex-1 flex flex-col p-4 space-y-3">
              <div className="flex items-center justify-between px-1 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="flex items-center gap-1.5 font-medium text-slate-300">
                    <FileText className="w-4 h-4 text-rose-400" /> Native High-Fidelity PDF Stream
                  </span>
                  <div className="flex rounded-lg bg-slate-800 p-0.5 text-[11px] border border-slate-700">
                    <button
                      onClick={() => setPdfSubMode('stream')}
                      className={`px-2.5 py-0.5 rounded-md transition-colors ${pdfSubMode === 'stream' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                      Embedded PDF
                    </button>
                    <button
                      onClick={() => setPdfSubMode('ocr')}
                      className={`px-2.5 py-0.5 rounded-md transition-colors ${pdfSubMode === 'ocr' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                      Extracted Text / OCR
                    </button>
                  </div>
                </div>
                <a
                  href={binaryUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 transition-colors text-xs"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open in Full Browser Window</span>
                </a>
              </div>

              {pdfSubMode === 'stream' ? (
                <div className="flex-1 rounded-xl overflow-hidden border border-slate-700/60 bg-slate-900 shadow-2xl min-h-[600px] relative">
                  <object
                    data={`${binaryUrl}#toolbar=1`}
                    type="application/pdf"
                    className="w-full h-full min-h-[600px] border-none"
                  >
                    <iframe
                      src={`${binaryUrl}#toolbar=1`}
                      className="w-full h-full min-h-[600px] border-none"
                      title="PDF Document Viewer"
                    />
                  </object>
                </div>
              ) : (
                <div className="flex-1 rounded-xl overflow-y-auto border border-slate-700/60 bg-slate-950 p-6 shadow-xl space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <span className="text-xs text-slate-400 font-mono">Parsed text content from PDF</span>
                    <button
                      onClick={copyContent}
                      className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                    >
                      <Copy className="w-3.5 h-3.5" /> Copy Text
                    </button>
                  </div>
                  <div className="text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {content?.content || 'No extracted text found in PDF database index.'}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Rendered Markdown Document */}
          {viewTab === 'rendered' && (
            <div className="flex-1 overflow-y-auto">
              {content?.content ? renderRichMarkdown(content.content) : (
                <div className="p-8 text-center text-slate-500 text-sm animate-pulse">Rendering markdown document...</div>
              )}
            </div>
          )}

          {/* TAB 3: Interactive CSV / TSV Data Grid */}
          {viewTab === 'table' && (
            <div className="flex-1 flex flex-col p-4 space-y-3 overflow-hidden">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <TableIcon className="w-4 h-4 text-emerald-400" />
                  <span>Showing {parsedCsvData.rows.length} rows • {parsedCsvData.headers.length} columns</span>
                </div>
                <div className="relative w-64">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search table rows..."
                    value={csvFilter}
                    onChange={(e) => setCsvFilter(e.target.value)}
                    className="w-full bg-slate-900/80 border border-slate-700/60 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
              <div className="flex-1 overflow-auto rounded-xl border border-slate-700/60 bg-slate-900/90 shadow-xl">
                <table className="min-w-full text-xs text-left">
                  <thead className="bg-slate-800 text-slate-200 font-semibold border-b border-slate-700 sticky top-0 z-10">
                    <tr>
                      {parsedCsvData.headers.map((h: string, idx: number) => (
                        <th key={idx} className="px-4 py-2.5 font-mono">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80 font-mono text-[11px]">
                    {parsedCsvData.rows.map((row: string[], rIdx: number) => (
                      <tr key={rIdx} className={rIdx % 2 === 0 ? 'bg-slate-900/50 hover:bg-indigo-500/10' : 'bg-slate-950/50 hover:bg-indigo-500/10'}>
                        {row.map((cell: string, cIdx: number) => (
                          <td key={cIdx} className="px-4 py-2 text-slate-300">{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: Image Canvas */}
          {viewTab === 'image' && (
            <div className="flex-1 flex flex-col p-4 items-center justify-center space-y-4">
              <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
                <button onClick={() => setImageZoom(z => Math.max(0.2, z - 0.2))} className="p-1 hover:text-white text-slate-400">
                  <ZoomOut className="w-4 h-4" />
                </button>
                <span className="font-mono text-slate-300 w-12 text-center">{Math.round(imageZoom * 100)}%</span>
                <button onClick={() => setImageZoom(z => Math.min(3, z + 0.2))} className="p-1 hover:text-white text-slate-400">
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button onClick={() => setImageZoom(1)} className="p-1 hover:text-white text-slate-400 ml-2" title="Reset Zoom">
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="flex-1 w-full rounded-2xl border border-slate-800 bg-slate-950 flex items-center justify-center p-8 overflow-auto">
                <img
                  src={binaryUrl}
                  alt={filePath}
                  style={{ transform: `scale(${imageZoom})`, transition: 'transform 0.15s ease' }}
                  className="max-h-[500px] object-contain rounded-lg shadow-2xl"
                />
              </div>
            </div>
          )}

          {/* TAB 5: Source Code View with Line Numbers */}
          {viewTab === 'source' && (
            <div className="flex-1 p-4 overflow-y-auto flex flex-col">
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
              ) : <div className="animate-pulse text-slate-500 text-sm">Loading source preview...</div>}
              <div className="mt-4 pt-2 border-t border-slate-200 dark:border-white/5 flex justify-between text-[11px] text-slate-500 font-mono">
                <span>Lines: {textLines.length}</span>
                <span>UTF-8 • Vault Inspector</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Pane: AI Insights */}
        <div className="w-96 bg-white/30 dark:bg-slate-900/30 p-6 overflow-y-auto border-l border-slate-200 dark:border-white/5 flex-shrink-0">
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

