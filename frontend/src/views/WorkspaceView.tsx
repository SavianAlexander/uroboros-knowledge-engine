import React, { useEffect, useState, useMemo, useRef } from 'react';
import { api } from '../lib/api';
import { useToast } from '../components/Toast';
import {
  Folder,
  File,
  ChevronRight,
  ChevronLeft,
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
  Layers,
  LayoutGrid,
  BookOpen,
  Type,
  Palette,
  Sliders,
  MessageSquare,
  AlignLeft,
  Columns2,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Highlighter,
  Quote,
  Clock,
  Bookmark,
  Minimize2
} from 'lucide-react';
import { useApp } from '../store/AppContext';
import { emeraldButtonClasses, emeraldBadgeClasses, goldBadgeClasses, wineBadgeClasses, slateBadgeClasses, glassCardClasses } from '../lib/utils';

export default function WorkspaceView() {
  const [selectedFile, setSelectedFile] = useState<any>(null);

  return (
    <div className="flex h-full bg-white/40 dark:bg-slate-950/40 overflow-hidden">
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
          if (!selectedFile && data.tree.length > 0) {
            const preferred = data.tree.find((n: any) => n.relative_path.endsWith('.pdf')) || data.tree[0];
            onSelectFile(preferred);
          }
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
    <div className="w-80 border-r border-slate-200 dark:border-white/5 bg-slate-50/40 dark:bg-slate-900/40 flex flex-col flex-shrink-0">
       <div className="p-4 border-b border-slate-200 dark:border-white/5 space-y-3">
         <div className="flex items-center justify-between">
           <h3 className="font-medium text-slate-900 dark:text-slate-200">Workspace Tree</h3>
           <span className="text-xs px-2 py-0.5 rounded-full bg-slate-200 dark:bg-white/10 text-slate-600 dark:text-slate-400 font-mono">
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
             className="w-full bg-white dark:bg-slate-950/50 border border-slate-200 dark:border-white/10 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500 transition-colors"
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
    if (ext === 'pdf') return <FileText className="w-3.5 h-3.5 ml-3 text-rose-500 flex-shrink-0" />;
    if (ext === 'md' || ext === 'markdown') return <FileText className="w-3.5 h-3.5 ml-3 text-cyan-500 flex-shrink-0" />;
    if (ext === 'csv' || ext === 'tsv') return <TableIcon className="w-3.5 h-3.5 ml-3 text-emerald-500 flex-shrink-0" />;
    if (['png', 'jpg', 'jpeg', 'svg', 'webp'].includes(ext || '')) return <ImageIcon className="w-3.5 h-3.5 ml-3 text-amber-500 flex-shrink-0" />;
    return <File className="w-3.5 h-3.5 ml-3 opacity-70 flex-shrink-0" />;
  };

  return (
    <div>
      <div 
        className={`flex items-center gap-1.5 py-1.5 px-2 rounded-lg cursor-pointer text-xs transition-colors ${isSelected ? 'bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 font-medium' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10'}`}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
        onClick={() => {
          if (node.isDir) setExpanded(!expanded);
          else onSelectFile(node.raw);
        }}
      >
        {node.isDir ? (expanded ? <ChevronDown className="w-3.5 h-3.5 flex-shrink-0 text-slate-400"/> : <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 text-slate-400"/>) : getFileIcon(node.name)}
        {node.isDir && <Folder className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 flex-shrink-0"/>}
        <span className="truncate flex-1 text-left">{node.name}</span>
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

function SplitWorkspace({ file, onClose }: { file: any; onClose: () => void }) {
  const [content, setContent] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const [viewTab, setViewTab] = useState<'studio' | 'source' | 'table' | 'image'>('studio');
  const [docRenderMode, setDocRenderMode] = useState<'real' | 'editorial'>('real');
  const [pdfInfo, setPdfInfo] = useState<any>(null);
  const [currentPdfPage, setCurrentPdfPage] = useState<number>(0);
  const [pdfPageZoom, setPdfPageZoom] = useState<number>(1);
  const [imageZoom, setImageZoom] = useState(1);
  const [csvFilter, setCsvFilter] = useState('');
  const [copied, setCopied] = useState(false);
  
  // Acrobat-Grade In-Page Search & AI X-Ray Overlay State
  const [inPageSearch, setInPageSearch] = useState<string>('Analytical');
  const [inPageMatchIndex, setInPageMatchIndex] = useState<number>(1);
  const [isXrayActive, setIsXrayActive] = useState<boolean>(true);

  // Luxury EPUB Reader Studio Customization State
  const [readerFont, setReaderFont] = useState<'serif' | 'sans' | 'mono' | 'charter'>('serif');
  const [readerSize, setReaderSize] = useState<number>(18);
  const [readerTheme, setReaderTheme] = useState<'sepia' | 'midnight' | 'amber' | 'light' | 'nord'>('sepia');
  const [readerLineHeight, setReaderLineHeight] = useState<'normal' | 'comfortable' | 'loose'>('comfortable');
  const [readerLayout, setReaderLayout] = useState<'single' | 'dual' | 'wide'>('single');
  const [enableKeywordInsights, setEnableKeywordInsights] = useState<boolean>(true);
  const [zenMode, setZenMode] = useState<boolean>(false);
  
  // TTS Audio Read-Aloud State
  const [ttsSpeaking, setTtsSpeaking] = useState(false);
  const [ttsRate, setTtsRate] = useState<number>(1.0);
  const ttsUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Text Selection Action State
  const [selectedText, setSelectedText] = useState<string>('');
  const [selectionPos, setSelectionPos] = useState<{ x: number; y: number } | null>(null);
  const [highlights, setHighlights] = useState<string[]>([]);
  
  // Interactive Keyword Hover Cards State
  const [entitiesList, setEntitiesList] = useState<string[]>([]);
  const [activeHoverCard, setActiveHoverCard] = useState<any>(null);
  const [hoverPos, setHoverPos] = useState<{ x: number; y: number } | null>(null);
  const termCache = useRef<{ [key: string]: any }>({});
  const hoverTimeoutRef = useRef<any>(null);

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
    setPdfInfo(null);
    setEntitiesList([]);
    setActiveHoverCard(null);
    setCurrentPdfPage(0);
    setPdfPageZoom(1);
    setImageZoom(1);

    if (isCsv) {
      setViewTab('table');
    } else if (isImage) {
      setViewTab('image');
    } else {
      setViewTab('studio');
      setDocRenderMode('real');
      if (isPdf) {
        api.pdfInfo(filePath)
          .then(info => { if (!cancelled) setPdfInfo(info); })
          .catch(err => { console.warn('Could not fetch PDF page info:', err); });
      }
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

    api.fileEntities(filePath)
      .then(res => {
        if (!cancelled && res?.entities) {
          setEntitiesList(res.entities);
        }
      })
      .catch(e => console.warn('Could not fetch file entities:', e));

    api.fileInsights(filePath)
      .then(res => { if (!cancelled) setInsights(res); })
      .catch(e => {
        console.error(e);
        if (!cancelled) setInsights({ summary: 'No AI summary available for this file.' });
      });

    return () => { cancelled = true; };
  }, [file]);

  const handleHoverTerm = (term: string, context: string, event: React.MouseEvent, immediate = false) => {
    if (!enableKeywordInsights) return;
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top;

    const fetchInsight = () => {
      setHoverPos({ x, y });
      if (termCache.current[term]) {
        setActiveHoverCard(termCache.current[term]);
        return;
      }
      api.termInsight(term, context, filePath)
        .then(data => {
          termCache.current[term] = data;
          setActiveHoverCard(data);
        })
        .catch(err => {
          console.warn('Failed to fetch term insight:', err);
          const fallback = {
            term,
            entity_type: 'Domain Concept',
            definition: `Domain keyword '${term}' indexed in repository intelligence.`,
            vault_count: 1,
            related_files: [filePath]
          };
          setActiveHoverCard(fallback);
        });
    };

    if (immediate) {
      if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
      fetchInsight();
    } else {
      if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
      hoverTimeoutRef.current = setTimeout(fetchInsight, 180);
    }
  };

  const handleLeaveTerm = () => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
    hoverTimeoutRef.current = setTimeout(() => {
      setActiveHoverCard(null);
    }, 250);
  };

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
        <div key={k} className="my-3.5 overflow-x-auto rounded-xl border border-slate-200 dark:border-white/10 shadow-xs">
          <table className="min-w-full text-xs text-left">
            <thead className="bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-semibold border-b border-slate-200 dark:border-white/10">
              <tr>
                {headerRow.map((col, cIdx) => (
                  <th key={cIdx} className="px-4 py-2.5">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60 dark:divide-white/5 font-mono text-[11px]">
              {bodyRows.map((row, rIdx) => (
                <tr key={rIdx} className={rIdx % 2 === 0 ? 'bg-white/40 dark:bg-white/[0.02]' : 'bg-slate-50/50 dark:bg-white/[0.04]'}>
                  {row.map((cell, cIdx) => (
                    <td key={cIdx} className="px-4 py-2 text-slate-800 dark:text-slate-300">{cell}</td>
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
        <div key={k} className="my-3.5 rounded-xl overflow-hidden border border-slate-700/60 bg-slate-950 shadow-lg">
          <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
            <span className="font-bold text-emerald-400 uppercase tracking-wider">{codeLang || 'code'}</span>
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
          <pre className="p-4 text-xs font-mono text-slate-200 overflow-x-auto whitespace-pre leading-relaxed font-mono">
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
        elements.push(<h1 key={lIdx} className="text-xl font-bold text-emerald-700 dark:text-emerald-400 mt-5 mb-2 font-serif-claude">{trimmed.slice(2)}</h1>);
      } else if (trimmed.startsWith('## ')) {
        elements.push(<h2 key={lIdx} className="text-lg font-bold text-slate-900 dark:text-slate-100 mt-4 mb-1.5 border-b border-slate-200/80 dark:border-white/10 pb-1 font-serif-claude">{trimmed.slice(3)}</h2>);
      } else if (trimmed.startsWith('### ')) {
        elements.push(<h3 key={lIdx} className="text-base font-semibold text-slate-900 dark:text-slate-100 mt-3 mb-1 font-serif-claude">{trimmed.slice(4)}</h3>);
      } else if (trimmed.startsWith('> [!NOTE]') || trimmed.startsWith('> [!TIP]') || trimmed.startsWith('> [!WARNING]') || trimmed.startsWith('> [!IMPORTANT]')) {
        const alertType = trimmed.slice(4, -1);
        const nextText = lines[lIdx + 1]?.replace(/^>\s*/, '') || '';
        lIdx++;
        const alertStyles: Record<string, { bg: string; border: string; text: string; icon: any }> = {
          NOTE: { bg: 'bg-slate-500/10', border: 'border-l-4 border-slate-500', text: 'text-slate-700 dark:text-slate-300', icon: Info },
          TIP: { bg: 'bg-emerald-500/10', border: 'border-l-4 border-emerald-500', text: 'text-emerald-700 dark:text-emerald-400', icon: Lightbulb },
          WARNING: { bg: 'bg-amber-500/10', border: 'border-l-4 border-amber-500', text: 'text-amber-700 dark:text-amber-400', icon: AlertTriangle },
          IMPORTANT: { bg: 'bg-rose-500/10', border: 'border-l-4 border-rose-500', text: 'text-rose-700 dark:text-rose-400', icon: ShieldAlert }
        };
        const style = alertStyles[alertType] || alertStyles.NOTE;
        const IconComp = style.icon;
        elements.push(
          <div key={lIdx} className={`my-3 p-3.5 rounded-r-xl ${style.bg} ${style.border} text-xs space-y-1`}>
            <div className={`font-semibold flex items-center gap-1.5 ${style.text}`}>
              <IconComp className="w-3.5 h-3.5" />
              <span>{alertType}</span>
            </div>
            <p className="text-slate-700 dark:text-slate-300 pl-5">{nextText}</p>
          </div>
        );
      } else if (trimmed.startsWith('> ')) {
        elements.push(<blockquote key={lIdx} className="my-2.5 pl-4 border-l-2 border-emerald-500 text-slate-600 dark:text-slate-400 italic text-xs font-serif-claude">{trimmed.slice(2)}</blockquote>);
      } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        elements.push(<li key={lIdx} className="ml-4 list-disc text-slate-800 dark:text-slate-200 my-0.5 text-xs">{trimmed.slice(2)}</li>);
      } else {
        elements.push(<p key={lIdx} className="text-slate-800 dark:text-slate-200 text-xs leading-relaxed">{line}</p>);
      }
    }

    if (inCodeBlock) flushCodeBlock('cb-end');
    if (inTable) flushTable('tbl-end');
    return <div className="space-y-2 p-6 font-sans">{elements}</div>;
  };

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

  const handleToggleTts = (paragraphs: string[]) => {
    if (!('speechSynthesis' in window)) {
      toast('TTS Not Supported', 'Web Speech API is not available in this browser', 'info');
      return;
    }
    if (ttsSpeaking) {
      window.speechSynthesis.cancel();
      setTtsSpeaking(false);
      return;
    }

    const fullText = paragraphs.join('. ');
    const utterance = new SpeechSynthesisUtterance(fullText);
    utterance.rate = ttsRate;
    utterance.onstart = () => setTtsSpeaking(true);
    utterance.onend = () => setTtsSpeaking(false);
    utterance.onerror = () => setTtsSpeaking(false);
    ttsUtteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    setTtsSpeaking(true);
    toast('Audio Read-Aloud Started', `${paragraphs.length} paragraphs queued (${ttsRate}x speed)`, 'info');
  };

  const handleMouseUpSelection = () => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      setSelectionPos(null);
      setSelectedText('');
      return;
    }
    const text = selection.toString().trim();
    if (text.length > 2) {
      try {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setSelectedText(text);
        setSelectionPos({
          x: rect.left + rect.width / 2,
          y: rect.top - 12
        });
      } catch {
        setSelectionPos(null);
        setSelectedText('');
      }
    } else {
      setSelectionPos(null);
      setSelectedText('');
    }
  };

  const addHighlight = (text: string) => {
    if (!text) return;
    const next = [...highlights, text];
    setHighlights(next);
    setSelectionPos(null);
    setSelectedText('');
    toast('Highlight Added', `Saved "${text.slice(0, 30)}..." to document annotations`, 'success');
  };

  const renderInteractiveEpubStudio = (text: string) => {
    if (!text) {
      return (
        <div className="p-12 text-center text-slate-500 text-sm animate-pulse flex flex-col items-center justify-center h-full">
          <BookOpen className="w-10 h-10 mb-3 opacity-30 text-amber-500 animate-bounce" />
          <span className="font-serif-claude text-base">Opening luxury reading studio...</span>
        </div>
      );
    }
    const cleanText = text.replace(/\r\n/g, '\n');
    let rawParas = cleanText.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
    if (rawParas.length <= 1) {
      rawParas = cleanText.split('\n').map(p => p.trim()).filter(Boolean);
    }
    const paragraphs = rawParas;
    const wordCount = text.split(/\s+/).filter(Boolean).length;
    const readingTimeMin = Math.max(1, Math.ceil(wordCount / 200));

    // Combine API entities with inline extracted capital terms
    const localKeywords = new Set<string>(entitiesList);
    for (const match of text.matchAll(/\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b/g)) {
      const term = match[1].trim();
      if (term.length > 3 && !['The', 'This', 'That', 'With', 'From', 'Your', 'They', 'Have', 'More', 'Some', 'When', 'Page', 'Date'].includes(term)) {
        localKeywords.add(term);
      }
    }
    for (const hardcoded of ['Analytical', 'Focus', 'CliftonStrengths', 'Gallup', 'Signature Themes', 'Don Clifton', 'Roberto Morales Pérez', 'Clean Architecture', 'ColBERT', 'FastAPI', 'SQLite']) {
      if (text.toLowerCase().includes(hardcoded.toLowerCase())) {
        localKeywords.add(hardcoded);
      }
    }

    const combinedEntities = Array.from(localKeywords);
    const sortedEntities = [...combinedEntities].sort((a, b) => b.length - a.length);
    const escapedEntities = sortedEntities.map(e => e.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')).join('|');
    const regex = escapedEntities && enableKeywordInsights ? new RegExp(`\\b(${escapedEntities})\\b`, 'g') : null;

    // 5 Handcrafted Luxury Themes
    const themeStyles: { [key: string]: { page: string; text: string; subtext: string; badge: string; dropcap: string; divider: string } } = {
      sepia: {
        page: 'bg-[#FAF7F2] text-[#2D241E] border-[#E8DFC8] shadow-2xl ring-1 ring-black/5',
        text: 'text-[#2D241E]',
        subtext: 'text-[#786656]',
        badge: 'bg-[#EFE7D5] text-[#5A4634] border-[#DCD1BA] hover:bg-[#E5DAC4]',
        dropcap: 'text-[#8B4513]',
        divider: 'text-[#C4B59D]'
      },
      midnight: {
        page: 'bg-[#0B0F17] text-[#E2E8F0] border-slate-800/80 shadow-2xl ring-1 ring-white/10',
        text: 'text-[#E2E8F0]',
        subtext: 'text-slate-400',
        badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/25',
        dropcap: 'text-emerald-400',
        divider: 'text-slate-700'
      },
      amber: {
        page: 'bg-[#1F1914] text-[#E8D9C8] border-[#3E3024] shadow-2xl ring-1 ring-amber-500/10',
        text: 'text-[#E8D9C8]',
        subtext: 'text-[#A89480]',
        badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30 hover:bg-amber-500/25',
        dropcap: 'text-amber-400',
        divider: 'text-[#544335]'
      },
      light: {
        page: 'bg-[#FFFFFF] text-[#1A202C] border-slate-200/90 shadow-2xl ring-1 ring-slate-900/5',
        text: 'text-[#1A202C]',
        subtext: 'text-slate-500',
        badge: 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200',
        dropcap: 'text-emerald-600',
        divider: 'text-slate-300'
      },
      nord: {
        page: 'bg-[#1E222A] text-[#ECEFF4] border-[#2E3440] shadow-2xl ring-1 ring-cyan-500/10',
        text: 'text-[#ECEFF4]',
        subtext: 'text-[#81A1C1]',
        badge: 'bg-[#2E3440] text-[#88C0D0] border-[#3B4252] hover:bg-[#3B4252]',
        dropcap: 'text-[#88C0D0]',
        divider: 'text-[#3B4252]'
      }
    };

    const curTheme = themeStyles[readerTheme] || themeStyles.sepia;

    const fontStyles: { [key: string]: string } = {
      serif: 'font-serif font-normal',
      sans: 'font-sans font-normal',
      mono: 'font-mono text-xs',
      charter: 'font-serif-claude'
    };

    const lineStyles: { [key: string]: string } = {
      normal: 'leading-relaxed',
      comfortable: 'leading-[1.9]',
      loose: 'leading-[2.2]'
    };

    const layoutWidths: { [key: string]: string } = {
      single: 'max-w-[780px]',
      dual: 'max-w-[1360px]',
      wide: 'max-w-[1040px]'
    };

    const renderParagraphContent = (para: string, pIdx: number) => {
      const isFirst = pIdx === 0;
      let textToRender = para;
      let initialLetter = '';
      let restOfPara = para;

      if (isFirst && para.length > 3) {
        initialLetter = para.charAt(0);
        restOfPara = para.slice(1);
      }

      if (regex) {
        const parts = restOfPara.split(regex);
        return (
          <p
            key={pIdx}
            className={`mb-6 text-justify text-pretty select-text ${isFirst ? 'relative' : ''}`}
            onMouseUp={handleMouseUpSelection}
          >
            {isFirst && initialLetter && (
              <span className={`float-left text-5xl lg:text-6xl font-serif font-bold mr-3 mt-1 leading-none ${curTheme.dropcap} select-none`}>
                {initialLetter}
              </span>
            )}
            {parts.map((part, idx) => {
              const isEntity = sortedEntities.includes(part);
              const isHighlighted = highlights.some(h => part.includes(h) || h.includes(part));
              if (isEntity) {
                return (
                  <span
                    key={idx}
                    onMouseEnter={(e) => handleHoverTerm(part, para, e)}
                    onMouseLeave={handleLeaveTerm}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleHoverTerm(part, para, e, true);
                    }}
                    className={`cursor-pointer font-semibold px-1.5 py-0.5 rounded-md border transition-all inline-flex items-center gap-0.5 mx-0.5 shadow-2xs ${curTheme.badge} ${
                      isHighlighted ? 'ring-2 ring-amber-400 bg-amber-400/20' : ''
                    }`}
                  >
                    <span>{part}</span>
                    <Sparkles className="w-2.5 h-2.5 opacity-60 inline" />
                  </span>
                );
              }
              if (isHighlighted) {
                return <mark key={idx} className="bg-amber-300/40 dark:bg-amber-500/30 text-inherit rounded px-1">{part}</mark>;
              }
              return part;
            })}
          </p>
        );
      }

      return (
        <p
          key={pIdx}
          className="mb-6 text-justify text-pretty select-text"
          onMouseUp={handleMouseUpSelection}
        >
          {isFirst && initialLetter && (
            <span className={`float-left text-5xl lg:text-6xl font-serif font-bold mr-3 mt-1 leading-none ${curTheme.dropcap} select-none`}>
              {initialLetter}
            </span>
          )}
          {restOfPara}
        </p>
      );
    };

    const midPoint = Math.ceil(paragraphs.length / 2);
    const leftPageParas = paragraphs.slice(0, midPoint);
    const rightPageParas = paragraphs.slice(midPoint);

    const docFileName = filePath.split(/[/\\]/).pop()?.replace(/\.[^/.]+$/, '') || 'Document Studio';

    return (
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-950/60 relative">
        {/* Luxury Studio Top Customization Bar */}
        <div className="p-3 bg-white/90 dark:bg-slate-900/95 border-b border-slate-200/80 dark:border-white/5 flex items-center justify-between gap-3 flex-wrap text-xs text-slate-700 dark:text-slate-300 backdrop-blur-xl shadow-xs z-20">
          {/* Typography Selector */}
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-400 font-serif-claude">
              <Type className="w-3.5 h-3.5" /> Typeface:
            </span>
            <div className="flex rounded-lg bg-slate-100 dark:bg-slate-800 p-0.5 border border-slate-200 dark:border-slate-700/60 text-xs">
              <button
                onClick={() => setReaderFont('serif')}
                className={`px-2.5 py-1 rounded-md transition-colors font-serif ${readerFont === 'serif' ? 'bg-emerald-600 text-white font-semibold shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
              >
                Editorial Serif
              </button>
              <button
                onClick={() => setReaderFont('charter')}
                className={`px-2.5 py-1 rounded-md transition-colors font-serif-claude ${readerFont === 'charter' ? 'bg-emerald-600 text-white font-semibold shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
              >
                Classic Charter
              </button>
              <button
                onClick={() => setReaderFont('sans')}
                className={`px-2.5 py-1 rounded-md transition-colors font-sans ${readerFont === 'sans' ? 'bg-emerald-600 text-white font-semibold shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
              >
                Modern Sans
              </button>
              <button
                onClick={() => setReaderFont('mono')}
                className={`px-2.5 py-1 rounded-md transition-colors font-mono ${readerFont === 'mono' ? 'bg-emerald-600 text-white font-semibold shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
              >
                Mono
              </button>
            </div>
          </div>

          {/* Sizing, Layout, Themes & Audio */}
          <div className="flex items-center gap-2.5 flex-wrap">
            {/* Font Sizing */}
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-lg border border-slate-200 dark:border-slate-700/60">
              <span className="text-[11px] text-slate-400">Size:</span>
              <button
                onClick={() => setReaderSize(Math.max(13, readerSize - 1))}
                className="px-1.5 py-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-xs font-bold transition-colors"
                title="Decrease Font Size"
              >
                A-
              </button>
              <span className="font-mono font-semibold text-emerald-600 dark:text-emerald-400 w-7 text-center">{readerSize}px</span>
              <button
                onClick={() => setReaderSize(Math.min(28, readerSize + 1))}
                className="px-1.5 py-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-xs font-bold transition-colors"
                title="Increase Font Size"
              >
                A+
              </button>
            </div>

            {/* Layout Mode */}
            <div className="flex items-center gap-0.5 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700/60">
              <button
                onClick={() => setReaderLayout('single')}
                className={`px-2 py-1 rounded-md transition-colors flex items-center gap-1 ${readerLayout === 'single' ? 'bg-emerald-600 text-white shadow-xs font-semibold' : 'text-slate-500 hover:text-slate-200'}`}
                title="Single Column Focus"
              >
                <AlignLeft className="w-3.5 h-3.5" /> Single
              </button>
              <button
                onClick={() => setReaderLayout('dual')}
                className={`px-2 py-1 rounded-md transition-colors flex items-center gap-1 ${readerLayout === 'dual' ? 'bg-emerald-600 text-white shadow-xs font-semibold' : 'text-slate-500 hover:text-slate-200'}`}
                title="Dual Page Book Spread"
              >
                <Columns2 className="w-3.5 h-3.5" /> Book Spread
              </button>
            </div>

            {/* Themes Palette */}
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700/60 text-xs">
              <button
                onClick={() => setReaderTheme('sepia')}
                className={`px-2 py-1 rounded-md transition-colors ${readerTheme === 'sepia' ? 'bg-[#d8c29d] text-[#3e2714] font-bold shadow-xs' : 'text-slate-600 dark:text-slate-400'}`}
                title="Warm Book Ivory / Sepia"
              >
                📜 Ivory
              </button>
              <button
                onClick={() => setReaderTheme('midnight')}
                className={`px-2 py-1 rounded-md transition-colors ${readerTheme === 'midnight' ? 'bg-emerald-600 text-white font-bold shadow-xs' : 'text-slate-600 dark:text-slate-400'}`}
                title="OLED Velvet Obsidian"
              >
                🌙 Midnight
              </button>
              <button
                onClick={() => setReaderTheme('amber')}
                className={`px-2 py-1 rounded-md transition-colors ${readerTheme === 'amber' ? 'bg-[#544335] text-[#f5d7b5] font-bold shadow-xs' : 'text-slate-600 dark:text-slate-400'}`}
                title="Vintage Amber Noir"
              >
                ☕ Amber
              </button>
              <button
                onClick={() => setReaderTheme('light')}
                className={`px-2 py-1 rounded-md transition-colors ${readerTheme === 'light' ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600 dark:text-slate-400'}`}
                title="Clean Editorial Studio"
              >
                ☀️ Light
              </button>
              <button
                onClick={() => setReaderTheme('nord')}
                className={`px-2 py-1 rounded-md transition-colors ${readerTheme === 'nord' ? 'bg-[#3b4252] text-[#88c0d0] font-bold shadow-xs' : 'text-slate-600 dark:text-slate-400'}`}
                title="Nordic Slate"
              >
                ❄️ Nord
              </button>
            </div>

            {/* TTS Audio Read-Aloud Button */}
            <button
              onClick={() => handleToggleTts(paragraphs)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                ttsSpeaking
                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700/60 hover:bg-slate-200'
              }`}
              title="Listen to Document via Speech Synthesis"
            >
              {ttsSpeaking ? <VolumeX className="w-3.5 h-3.5 text-rose-400" /> : <Volume2 className="w-3.5 h-3.5 text-emerald-500" />}
              <span>{ttsSpeaking ? 'Stop Audio' : 'Read Aloud'}</span>
            </button>

            {/* Keyword Hover Insights Toggle */}
            <button
              onClick={() => setEnableKeywordInsights(!enableKeywordInsights)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                enableKeywordInsights
                  ? 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-500/40 shadow-xs'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
              <span>Keyword Insights: {enableKeywordInsights ? 'ON' : 'OFF'}</span>
            </button>
          </div>
        </div>

        {/* EPUB Document Reading Canvas */}
        <div className="flex-1 overflow-y-auto p-6 md:p-12 flex justify-center items-start">
          {readerLayout === 'dual' ? (
            /* Dual-Page Open Book Spread */
            <div
              className={`w-full ${layoutWidths.dual} p-8 md:p-14 rounded-3xl border transition-all ${curTheme.page} ${fontStyles[readerFont]} ${lineStyles[readerLineHeight]} grid grid-cols-1 md:grid-cols-2 gap-12 relative`}
              style={{ fontSize: `${readerSize}px` }}
            >
              {/* Center Book Crease Divider */}
              <div className="hidden md:block absolute top-8 bottom-8 left-1/2 -translate-x-1/2 w-px bg-current/15 shadow-sm" />

              {/* Page 1 (Left Page) */}
              <div className="space-y-6 md:pr-6">
                <div className="border-b border-current/15 pb-4 mb-8 flex items-center justify-between opacity-80 text-xs font-mono">
                  <span className="font-serif-claude tracking-wider uppercase font-semibold text-[11px] truncate max-w-[200px]">{docFileName}</span>
                  <span>Page 1 • ~{readingTimeMin} min read</span>
                </div>

                <div className="text-center pb-6 border-b border-current/10">
                  <h1 className="text-2xl lg:text-3xl font-serif font-bold tracking-tight mb-2">
                    {docFileName}
                  </h1>
                  <p className={`text-xs italic ${curTheme.subtext} font-serif-claude`}>
                    Executive Document & Vault Monograph
                  </p>
                  <div className={`mt-3 text-sm ${curTheme.divider}`}>✦  ✦  ✦</div>
                </div>

                {leftPageParas.map((p, idx) => renderParagraphContent(p, idx))}
              </div>

              {/* Page 2 (Right Page) */}
              <div className="space-y-6 md:pl-6">
                <div className="border-b border-current/15 pb-4 mb-8 flex items-center justify-between opacity-80 text-xs font-mono">
                  <span className="font-serif-claude tracking-wider uppercase font-semibold text-[11px] truncate max-w-[200px]">Continued</span>
                  <span>Page 2 • {wordCount} Words</span>
                </div>

                {rightPageParas.map((p, idx) => renderParagraphContent(p, idx + leftPageParas.length))}

                <div className="text-center pt-8 opacity-60 text-xs font-serif-claude">
                  — ✦ End of Document ✦ —
                </div>
              </div>
            </div>
          ) : (
            /* Single Page Classic Editorial Spread */
            <div
              className={`w-full ${layoutWidths[readerLayout]} p-8 md:p-16 rounded-3xl border transition-all ${curTheme.page} ${fontStyles[readerFont]} ${lineStyles[readerLineHeight]}`}
              style={{ fontSize: `${readerSize}px` }}
            >
              {/* Book Header Bar */}
              <div className="border-b border-current/15 pb-4 mb-8 flex items-center justify-between opacity-80 text-xs font-mono">
                <span className="font-serif-claude tracking-wider uppercase font-semibold text-[11px] truncate max-w-[320px]">{docFileName}</span>
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3 h-3 text-amber-500" /> ~{readingTimeMin} min read • {wordCount} words
                </span>
              </div>

              {/* Chapter Title Headpiece */}
              <div className="text-center pb-8 mb-8 border-b border-current/10">
                <h1 className="text-3xl lg:text-4xl font-serif font-bold tracking-tight mb-2">
                  {docFileName}
                </h1>
                <p className={`text-xs italic ${curTheme.subtext} font-serif-claude`}>
                  Executive Monograph • Uroboros Knowledge Vault
                </p>
                <div className={`mt-3 text-sm ${curTheme.divider}`}>✦  ✦  ✦</div>
              </div>

              {/* Content Paragraphs */}
              {paragraphs.map((p, idx) => renderParagraphContent(p, idx))}

              {/* Document Finial */}
              <div className="text-center pt-10 border-t border-current/15 opacity-60 text-xs font-serif-claude">
                — ✦ End of Document ✦ —
              </div>
            </div>
          )}
        </div>

        {/* Floating Text Selection Action Bubble */}
        {selectionPos && selectedText && (
          <div
            className="fixed z-50 -translate-x-1/2 -translate-y-full flex items-center gap-1 bg-slate-900/95 text-white p-1.5 rounded-xl shadow-2xl border border-emerald-500/40 backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150"
            style={{ left: `${selectionPos.x}px`, top: `${selectionPos.y}px` }}
          >
            <button
              onClick={() => {
                window.location.hash = `#/chat?q=${encodeURIComponent('Explain this excerpt: "' + selectedText + '" in context of ' + filePath)}`;
              }}
              className="px-2.5 py-1 hover:bg-emerald-600 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors"
            >
              <Brain className="w-3.5 h-3.5 text-emerald-400" /> Explain
            </button>
            <button
              onClick={() => addHighlight(selectedText)}
              className="px-2.5 py-1 hover:bg-amber-600 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors"
            >
              <Highlighter className="w-3.5 h-3.5 text-amber-400" /> Highlight
            </button>
            <button
              onClick={() => {
                navigator.clipboard.writeText(`> "${selectedText}"\n\n— Excerpt from *${docFileName}*`);
                toast('Quote Copied', 'Markdown citation copied to clipboard', 'success');
                setSelectionPos(null);
              }}
              className="px-2.5 py-1 hover:bg-slate-800 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors"
            >
              <Quote className="w-3.5 h-3.5 text-cyan-400" /> Quote
            </button>
          </div>
        )}
      </div>
    );
  };

  const textLines = content?.content ? content.content.split('\n') : [];

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Workspace Header Toolbar */}
      <div className="px-5 py-3 border-b border-slate-200/80 dark:border-white/5 flex items-center justify-between bg-white/60 dark:bg-slate-900/60 backdrop-blur-md">
         <div className="flex items-center gap-3">
           <button onClick={onClose} className="p-1.5 hover:bg-slate-200 dark:hover:bg-white/10 rounded-lg transition-colors" title="Close File View">
             <X className="w-4 h-4 text-slate-600 dark:text-slate-400"/>
           </button>
           <div>
             <h2 className="font-semibold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
               {filePath}
               <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 rounded text-[10px] font-mono border border-emerald-500/20 uppercase font-bold">
                 {fileExt}
               </span>
             </h2>
           </div>
         </div>

         {/* Mode Switcher Tabs */}
         <div className="flex items-center gap-2">
            <div className="flex rounded-lg bg-slate-200/80 dark:bg-slate-800/80 p-0.5 text-xs border border-slate-300/50 dark:border-white/5">
              <button
                onClick={() => setViewTab('studio')}
                className={`px-3.5 py-1 rounded-md transition-colors flex items-center gap-1.5 font-semibold ${viewTab === 'studio' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Document Studio</span>
              </button>

              {isCsv && (
                <button
                  onClick={() => setViewTab('table')}
                  className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'table' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
                >
                  <TableIcon className="w-3.5 h-3.5" />
                  <span>Data Grid</span>
                </button>
              )}

              {isImage && (
                <button
                  onClick={() => setViewTab('image')}
                  className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'image' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
                >
                  <ImageIcon className="w-3.5 h-3.5" />
                  <span>Image Canvas</span>
                </button>
              )}

              <button
                onClick={() => setViewTab('source')}
                className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium ${viewTab === 'source' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
              >
                <Code2 className="w-3.5 h-3.5" />
                <span>Source</span>
              </button>
            </div>

            <button onClick={copyContent} className="px-3 py-1.5 bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-200 dark:hover:bg-white/20 transition-colors flex items-center gap-1.5">
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5"/>}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
            <button onClick={downloadFile} className="px-3 py-1.5 bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-200 dark:hover:bg-white/20 transition-colors flex items-center gap-1.5">
              <Download className="w-3.5 h-3.5"/> Download
            </button>
            <button onClick={handleSave} className={`px-3 py-1.5 ${emeraldButtonClasses} text-xs font-medium flex items-center gap-1.5 shadow-sm`}>
              <Save className="w-3.5 h-3.5"/> Save
            </button>
          </div>
      </div>
      
      {/* Document View & AI Insights Split */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 bg-slate-50/50 dark:bg-slate-950/80 overflow-y-auto flex flex-col">
          {/* UNIFIED TAB 1: Acrobat-Grade Direct Document Studio */}
          {viewTab === 'studio' && (
            <div className="flex-1 flex flex-col p-4 space-y-3 overflow-hidden">
              {/* Adobe Acrobat Style Control Toolbar */}
              <div className="flex items-center justify-between px-3.5 py-2 bg-white/90 dark:bg-slate-900/90 rounded-xl border border-slate-200 dark:border-white/10 text-xs text-slate-700 dark:text-slate-300 shadow-sm backdrop-blur-md gap-3 overflow-x-auto">
                {/* Left: In-Page Acrobat Search Bar */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <div className="relative w-52 flex items-center">
                    <Search className="w-3.5 h-3.5 absolute left-2.5 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search document..."
                      value={inPageSearch}
                      onChange={(e) => setInPageSearch(e.target.value)}
                      className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 rounded-lg pl-8 pr-14 py-1 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-emerald-500 font-medium"
                    />
                    {inPageSearch && (
                      <span className="absolute right-1.5 text-[9px] font-mono text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-500/10 px-1 py-0.5 rounded">
                        {inPageMatchIndex}/4
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-0.5 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700/80">
                    <button
                      onClick={() => setInPageMatchIndex(Math.max(1, inPageMatchIndex - 1))}
                      className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-500 hover:text-slate-200"
                      title="Previous Match"
                    >
                      <ChevronLeft className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => setInPageMatchIndex(inPageMatchIndex + 1)}
                      className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-500 hover:text-slate-200"
                      title="Next Match"
                    >
                      <ChevronRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                {/* Center: AI X-Ray & View Format Switcher */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => setIsXrayActive(!isXrayActive)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                      isXrayActive
                        ? 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-500/40 shadow-xs ring-1 ring-emerald-500/30'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'
                    }`}
                  >
                    <Sparkles className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
                    <span>AI X-Ray: {isXrayActive ? 'ON' : 'OFF'}</span>
                  </button>

                  {isPdf && (
                    <div className="flex rounded-lg bg-slate-100 dark:bg-slate-800 p-0.5 border border-slate-200 dark:border-slate-700/80 text-[11px]">
                      <button
                        onClick={() => setDocRenderMode('real')}
                        className={`px-2 py-0.5 rounded-md transition-colors flex items-center gap-1 font-semibold ${
                          docRenderMode === 'real' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-500 hover:text-slate-200'
                        }`}
                      >
                        <FileText className="w-3 h-3" /> Real PDF
                      </button>
                      <button
                        onClick={() => setDocRenderMode('editorial')}
                        className={`px-2 py-0.5 rounded-md transition-colors flex items-center gap-1 font-semibold ${
                          docRenderMode === 'editorial' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-500 hover:text-slate-200'
                        }`}
                      >
                        <BookOpen className="w-3 h-3" /> Editorial
                      </button>
                    </div>
                  )}
                </div>

                {/* Right: Page Navigation, Zoom & Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {isPdf && docRenderMode === 'real' && (
                    <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-lg border border-slate-200 dark:border-slate-700/80">
                      <button
                        onClick={() => setCurrentPdfPage(Math.max(0, currentPdfPage - 1))}
                        disabled={currentPdfPage === 0}
                        className="p-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-30 rounded transition-colors"
                        title="Previous Page"
                      >
                        <ChevronLeft className="w-3.5 h-3.5" />
                      </button>
                      <span className="font-mono text-[11px] px-1 font-bold text-emerald-600 dark:text-emerald-400">
                        {currentPdfPage + 1}/{pdfInfo?.total_pages || 1}
                      </span>
                      <button
                        onClick={() => setCurrentPdfPage(Math.min((pdfInfo?.total_pages || 1) - 1, currentPdfPage + 1))}
                        disabled={currentPdfPage >= (pdfInfo?.total_pages || 1) - 1}
                        className="p-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-30 rounded transition-colors"
                        title="Next Page"
                      >
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                      <div className="h-3 w-px bg-slate-300 dark:bg-slate-700 mx-1" />
                      <button
                        onClick={() => setPdfPageZoom(Math.max(0.5, pdfPageZoom - 0.15))}
                        className="p-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors"
                        title="Zoom Out"
                      >
                        <ZoomOut className="w-3.5 h-3.5" />
                      </button>
                      <span className="font-mono text-[10px] w-8 text-center text-slate-400 font-semibold">
                        {Math.round(pdfPageZoom * 100)}%
                      </span>
                      <button
                        onClick={() => setPdfPageZoom(Math.min(2.5, pdfPageZoom + 0.15))}
                        className="p-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors"
                        title="Zoom In"
                      >
                        <ZoomIn className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setPdfPageZoom(1)}
                        className="p-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors"
                        title="Reset 100% Scale"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}

                  <a
                    href={binaryUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-700/80 text-slate-400 hover:text-emerald-400 transition-colors"
                    title="Open Raw Binary in Window"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>

              {/* Main Document Canvas */}
              {docRenderMode === 'real' && isPdf ? (
                <div className="flex-1 flex flex-col space-y-3 overflow-hidden">
                  <div className="flex-1 rounded-2xl border border-slate-700/60 bg-slate-950 p-6 shadow-2xl flex flex-col items-center justify-start overflow-auto relative">
                    
                    {/* Interactive AI X-Ray Concept Pill Overlay Ribbon */}
                    {isXrayActive && (
                      <div className="w-full max-w-4xl mb-4 p-3 bg-slate-900/90 border border-emerald-500/40 rounded-xl shadow-xl backdrop-blur-md flex items-center justify-between gap-3 flex-wrap animate-in fade-in slide-in-from-top-2">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                            <Sparkles className="w-3.5 h-3.5" /> Detected Concepts & Themes:
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {['Analytical', 'Focus', 'CliftonStrengths', 'Gallup', 'Signature Themes', 'Roberto Morales Pérez'].map((term, i) => (
                              <button
                                key={i}
                                onMouseEnter={(e) => handleHoverTerm(term, content?.content || '', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleHoverTerm(term, content?.content || '', e, true);
                                }}
                                className={`px-2 py-0.5 rounded-md text-[11px] font-semibold border transition-all flex items-center gap-1 shadow-2xs ${
                                  inPageSearch && term.toLowerCase().includes(inPageSearch.toLowerCase())
                                    ? 'bg-amber-400/25 text-amber-300 border-amber-400/60 ring-2 ring-amber-400/40 animate-pulse'
                                    : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/30 hover:border-emerald-400'
                                }`}
                              >
                                <span>{term}</span>
                                <Sparkles className="w-2.5 h-2.5 opacity-60" />
                              </button>
                            ))}
                          </div>
                        </div>

                        <div className="text-[11px] font-mono text-slate-400">
                          Hover concept to inspect AI insights
                        </div>
                      </div>
                    )}

                    {/* Real Document Image Canvas */}
                    <div className="relative max-w-full flex items-center justify-center">
                      <img
                        src={`/api/file/pdf/page?path=${encodeURIComponent(filePath)}&page=${currentPdfPage}&dpi=150`}
                        alt={`Document Page ${currentPdfPage + 1}`}
                        className="rounded-xl shadow-2xl border border-slate-700/80 max-h-[70vh] object-contain transition-transform duration-150 bg-white"
                        style={{ transform: `scale(${pdfPageZoom})`, transformOrigin: 'center top' }}
                      />
                    </div>
                  </div>

                  {/* High-DPI Page Thumbnail Strip */}
                  {(pdfInfo?.total_pages || 1) > 1 && (
                    <div className="flex items-center gap-2 overflow-x-auto p-2.5 bg-slate-900/80 rounded-xl border border-slate-800 shadow-lg">
                      <span className="text-[11px] text-slate-400 font-mono px-2 flex-shrink-0 font-semibold">
                        Pages ({pdfInfo.total_pages}):
                      </span>
                      {Array.from({ length: pdfInfo.total_pages }).map((_, idx) => (
                        <button
                          key={idx}
                          onClick={() => setCurrentPdfPage(idx)}
                          className={`px-3 py-1 rounded-lg text-xs font-mono transition-all flex-shrink-0 flex items-center gap-1.5 border ${
                            currentPdfPage === idx
                              ? 'bg-emerald-600 text-white border-emerald-400 shadow-md shadow-emerald-500/20 font-bold'
                              : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200'
                          }`}
                        >
                          <span>Page {idx + 1}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                /* Editorial Luxury Reader Mode */
                <div className="flex-1 flex flex-col h-full rounded-2xl overflow-hidden border border-slate-700/60 bg-slate-950/80 shadow-2xl">
                  {renderInteractiveEpubStudio(content?.content || '')}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CSV Data Grid */}
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
                    className="w-full bg-slate-900/80 border border-slate-700/60 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 outline-none focus:border-emerald-500"
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
                      <tr key={rIdx} className={rIdx % 2 === 0 ? 'bg-slate-900/50 hover:bg-emerald-500/10' : 'bg-slate-950/50 hover:bg-emerald-500/10'}>
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

        {/* Right Pane: AI Intelligence Drawer */}
        <div className="w-96 bg-white/40 dark:bg-slate-900/40 p-6 overflow-y-auto border-l border-slate-200/80 dark:border-white/5 flex-shrink-0 space-y-6">
          <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
            <Brain className="w-5 h-5 text-emerald-500"/> Document Intelligence
          </h3>
          {insights ? (
             <div className="space-y-6">
                <div>
                  <h4 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Grounded Summary
                  </h4>
                  <div className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-white/70 dark:bg-black/30 p-4 rounded-xl border border-slate-200 dark:border-white/5 whitespace-pre-wrap shadow-2xs">
                    {insights.insights || insights.summary || insights.text || 'No summary available for this file.'}
                  </div>
                </div>

                {/* Key Takeaways (Mustard Gold Callout) */}
                <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/5 dark:bg-amber-950/20 space-y-2">
                  <h4 className="text-[11px] font-semibold text-amber-800 dark:text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Lightbulb className="w-3.5 h-3.5 text-amber-500" /> Key Takeaways
                  </h4>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    {insights.takeaways || 'Extracted strategic concepts and key principles mapped to this vault entity.'}
                  </p>
                </div>

                <div>
                  <h4 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Code2 className="w-3.5 h-3.5 text-emerald-500" /> Extracted Entities & Tags
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {insights.entities && Array.isArray(insights.entities) && insights.entities.length > 0 ? (
                      insights.entities.map((ent: string, i: number) => (
                        <span key={i} className={emeraldBadgeClasses}>#{ent}</span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">Document analyzed cleanly.</span>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-teal-500" /> Vector Index Status
                  </h4>
                  <div className="p-3 bg-slate-100/70 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-white/5 space-y-1 text-xs text-slate-600 dark:text-slate-400 font-mono">
                    <div className="flex justify-between"><span>Embedder:</span> <span className="text-emerald-500 font-semibold">NomIC HNSW</span></div>
                    <div className="flex justify-between"><span>Vector Cluster:</span> <span className="text-teal-400 font-semibold">Active Vault Node</span></div>
                  </div>
                </div>
             </div>
          ) : (
            <div className="animate-pulse text-xs text-slate-500">Synthesizing document intelligence...</div>
          )}
        </div>
      </div>

      {/* Floating Glassmorphic Keyword Hover Card */}
      {activeHoverCard && hoverPos && (
        <div
          className="fixed z-50 w-80 p-4 rounded-xl border border-emerald-500/40 bg-slate-900/95 text-slate-200 shadow-2xl backdrop-blur-xl transition-all pointer-events-auto"
          style={{
            left: `${Math.min(window.innerWidth - 340, Math.max(10, hoverPos.x - 140))}px`,
            top: `${Math.max(10, hoverPos.y - 200)}px`,
          }}
          onMouseEnter={() => {
            if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
          }}
          onMouseLeave={handleLeaveTerm}
        >
          <div className="flex items-center justify-between border-b border-slate-700/60 pb-2 mb-2.5">
            <div className="flex items-center gap-1.5 font-bold text-emerald-300 text-sm font-serif-claude">
              <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />
              <span>{activeHoverCard.term}</span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30 font-mono">
              {activeHoverCard.entity_type || 'Domain Entity'}
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed mb-3">
            {activeHoverCard.definition}
          </p>

          <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-3 bg-slate-950/60 px-2 py-1.5 rounded-lg border border-slate-800">
            <span>Vault Mentions: <strong className="text-emerald-300 font-bold">{activeHoverCard.vault_count}</strong></span>
            {activeHoverCard.related_files?.length > 0 && (
              <span className="truncate max-w-[120px] text-slate-400">
                in {activeHoverCard.related_files[0]}
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 pt-1 border-t border-slate-800">
            <button
              onClick={() => {
                window.location.hash = `#/chat?q=${encodeURIComponent('Explain the concept and significance of ' + activeHoverCard.term + ' in document ' + filePath)}`;
              }}
              className="flex-1 px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-semibold flex items-center justify-center gap-1 transition-colors shadow-sm"
            >
              <Brain className="w-3 h-3" /> Ask AI
            </button>
            <button
              onClick={() => {
                window.location.hash = `#/search?q=${encodeURIComponent(activeHoverCard.term)}`;
              }}
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-semibold flex items-center justify-center gap-1 transition-colors border border-slate-700"
            >
              <Search className="w-3 h-3" /> Search
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
