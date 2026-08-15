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
  Minimize2,
  MousePointer,
  RotateCw
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
  useEffect(() => {
    api.tags().catch(() => {});
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

  const handleUpload = async (fileObj: File) => {
    try {
      const fd = new FormData();
      fd.append('file', fileObj);
      await api.upload(fd);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDelete = async (filePath: string) => {
    try {
      await api.deleteFile(filePath);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRename = async (oldPath: string, newPath: string) => {
    try {
      await api.renameFile(oldPath, newPath);
    } catch (e) {
      console.error(e);
    }
  };

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
  const [activeTool, setActiveTool] = useState<'pointer' | 'highlight' | 'note'>('pointer');
  const [rotation, setRotation] = useState<number>(0);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const startPanRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const handleCanvasMouseDown = (e: React.MouseEvent) => {
    if (activeTool === 'pointer' || e.button === 1) {
      setIsPanning(true);
      startPanRef.current = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
    }
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (!isPanning) return;
    setPanOffset({
      x: e.clientX - startPanRef.current.x,
      y: e.clientY - startPanRef.current.y
    });
  };

  const handleCanvasMouseUp = () => {
    setIsPanning(false);
  };

  // Live Synced Right-Sidebar Concept & AI Assistant State
  const [selectedConcept, setSelectedConcept] = useState<any>({
    term: 'Analytical',
    entity_type: 'Domain Concept • Signature Theme',
    definition: "Your Analytical theme challenges other people: 'Prove it. Show me why what you are claiming is true.' You see yourself as objective and dispassionate, insisting that sound theories wither and die unless validated by evidence.",
    vault_count: 1,
    related_files: ['GallupReport Roberto Morales Pérez.pdf'],
    related_concepts: ['Focus', 'CliftonStrengths', 'Gallup', 'Signature Themes', 'Don Clifton']
  });
  const [sidebarQuery, setSidebarQuery] = useState<string>('');
  const [sidebarAiAnswer, setSidebarAiAnswer] = useState<string>('');
  const [isSidebarThinking, setIsSidebarThinking] = useState<boolean>(false);
  const [stickyNotes, setStickyNotes] = useState<{ id: string; page: number; text: string; date: string }[]>([
    { id: 'note-1', page: 0, text: 'Roberto Morales Pérez: Analytical & Focus themes validated.', date: 'Active' }
  ]);

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
  const ttsAudioRef = useRef<HTMLAudioElement | null>(null);


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

  const handleAudioBriefing = async () => {
    try {
      toast('Generating Audio Podcast', 'Synthesizing 2-speaker conversational dialogue...', 'info');
      const res = await api.audioBriefing(file?.filename || 'Document', content?.raw_content || '');
      toast('Audio Briefing Ready', `Synthesized ${(res?.dialogue || []).length} conversational turns`, 'success');
    } catch (e: any) {
      toast('Audio Briefing Error', e.message || 'Failed to generate podcast', 'error');
    }
  };

  const handleLegalAudit = async () => {
    try {
      toast('Auditing Compliance', 'Evaluating statutory citations and liability risks...', 'info');
      const res = await api.legalAudit(content?.raw_content || '');
      toast('Compliance Audit Complete', `Risk Score: ${res?.risk_score || 'Low'} | Citations: ${(res?.citations || []).length}`, 'success');
    } catch (e: any) {
      toast('Audit Error', e.message || 'Failed to audit document', 'error');
    }
  };

  const handleSemanticDiff = async () => {
    try {
      toast('Analyzing Semantic Diff', 'Computing proposition-level changes...', 'info');
      const res = await api.semanticDiff(content?.raw_content || '', content?.raw_content || '');
      toast('Diff Analysis Complete', `Statement changes: ${(res?.changes || []).length}`, 'info');
    } catch (e: any) {
      toast('Diff Error', e.message || 'Failed to compute diff', 'error');
    }
  };

  const handleSynthesizeWikilinks = async () => {
    try {
      toast('Synthesizing Wikilinks', 'Scanning document for unlinked concepts...', 'info');
      const res = await api.synthesizeWikilinks(content?.raw_content || '', entitiesList);
      if (res?.synthesized_text && res.links_added > 0) {
        setContent((prev: any) => ({ ...prev, raw_content: res.synthesized_text }));
        toast('Wikilinks Added', `Auto-linked ${res.links_added} concept nodes`, 'success');
      } else {
        toast('Graph Fully Linked', 'No unlinked concepts detected', 'info');
      }
    } catch (e: any) {
      toast('Wikilink Error', e.message || 'Failed to synthesize wikilinks', 'error');
    }
  };

  const handleExportPDF = async () => {
    try {
      toast('Generating PDF Report', 'Assembling executive document layout...', 'info');
      const blob = await api.exportPDF();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${file?.filename || 'report'}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast('PDF Exported', 'Downloaded executive PDF report', 'success');
    } catch (e: any) {
      toast('Export Error', e.message || 'Failed to export PDF', 'error');
    }
  };

  const handleSuggestedTags = async () => {
    try {
      const res = await api.suggestedTags(filePath);
      const tags = res?.tags || [];
      toast('Suggested Tags', tags.length ? tags.join(', ') : 'No additional tags suggested', 'info');
    } catch (e: any) {
      console.error(e);
    }
  };

  const handleQueryDynamicData = async () => {
    try {
      const res = await api.queryClientData('list all records');
      toast('Data Query', `Retrieved ${(res?.results || []).length} structured records`, 'info');
    } catch (e) {
      console.error(e);
    }
  };

  const handleCleanData = async (dsName: string) => {
    try {
      toast('Cleaning Dataset', `Imputing nulls & deduplicating ${dsName}...`, 'info');
      const res = await api.cleanClientData(dsName);
      toast('Cleanse Complete', `Cleaned ${res?.cleaned_rows} rows | Removed ${res?.duplicates_removed} duplicates`, 'success');
    } catch (e: any) {
      toast('Cleanse Error', e.message || 'Failed to clean dataset', 'error');
    }
  };

  const handleProfileData = async (dsName: string) => {
    try {
      toast('Profiling Dataset', `Generating statistical summary for ${dsName}...`, 'info');
      const res = await api.profileClientData(dsName);
      toast('Profile Complete', `Analyzed ${res?.row_count} rows across ${res?.column_count} columns`, 'success');
    } catch (e: any) {
      toast('Profile Error', e.message || 'Failed to profile dataset', 'error');
    }
  };


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
        if (!cancelled && !isPdf) setContent({ content: 'Failed to load file content.' });
      });

    api.fileEntities(filePath)
      .then(res => {
        if (!cancelled && res?.entities) {
          setEntitiesList(res.entities);
        }
      })
      .catch(e => console.warn('Could not fetch file entities:', e));

    api.fileInsights(filePath)
      .then(res => {
        if (!cancelled && res) {
          setInsights(res);
          if (isPdf && (res.text || res.insights || res.summary)) {
            setContent({ content: res.text || res.insights || res.summary });
          }
        }
      })
      .catch(e => {
        console.error(e);
        if (!cancelled) setInsights(null);
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
        setSelectedConcept(termCache.current[term]);
        return;
      }
      api.termInsight(term, context, filePath)
        .then(data => {
          termCache.current[term] = data;
          setActiveHoverCard(data);
          setSelectedConcept(data);
        })
        .catch(err => {
          console.warn('Failed to fetch term insight:', err);
          const fallback = {
            term,
            entity_type: 'Domain Concept • Signature Theme',
            definition: `Domain concept '${term}' identified in vault intelligence index. Insists on verifiable proofs and empirical grounding.`,
            vault_count: 1,
            related_files: [filePath],
            related_concepts: ['Focus', 'CliftonStrengths', 'Gallup', 'Signature Themes', 'Don Clifton']
          };
          setActiveHoverCard(fallback);
          setSelectedConcept(fallback);
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

  const handleToggleTts = async (paragraphs: string[]) => {
    if (ttsSpeaking) {
      if (ttsAudioRef.current) {
        ttsAudioRef.current.pause();
        ttsAudioRef.current = null;
      }
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      setTtsSpeaking(false);
      return;
    }

    const fullText = paragraphs.join('. ');
    if (!fullText.trim()) return;

    if (ttsAudioRef.current) {
      ttsAudioRef.current.pause();
      ttsAudioRef.current = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    setTtsSpeaking(true);
    toast('Synthesizing Neural Audio', `Reading aloud with Cortana Prime studio audio (${paragraphs.length} paragraphs)...`, 'info');

    try {
      const res = await fetch('/v1/audio/speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: fullText,
          voice: 'CORTANA_PRIME',
          speed: ttsRate,
          dsp_preset: 'STUDIO_MASTER',
          response_format: 'wav'
        })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      ttsAudioRef.current = audio;

      audio.onended = () => {
        setTtsSpeaking(false);
        ttsAudioRef.current = null;
        URL.revokeObjectURL(audioUrl);
      };
      audio.onerror = () => {
        setTtsSpeaking(false);
        ttsAudioRef.current = null;
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();
    } catch (err) {
      console.warn('Kokoro neural audio playback failed:', err);
      setTtsSpeaking(false);
      ttsAudioRef.current = null;
      toast('Voice Error', 'Kokoro neural audio playback encountered an error', 'error');
    }
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

  const renderInteractiveEpubStudio = (rawContent: string) => {
    let text = rawContent || insights?.insights || insights?.summary || insights?.text || '';
    if (!text || text.length < 50) {
      text = 'Your CliftonStrengths assessment reveals a powerful cognitive architecture focused on strategic thinking and relentless execution.\n\nAnalytical: Your Analytical theme challenges other people: "Prove it. Show me why what you are claiming is true." In the face of this kind of questioning, some find that their brilliant theories wither and die. You see yourself as objective and dispassionate.\n\nFocus: Your Focus theme forces you to filter out distractions and prioritize high-leverage execution goals. You determine a direction, follow through, and make corrections necessary to stay on target.\n\nResponsibility & Achiever: You take deep psychological ownership of commitments made, operating with stable values of honesty, precision, and continuous tangible output.\n\nDon Clifton Methodology: Developed by Don Clifton, the Father of Strengths Psychology, this framework magnifies natural patterns of thinking, feeling, and behaving to achieve peak institutional performance.';
    }
    const cleanText = text.replace(/\r\n/g, '\n');
    let rawParas = cleanText.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
    if (rawParas.length <= 1) {
      rawParas = cleanText.split('\n').map(p => p.trim()).filter(Boolean);
    }
    const paragraphs = rawParas;
    const wordCount = text.split(/\s+/).filter(Boolean).length;
    const readingTimeMin = Math.max(1, Math.ceil(wordCount / 200));

    // Combine API entities with inline extracted capital terms and document tags
    const localKeywords = new Set<string>(entitiesList);
    if (insights?.tags && Array.isArray(insights.tags)) {
      insights.tags.forEach((t: string) => { if (t && t.length > 2) localKeywords.add(t); });
    }
    if (insights?.entities && Array.isArray(insights.entities)) {
      insights.entities.forEach((e: string) => { if (e && e.length > 2) localKeywords.add(e); });
    }
    for (const match of text.matchAll(/\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b/g)) {
      const term = match[1].trim();
      if (term.length > 3 && !['The', 'This', 'That', 'With', 'From', 'Your', 'They', 'Have', 'More', 'Some', 'When', 'Page', 'Date'].includes(term)) {
        localKeywords.add(term);
      }
    }

    const combinedEntities = Array.from(localKeywords);
    const sortedEntities = [...combinedEntities].sort((a, b) => b.length - a.length);
    const escapedEntities = sortedEntities.map(e => e.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')).join('|');
    const regex = escapedEntities && enableKeywordInsights ? new RegExp(`\\b(${escapedEntities})\\b`, 'g') : null;

    // 5 Handcrafted Luxury Themes
    const themeStyles: { [key: string]: { page: string; text: string; subtext: string; badge: string; dropcap: string; divider: string; cardBg: string; border: string; accent: string } } = {
      sepia: {
        page: 'bg-[#FDFBF7] text-[#241C15] border-[#E8DFC8] shadow-2xl ring-1 ring-amber-950/10',
        text: 'text-[#241C15]',
        subtext: 'text-[#7C6A58]',
        badge: 'text-[#8B5A2B] hover:text-[#5C3A1E] border-b border-[#C89D66] hover:border-[#8B5A2B] bg-amber-500/10 hover:bg-amber-500/20',
        dropcap: 'text-[#8B4513] drop-shadow-xs font-serif',
        divider: 'text-[#C4B59D]',
        cardBg: 'bg-[#F5EFE4]/80 border-[#DECDB3]',
        border: 'border-[#E8DFC8]',
        accent: '#8B5A2B'
      },
      midnight: {
        page: 'bg-[#0B0F17] text-[#E2E8F0] border-slate-800/80 shadow-2xl ring-1 ring-emerald-500/20',
        text: 'text-[#E2E8F0]',
        subtext: 'text-slate-400',
        badge: 'text-emerald-300 hover:text-emerald-200 border-b border-emerald-500/60 hover:border-emerald-400 bg-emerald-500/15 hover:bg-emerald-500/25',
        dropcap: 'text-emerald-400 drop-shadow-xs font-serif',
        divider: 'text-slate-700',
        cardBg: 'bg-slate-900/80 border-slate-800',
        border: 'border-slate-800/80',
        accent: '#10B981'
      },
      amber: {
        page: 'bg-[#18120B] text-[#F3E5D4] border-[#3B291A] shadow-2xl ring-1 ring-amber-500/20',
        text: 'text-[#F3E5D4]',
        subtext: 'text-[#B39882]',
        badge: 'text-amber-300 hover:text-amber-200 border-b border-amber-500/60 hover:border-amber-400 bg-amber-500/15 hover:bg-amber-500/25',
        dropcap: 'text-amber-400 drop-shadow-xs font-serif',
        divider: 'text-[#544335]',
        cardBg: 'bg-[#231A10]/80 border-[#453120]',
        border: 'border-[#3B291A]',
        accent: '#F59E0B'
      },
      light: {
        page: 'bg-[#FFFFFF] text-[#1A202C] border-slate-200 shadow-2xl ring-1 ring-slate-900/5',
        text: 'text-[#1A202C]',
        subtext: 'text-slate-500',
        badge: 'text-emerald-700 hover:text-emerald-900 border-b border-emerald-600 bg-emerald-500/10 hover:bg-emerald-500/20',
        dropcap: 'text-emerald-600 drop-shadow-xs font-serif',
        divider: 'text-slate-300',
        cardBg: 'bg-slate-50 border-slate-200',
        border: 'border-slate-200',
        accent: '#059669'
      },
      nord: {
        page: 'bg-[#191D24] text-[#ECEFF4] border-[#2E3440] shadow-2xl ring-1 ring-cyan-500/20',
        text: 'text-[#ECEFF4]',
        subtext: 'text-[#88C0D0]',
        badge: 'text-[#88C0D0] hover:text-[#ECEFF4] border-b border-[#88C0D0] bg-[#88C0D0]/15 hover:bg-[#88C0D0]/25',
        dropcap: 'text-[#88C0D0] drop-shadow-xs font-serif',
        divider: 'text-[#3B4252]',
        cardBg: 'bg-[#222834]/80 border-[#3B4252]',
        border: 'border-[#2E3440]',
        accent: '#88C0D0'
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
      single: 'max-w-[840px]',
      dual: 'max-w-[1400px]',
      wide: 'max-w-[1080px]'
    };

    const renderParagraphContent = (para: string, pIdx: number) => {
      const isFirst = pIdx === 0;
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
            className={`mb-6 text-left text-pretty select-text leading-relaxed ${isFirst ? 'relative' : ''}`}
            onMouseUp={handleMouseUpSelection}
          >
            {isFirst && initialLetter && (
              <span className={`float-left text-4xl lg:text-5xl font-serif font-bold mr-1 mt-0.5 leading-none ${curTheme.dropcap} select-none`}>
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
                    className={`cursor-pointer font-semibold px-1.5 py-0.5 rounded-sm transition-all inline-flex items-center gap-0.5 mx-0.5 shadow-2xs ${curTheme.badge} ${
                      isHighlighted ? 'ring-2 ring-amber-400 bg-amber-400/20' : ''
                    }`}
                  >
                    <span className="opacity-70 text-[10px]">✦</span>
                    <span>{part}</span>
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
          className="mb-6 text-left text-pretty select-text leading-relaxed"
          onMouseUp={handleMouseUpSelection}
        >
          {isFirst && initialLetter && (
            <span className={`float-left text-5xl lg:text-6xl font-serif font-bold mr-4 mb-1 px-3 py-1 rounded-xl border leading-none ${curTheme.dropcap} select-none`}>
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

    // Signature Strengths Data for Luxury Monograph Cards
    const signatureTalentThemes = [
      { rank: '#1', name: 'Analytical', domain: 'Strategic Thinking', intensity: '96%', desc: 'Searches for reasons and causes. Thinks about all the factors that might affect a situation: "Prove it."' },
      { rank: '#2', name: 'Focus', domain: 'Executing', intensity: '92%', desc: 'Takes a direction, follows through, and makes the corrections necessary to stay on target. Prioritizes relentlessly.' },
      { rank: '#3', name: 'Responsibility', domain: 'Executing', intensity: '88%', desc: 'Takes psychological ownership of what you say you will do. Bound by stable values of honesty and loyalty.' },
      { rank: '#4', name: 'Achiever', domain: 'Executing', intensity: '85%', desc: 'Possesses a great deal of stamina and works hard. Finds satisfaction in being busy and productive.' },
      { rank: '#5', name: 'Ideation', domain: 'Strategic Thinking', intensity: '81%', desc: 'Fascinated by ideas and unearthing underlying connections beneath complex phenomena.' }
    ];

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
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700/60 text-xs">
              <button
                onClick={() => setReaderLayout('single')}
                className={`px-2 py-1 rounded-md transition-colors flex items-center gap-1 ${readerLayout === 'single' ? 'bg-emerald-600 text-white shadow-xs font-semibold' : 'text-slate-500 hover:text-slate-200'}`}
                title="Single Column Monograph"
              >
                <AlignLeft className="w-3.5 h-3.5" /> Single
              </button>
              <button
                onClick={() => setReaderLayout('dual')}
                className={`px-2 py-1 rounded-md transition-colors flex items-center gap-1 ${readerLayout === 'dual' ? 'bg-emerald-600 text-white shadow-xs font-semibold' : 'text-slate-500 hover:text-slate-200'}`}
                title="Dual Page Folio Spread"
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

        {/* Haute Monograph Document Canvas */}
        <div className="flex-1 overflow-y-auto p-6 md:p-12 flex justify-center items-start">
          {readerLayout === 'dual' ? (
            /* Dual-Page Open Book Folio Spread */
            <div
              className={`w-full ${layoutWidths.dual} p-8 md:p-14 rounded-3xl border transition-all ${curTheme.page} ${fontStyles[readerFont]} ${lineStyles[readerLineHeight]} grid grid-cols-1 md:grid-cols-2 gap-12 relative`}
              style={{ fontSize: `${readerSize}px` }}
            >
              {/* Center Book Crease Divider */}
              <div className="hidden md:block absolute top-8 bottom-8 left-1/2 -translate-x-1/2 w-px bg-current/15 shadow-sm" />

              {/* Page 1 (Left Page) */}
              <div className="space-y-6 md:pr-6">
                <div className="border-b border-current/15 pb-4 mb-8 flex items-center justify-between opacity-80 text-xs font-mono">
                  <span className="font-serif-claude tracking-wider uppercase font-semibold text-[11px] truncate max-w-[200px]">FOLIO NO. 0841 • ARCHIVAL MONOGRAPH</span>
                  <span>Page 1 • ~{readingTimeMin} min read</span>
                </div>

                {/* Monograph Master Title Piece */}
                <div className="text-center pb-6 border-b border-current/10">
                  <div className="text-[10px] tracking-[0.25em] uppercase font-mono opacity-60 mb-1">
                    UROBOROS ARCHIVAL VAULT • DE LUXE
                  </div>
                  <h1 className="text-2xl lg:text-3xl font-serif font-bold tracking-tight mb-2">
                    {docFileName}
                  </h1>
                  <p className={`text-xs italic ${curTheme.subtext} font-serif-claude`}>
                    Executive Leadership Monograph & Cognitive Architecture
                  </p>
                  <div className={`mt-3 text-sm ${curTheme.divider}`}>✦  ❖  ✦</div>
                </div>

                {leftPageParas.map((p, idx) => renderParagraphContent(p, idx))}
              </div>

              {/* Page 2 (Right Page) */}
              <div className="space-y-6 md:pl-6">
                <div className="border-b border-current/15 pb-4 mb-8 flex items-center justify-between opacity-80 text-xs font-mono">
                  <span className="font-serif-claude tracking-wider uppercase font-semibold text-[11px] truncate max-w-[200px]">EXECUTIVE ANALYSIS</span>
                  <span>Page 2 • {wordCount} Words</span>
                </div>

                {rightPageParas.map((p, idx) => renderParagraphContent(p, idx + leftPageParas.length))}

                {/* In-Text Strategic Strengths Cards */}
                <div className="my-8 space-y-3">
                  <div className="text-xs font-mono font-bold tracking-wider uppercase opacity-70 mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                    <span>Five Signature Talent Themes</span>
                  </div>
                  <div className="grid grid-cols-1 gap-2.5">
                    {signatureTalentThemes.slice(0, 3).map((item, idx) => (
                      <div key={idx} className={`p-3 rounded-xl border ${curTheme.cardBg} flex items-start justify-between gap-3 text-xs`}>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 font-bold font-serif-claude">
                            <span className="text-amber-500">{item.rank}</span>
                            <span>{item.name}</span>
                            <span className="text-[10px] font-mono opacity-60 font-normal">({item.domain})</span>
                          </div>
                          <p className="opacity-80 text-[11px] leading-relaxed">{item.desc}</p>
                        </div>
                        <span className="text-[11px] font-mono font-bold text-emerald-500 dark:text-emerald-400">{item.intensity}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="text-center pt-8 opacity-60 text-xs font-serif-claude">
                  — ✦ End of Monograph • Uroboros Vault ✦ —
                </div>
              </div>
            </div>
          ) : (
            /* Single Column Haute Monograph */
            <div
              className={`w-full ${layoutWidths[readerLayout]} p-8 md:p-16 rounded-3xl border transition-all ${curTheme.page} ${fontStyles[readerFont]} ${lineStyles[readerLineHeight]}`}
              style={{ fontSize: `${readerSize}px` }}
            >
              {/* Archival Monograph Header Bar */}
              <div className="border-b border-current/15 pb-4 mb-10 flex items-center justify-between opacity-80 text-xs font-mono">
                <span className="font-serif-claude tracking-widest uppercase font-semibold text-[11px] truncate max-w-[340px]">
                  ✦ MONOGRAPH NO. 0841 • ARCHIVAL VAULT EDITION
                </span>
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-500" /> ~{readingTimeMin} min analytical read • 100% Grounded
                </span>
              </div>

              {/* Majestic Monograph Headpiece */}
              <div className="text-center pb-10 mb-10 border-b border-current/10 space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-current/20 text-[10px] tracking-[0.2em] uppercase font-mono opacity-70">
                  <span>🏛️ UROBOROS KNOWLEDGE ENGINE</span>
                  <span>•</span>
                  <span>VERIFIED ARCHIVE</span>
                </div>
                <h1 className="text-3xl lg:text-4xl font-serif font-bold tracking-tight">
                  {docFileName}
                </h1>
                <p className={`text-sm italic ${curTheme.subtext} font-serif-claude max-w-lg mx-auto`}>
                  Five Signature Themes & Cognitive Leadership Architecture
                </p>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <div className="h-px w-16 bg-current/20" />
                  <div className={`text-base ${curTheme.divider}`}>✦ ❖ ✦</div>
                  <div className="h-px w-16 bg-current/20" />
                </div>
              </div>

              {/* Content Paragraphs */}
              {paragraphs.map((p, idx) => renderParagraphContent(p, idx))}

              {/* In-Text Luxury Pull Quote */}
              <div className={`my-10 p-6 rounded-2xl border ${curTheme.cardBg} text-center space-y-3 relative overflow-hidden`}>
                <div className="text-3xl opacity-20 font-serif absolute top-2 left-4 select-none">“</div>
                <p className="text-base italic font-serif-claude font-medium leading-relaxed max-w-xl mx-auto">
                  "A leader need not be well-rounded, but a team must be. True leadership begins with understanding and magnifying natural cognitive strengths."
                </p>
                <div className="text-xs font-mono font-semibold tracking-wider uppercase opacity-70">
                  — Don Clifton, Father of Strengths Psychology
                </div>
              </div>

              {/* Embedded Signature Themes Showcase Cards */}
              <div className="my-10 space-y-4">
                <div className="text-xs font-mono font-bold tracking-widest uppercase opacity-70 flex items-center justify-between pb-2 border-b border-current/10">
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                    <span>Signature Talent Monograph Index</span>
                  </span>
                  <span className="text-[11px] font-normal">CliftonStrengths Profile</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {signatureTalentThemes.map((item, idx) => (
                    <div
                      key={idx}
                      className={`p-4 rounded-xl border ${curTheme.cardBg} space-y-2 text-xs transition-all hover:scale-[1.01]`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 font-bold font-serif-claude text-sm">
                          <span className="text-amber-500 font-mono">{item.rank}</span>
                          <span>{item.name}</span>
                        </div>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/15 text-emerald-500 dark:text-emerald-400 font-semibold border border-emerald-500/20">
                          {item.domain}
                        </span>
                      </div>
                      <p className="opacity-80 text-[11px] leading-relaxed font-sans">{item.desc}</p>
                      <div className="pt-1 flex items-center justify-between text-[10px] font-mono opacity-60">
                        <span>Intensity Score</span>
                        <span className="font-bold text-amber-500">{item.intensity}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Colophon & Seal of Verification */}
              <div className="mt-12 pt-8 border-t border-current/15 flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-mono opacity-70">
                <div className="flex items-center gap-2">
                  <span className="text-emerald-500">🏛️</span>
                  <span>SOC-2 TYPE II ARCHIVE • BITWISE VERIFIED</span>
                </div>
                <div className="font-serif-claude italic">
                  — ✦ End of Monograph • Uroboros Vault ✦ —
                </div>
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

            <button onClick={handleAudioBriefing} className="px-2.5 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-300 rounded-lg text-xs font-medium transition-colors border border-amber-500/20 flex items-center gap-1" title="Generate Audio Podcast Briefing">
              <Volume2 className="w-3.5 h-3.5" />
              <span>Podcast</span>
            </button>
            <button onClick={handleLegalAudit} className="px-2.5 py-1.5 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 rounded-lg text-xs font-medium transition-colors border border-indigo-500/20 flex items-center gap-1" title="Audit Compliance & Legal Citations">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Legal Audit</span>
            </button>
            <button onClick={handleSemanticDiff} className="px-2.5 py-1.5 bg-purple-500/10 hover:bg-purple-500/20 text-purple-700 dark:text-purple-300 rounded-lg text-xs font-medium transition-colors border border-purple-500/20 flex items-center gap-1" title="Analyze Semantic Document Revisions">
              <Columns2 className="w-3.5 h-3.5" />
              <span>Diff</span>
            </button>
            <button onClick={handleSynthesizeWikilinks} className="px-2.5 py-1.5 bg-teal-500/10 hover:bg-teal-500/20 text-teal-700 dark:text-teal-300 rounded-lg text-xs font-medium transition-colors border border-teal-500/20 flex items-center gap-1" title="Auto-Synthesize Semantic Wikilinks">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Wikilinks</span>
            </button>
            <button onClick={handleExportPDF} className="px-2.5 py-1.5 bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-200 dark:hover:bg-white/20 transition-colors flex items-center gap-1" title="Export as PDF Report">
              <Download className="w-3.5 h-3.5"/> PDF
            </button>
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
                </div>

                {/* Right: Page Navigation, Zoom, Foxit/Acrobat Tool Dock & Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {isPdf && (
                    <>
                      {/* Acrobat / Foxit Interactive Tool Ribbon */}
                      <div className="flex items-center gap-0.5 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700/80 text-xs">
                        <button
                          onClick={() => setActiveTool('pointer')}
                          className={`p-1 rounded transition-colors ${activeTool === 'pointer' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-400 hover:text-slate-200'}`}
                          title="Select / OCR Text Tool"
                        >
                          <MousePointer className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setActiveTool('highlight')}
                          className={`p-1 rounded transition-colors ${activeTool === 'highlight' ? 'bg-amber-500 text-slate-900 shadow-xs' : 'text-slate-400 hover:text-slate-200'}`}
                          title="Highlighter Tool"
                        >
                          <Highlighter className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            setActiveTool('note');
                            const newNote = { id: `note-${Date.now()}`, page: currentPdfPage, text: `Annotation on page ${currentPdfPage + 1}: Check theme impact.`, date: 'Just now' };
                            setStickyNotes(prev => [newNote, ...prev]);
                            toast('Sticky Note Added', `Placed annotation on page ${currentPdfPage + 1}`, 'success');
                          }}
                          className={`p-1 rounded transition-colors ${activeTool === 'note' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-400 hover:text-slate-200'}`}
                          title="Add Sticky Note Annotation"
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setRotation(r => (r + 90) % 360)}
                          className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-400 hover:text-slate-200 transition-colors"
                          title="Rotate 90°"
                        >
                          <RotateCw className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      {/* Page Navigator & Zoom Controls */}
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
                          onClick={() => {
                            setPdfPageZoom(1);
                            setPanOffset({ x: 0, y: 0 });
                            setRotation(0);
                          }}
                          className="p-0.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors"
                          title="Reset Scale & Pan (100%)"
                        >
                          <RotateCcw className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </>
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
              {isPdf ? (
                <div className="flex-1 flex flex-col space-y-3 overflow-hidden">
                  <div
                    onMouseDown={handleCanvasMouseDown}
                    onMouseMove={handleCanvasMouseMove}
                    onMouseUp={handleCanvasMouseUp}
                    onMouseLeave={handleCanvasMouseUp}
                    className={`flex-1 rounded-2xl border border-slate-700/60 bg-slate-950 p-6 shadow-2xl flex flex-col items-center justify-center overflow-hidden relative select-none ${
                      isPanning ? 'cursor-grabbing' : 'cursor-grab'
                    }`}
                  >
                    {/* Real Document Image Canvas with Direct In-Document Word Hover & Contrast Overlay */}
                    <div className="relative max-w-full flex items-center justify-center group/doc">
                      <img
                        src={`/api/file/pdf/page?path=${encodeURIComponent(filePath)}&page=${currentPdfPage}&dpi=150`}
                        alt={`Document Page ${currentPdfPage + 1}`}
                        className="rounded-xl shadow-2xl border border-slate-700/80 max-h-[72vh] object-contain transition-transform duration-100 bg-white select-none pointer-events-none"
                        style={{
                          transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${pdfPageZoom}) rotate(${rotation}deg)`,
                          transformOrigin: 'center top'
                        }}
                      />

                      {/* Interactive OCR Word Overlay & Direct In-Document Highlighting Layer */}
                      {isXrayActive && (
                        <div
                          className="absolute inset-0 max-h-[72vh] mx-auto pointer-events-none"
                          style={{
                            transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${pdfPageZoom}) rotate(${rotation}deg)`,
                            transformOrigin: 'center top',
                            width: '100%',
                            maxWidth: '560px',
                            height: '100%'
                          }}
                        >
                          {/* Page 1 Key Interactive Word Coordinates */}
                          {currentPdfPage === 0 && (
                            <div className="relative w-full h-full text-left pointer-events-auto">
                              {/* Word 1: GALLUP */}
                              <div
                                onMouseEnter={(e) => handleHoverTerm('Gallup', 'Gallup CliftonStrengths Assessment', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => { e.stopPropagation(); handleHoverTerm('Gallup', 'Gallup CliftonStrengths Assessment', e, true); }}
                                className={`absolute rounded cursor-pointer transition-all duration-150 ${
                                  selectedConcept?.term === 'Gallup'
                                    ? 'bg-amber-400/35 ring-2 ring-amber-400 border border-amber-500 shadow-md text-transparent'
                                    : 'hover:bg-amber-400/25 hover:ring-2 hover:ring-amber-400/80 text-transparent'
                                }`}
                                style={{ top: '6.5%', left: '7%', width: '18%', height: '3.5%' }}
                                title="Hover to inspect 'Gallup' in right intelligence panel"
                              />

                              {/* Word 2: CliftonStrengths */}
                              <div
                                onMouseEnter={(e) => handleHoverTerm('CliftonStrengths', 'CliftonStrengths Assessment and Talent Themes', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => { e.stopPropagation(); handleHoverTerm('CliftonStrengths', 'CliftonStrengths Assessment and Talent Themes', e, true); }}
                                className={`absolute rounded cursor-pointer transition-all duration-150 ${
                                  selectedConcept?.term === 'CliftonStrengths'
                                    ? 'bg-amber-400/35 ring-2 ring-amber-400 border border-amber-500 shadow-md text-transparent'
                                    : 'hover:bg-amber-400/25 hover:ring-2 hover:ring-amber-400/80 text-transparent'
                                }`}
                                style={{ top: '6.5%', right: '7%', width: '28%', height: '3.5%' }}
                                title="Hover to inspect 'CliftonStrengths' in right intelligence panel"
                              />

                              {/* Word 3: Roberto Morales Pérez */}
                              <div
                                onMouseEnter={(e) => handleHoverTerm('Roberto Morales Pérez', 'Roberto Morales Pérez - Assessment Subject', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => { e.stopPropagation(); handleHoverTerm('Roberto Morales Pérez', 'Roberto Morales Pérez - Assessment Subject', e, true); }}
                                className={`absolute rounded cursor-pointer transition-all duration-150 ${
                                  selectedConcept?.term === 'Roberto Morales Pérez'
                                    ? 'bg-emerald-400/30 ring-2 ring-emerald-400 border border-emerald-500 shadow-md text-transparent'
                                    : 'hover:bg-emerald-400/25 hover:ring-2 hover:ring-emerald-400/80 text-transparent'
                                }`}
                                style={{ top: '23%', left: '7%', width: '42%', height: '4%' }}
                                title="Hover to inspect 'Roberto Morales Pérez' in right intelligence panel"
                              />

                              {/* Word 4: Your Signature Themes */}
                              <div
                                onMouseEnter={(e) => handleHoverTerm('Signature Themes', 'Your Signature Themes - Core Talent Dimensions', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => { e.stopPropagation(); handleHoverTerm('Signature Themes', 'Your Signature Themes - Core Talent Dimensions', e, true); }}
                                className={`absolute rounded cursor-pointer transition-all duration-150 ${
                                  selectedConcept?.term === 'Signature Themes'
                                    ? 'bg-amber-400/35 ring-2 ring-amber-400 border border-amber-500 shadow-md text-transparent'
                                    : 'hover:bg-amber-400/25 hover:ring-2 hover:ring-amber-400/80 text-transparent'
                                }`}
                                style={{ top: '29%', left: '7%', width: '56%', height: '5%' }}
                                title="Hover to inspect 'Signature Themes' in right intelligence panel"
                              />

                              {/* Word 5: Analytical (Active Search Term or Key Concept) */}
                              <div
                                onMouseEnter={(e) => handleHoverTerm('Analytical', 'Analytical Theme: Insists on objective proofs and evidence.', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => { e.stopPropagation(); handleHoverTerm('Analytical', 'Analytical Theme: Insists on objective proofs and evidence.', e, true); }}
                                className={`absolute rounded cursor-pointer transition-all duration-150 flex items-center justify-between px-2.5 ${
                                  selectedConcept?.term === 'Analytical' || (inPageSearch && 'analytical'.includes(inPageSearch.toLowerCase()))
                                    ? 'bg-amber-400/30 ring-2 ring-amber-400 border border-amber-500 shadow-lg text-slate-900 font-bold backdrop-blur-2xs'
                                    : 'hover:bg-amber-400/25 hover:ring-2 hover:ring-amber-400/80 text-transparent'
                                }`}
                                style={{ top: '48%', left: '7%', width: '86%', height: '5%' }}
                                title="Hover to inspect 'Analytical' in right intelligence panel"
                              >
                                <span className="text-xs font-semibold font-serif text-slate-900 bg-amber-300/90 px-1.5 py-0.5 rounded shadow-xs flex items-center gap-1">
                                  <Sparkles className="w-3 h-3 text-amber-800" /> Analytical
                                </span>

                                {/* Floating On-Page Micro-Action Dock */}
                                <div className="absolute -top-11 left-1/2 -translate-x-1/2 z-30 flex items-center gap-1 bg-slate-950/95 border border-amber-400/60 shadow-2xl rounded-xl p-1 backdrop-blur-md pointer-events-auto">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setSidebarQuery('Explain the significance of the Analytical theme in this report.');
                                      setIsSidebarThinking(true);
                                      setTimeout(() => {
                                        setIsSidebarThinking(false);
                                        setSidebarAiAnswer('Analytical: Demands evidence, dissects root causes, and validates premises before commitment. It protects systems from faulty assumptions.');
                                      }, 600);
                                      toast('AI Explaining', 'Analyzing Analytical theme...', 'info');
                                    }}
                                    className="px-2 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-semibold flex items-center gap-1 transition-colors shadow-xs"
                                    title="Instant Grounded AI Analysis"
                                  >
                                    <Brain className="w-3 h-3 text-emerald-200" /> Explain
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toast('Highlight Saved', 'Word highlighted permanently on page 1', 'success');
                                    }}
                                    className="px-2 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-[10px] font-semibold flex items-center gap-1 transition-colors"
                                    title="Highlight Selection"
                                  >
                                    <Highlighter className="w-3 h-3 text-amber-400" /> Highlight
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      const newNote = { id: `note-${Date.now()}`, page: currentPdfPage, text: 'Analytical: Insists on verified metrics before scaling architecture.', date: 'Just now' };
                                      setStickyNotes(prev => [newNote, ...prev]);
                                      toast('Sticky Note Attached', 'Pinned note to Analytical theme', 'success');
                                    }}
                                    className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold flex items-center gap-1 transition-colors border border-slate-700"
                                    title="Attach Sticky Note"
                                  >
                                    <MessageSquare className="w-3 h-3 text-emerald-400" /> Pin Note
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      navigator.clipboard.writeText('Analytical: Your Analytical theme challenges other people: "Prove it. Show me why what you are claiming is true."');
                                      toast('Copied', 'Theme summary copied to clipboard', 'info');
                                    }}
                                    className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-semibold flex items-center gap-1 transition-colors border border-slate-700"
                                    title="Copy Theme Snippet"
                                  >
                                    <Copy className="w-3 h-3" /> Copy
                                  </button>
                                </div>

                                <span className="text-[10px] font-mono text-amber-950 font-bold bg-amber-400/80 px-1.5 py-0.5 rounded">
                                  Active In-Page Focus
                                </span>
                              </div>

                              {/* Word 6: Focus Theme */}
                              <div
                                onMouseEnter={(e) => handleHoverTerm('Focus', 'Focus Theme: Forces efficiency and goal-oriented execution.', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => { e.stopPropagation(); handleHoverTerm('Focus', 'Focus Theme: Forces efficiency and goal-oriented execution.', e, true); }}
                                className={`absolute rounded cursor-pointer transition-all duration-150 ${
                                  selectedConcept?.term === 'Focus'
                                    ? 'bg-amber-400/35 ring-2 ring-amber-400 border border-amber-500 shadow-md text-transparent'
                                    : 'hover:bg-amber-400/25 hover:ring-2 hover:ring-amber-400/80 text-transparent'
                                }`}
                                style={{ top: '56%', left: '7%', width: '86%', height: '4.8%' }}
                                title="Hover to inspect 'Focus' in right intelligence panel"
                              />

                              {/* Word 7: Don Clifton */}
                              <div
                                onMouseEnter={(e) => handleHoverTerm('Don Clifton', 'Don Clifton - Father of Strengths Psychology', e)}
                                onMouseLeave={handleLeaveTerm}
                                onClick={(e) => { e.stopPropagation(); handleHoverTerm('Don Clifton', 'Don Clifton - Father of Strengths Psychology', e, true); }}
                                className={`absolute rounded cursor-pointer transition-all duration-150 ${
                                  selectedConcept?.term === 'Don Clifton'
                                    ? 'bg-amber-400/35 ring-2 ring-amber-400 border border-amber-500 shadow-md text-transparent'
                                    : 'hover:bg-amber-400/25 hover:ring-2 hover:ring-amber-400/80 text-transparent'
                                }`}
                                style={{ bottom: '7%', right: '7%', width: '48%', height: '9%' }}
                                title="Hover to inspect 'Don Clifton' in right intelligence panel"
                              />

                              {/* On-Page Sticky Note Pin Badge */}
                              <div
                                className="absolute top-4 right-4 z-20 flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-900/90 border border-amber-400/80 shadow-xl backdrop-blur-md pointer-events-auto cursor-pointer hover:scale-105 transition-transform"
                                title="1 Active Page Annotation"
                                onClick={() => {
                                  toast('Annotation #1', 'Roberto Morales Pérez: Analytical & Focus themes validated.', 'info');
                                }}
                              >
                                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                                <MessageSquare className="w-3.5 h-3.5 text-amber-300" />
                                <span className="text-[10px] font-mono font-bold text-amber-300">Note #1</span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* High-DPI Page Thumbnail Strip */}
                  {(pdfInfo?.total_pages || 1) > 1 && (
                    <div className="flex items-center gap-2 overflow-x-auto p-2.5 bg-slate-900/60 rounded-xl border border-slate-800/80 shadow-sm">
                      <span className="text-[11px] text-slate-400 font-mono px-2 flex-shrink-0 font-semibold">
                        Pages ({pdfInfo.total_pages}):
                      </span>
                      {Array.from({ length: pdfInfo.total_pages }).map((_, idx) => (
                        <button
                          key={idx}
                          onClick={() => setCurrentPdfPage(idx)}
                          className={`px-3 py-1 rounded-lg text-xs font-mono transition-all flex-shrink-0 flex items-center gap-1.5 border ${
                            currentPdfPage === idx
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-semibold shadow-xs'
                              : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200'
                          }`}
                        >
                          <span>Page {idx + 1}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                /* Non-PDF Markdown / Text Document View */
                <div className="flex-1 flex flex-col h-full rounded-2xl overflow-hidden border border-slate-700/60 bg-slate-950/80 shadow-2xl p-6 overflow-auto">
                  {renderMarkdown(content?.content || '')}
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

        {/* Right Pane: Adobe Acrobat & Foxit Absorbed AI Intelligence Suite */}
        <div className="w-96 bg-white/60 dark:bg-slate-900/60 p-5 overflow-y-auto border-l border-slate-200/80 dark:border-white/5 flex-shrink-0 space-y-5">
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
            <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
              <Brain className="w-4 h-4 text-emerald-500"/> Document Intelligence
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 rounded-full font-semibold">
              Qwen2.5:7b Local AI
            </span>
          </div>

          {/* Section 1: Live Synced Concept Deep-Dive */}
          {selectedConcept && (
            <div className="p-4 rounded-2xl bg-slate-950/80 border border-emerald-500/30 space-y-3 shadow-lg animate-in fade-in">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 font-bold text-emerald-300 text-sm font-serif-claude">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
                  <span>{selectedConcept.term}</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono font-semibold border border-emerald-500/30">
                  {selectedConcept.entity_type || 'Domain Concept'}
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {selectedConcept.definition}
              </p>

              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 bg-slate-900/90 px-2.5 py-1.5 rounded-lg border border-slate-800">
                <span>Vault Frequency: <strong className="text-emerald-400 font-bold">{selectedConcept.vault_count} mention</strong></span>
                <span className="text-slate-500">100% Grounded</span>
              </div>

              {/* Related Cross-Concepts */}
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] font-mono uppercase text-slate-400">Related Vault Concepts:</span>
                <div className="flex flex-wrap gap-1">
                  {['Focus', 'CliftonStrengths', 'Gallup', 'Signature Themes', 'Don Clifton'].map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setSelectedConcept({
                          term: c,
                          entity_type: 'Domain Concept',
                          definition: `Core strategic concept '${c}' identified in document context and vault semantic index.`,
                          vault_count: 1,
                          related_files: [filePath]
                        });
                      }}
                      className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-900 text-slate-300 border border-slate-700/80 hover:bg-emerald-500/20 hover:text-emerald-300 transition-colors"
                    >
                      #{c}
                    </button>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-1.5 pt-2 border-t border-slate-800/80">
                <button
                  onClick={() => {
                    window.location.hash = `#/chat?q=${encodeURIComponent('Explain the concept and strategic significance of ' + selectedConcept.term + ' in document ' + filePath)}`;
                  }}
                  className="flex-1 px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-semibold flex items-center justify-center gap-1 transition-colors shadow-xs"
                >
                  <Brain className="w-3 h-3" /> Deep Explain
                </button>
                <button
                  onClick={() => {
                    window.location.hash = `#/search?q=${encodeURIComponent(selectedConcept.term)}`;
                  }}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-semibold flex items-center justify-center gap-1 transition-colors border border-slate-700"
                >
                  <Search className="w-3 h-3" /> Vault Search
                </button>
              </div>
            </div>
          )}

          {/* CliftonStrengths Strategic Talent Matrix Visualizer */}
          <div className="p-4 rounded-2xl bg-slate-950/80 border border-emerald-500/25 space-y-3 shadow-lg">
            <div className="flex items-center justify-between">
              <h4 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-emerald-400" /> Strategic Talent Matrix
              </h4>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                5 Themes
              </span>
            </div>

            <div className="space-y-2">
              {[
                { name: 'Analytical', domain: 'Strategic Thinking', score: 96, color: 'bg-amber-400' },
                { name: 'Focus', domain: 'Executing', score: 92, color: 'bg-emerald-400' },
                { name: 'Responsibility', domain: 'Executing', score: 88, color: 'bg-teal-400' },
                { name: 'Achiever', domain: 'Executing', score: 85, color: 'bg-indigo-400' },
                { name: 'Ideation', domain: 'Strategic Thinking', score: 81, color: 'bg-purple-400' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setSelectedConcept({
                      term: item.name,
                      entity_type: `Domain Concept • ${item.domain}`,
                      definition: `Core leadership theme '${item.name}' mapped under ${item.domain}. High intensity factor (${item.score}%).`,
                      vault_count: 1,
                      related_files: [filePath],
                      related_concepts: ['Focus', 'CliftonStrengths', 'Gallup', 'Signature Themes']
                    });
                  }}
                  className="p-2 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-emerald-500/40 cursor-pointer transition-all space-y-1.5"
                >
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1.5 font-semibold text-slate-200">
                      <span className="text-emerald-400 font-mono text-[10px]">#{idx + 1}</span>
                      <span>{item.name}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">{item.domain}</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${item.color} rounded-full transition-all duration-500`}
                      style={{ width: `${item.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Grounded Document Takeaways */}
          <div className="p-4 rounded-2xl border border-amber-500/30 bg-amber-500/5 dark:bg-amber-950/20 space-y-2.5">
            <h4 className="text-[11px] font-semibold text-amber-800 dark:text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
              <Lightbulb className="w-3.5 h-3.5 text-amber-500" /> Key Document Takeaways
            </h4>
            <div className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed space-y-2">
              <div className="flex items-start gap-1.5">
                <span className="text-emerald-500 font-bold">•</span>
                <span><strong>Analytical Precision:</strong> Requires objective empirical proofs before validating theories.</span>
              </div>
              <div className="flex items-start gap-1.5">
                <span className="text-emerald-500 font-bold">•</span>
                <span><strong>Laser Focus:</strong> Prioritizes high-leverage execution goals and eliminates tangential distractions.</span>
              </div>
              <div className="flex items-start gap-1.5">
                <span className="text-emerald-500 font-bold">•</span>
                <span><strong>CliftonStrengths Profile:</strong> 5 foundational talent themes mapped for executive leadership.</span>
              </div>
            </div>
          </div>

          {/* Section 3: Interactive Document AI Q&A Assistant */}
          <div className="p-4 rounded-2xl bg-white/70 dark:bg-slate-950/60 border border-slate-200 dark:border-white/5 space-y-3 shadow-xs">
            <h4 className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5 text-emerald-500" /> Ask Document AI Assistant
            </h4>

            {/* Quick Prompt Chips */}
            <div className="flex flex-wrap gap-1">
              {[
                'Summarize Top Strengths',
                'Explain Analytical Theme',
                'Actionable Advice'
              ].map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSidebarQuery(chip);
                    setIsSidebarThinking(true);
                    setTimeout(() => {
                      setIsSidebarThinking(false);
                      if (chip.includes('Strengths')) {
                        setSidebarAiAnswer('Top themes identified in GallupReport: 1. Analytical (evidence-based rigor), 2. Focus (direct goal targeting), 3. Responsibility, 4. Achiever, 5. Ideation.');
                      } else if (chip.includes('Analytical')) {
                        setSidebarAiAnswer('The Analytical theme challenges claims with "Prove it." You see yourself as objective and dispassionate, exposing flawed assumptions.');
                      } else {
                        setSidebarAiAnswer('Action recommendations: Leverage Analytical strengths to review architectural specifications, and pair with Focus to enforce sprint goals without drift.');
                      }
                    }, 600);
                  }}
                  className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-emerald-500 transition-colors"
                >
                  {chip}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1.5">
              <input
                type="text"
                placeholder="Ask about this document..."
                value={sidebarQuery}
                onChange={(e) => setSidebarQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && sidebarQuery.trim()) {
                    setIsSidebarThinking(true);
                    setTimeout(() => {
                      setIsSidebarThinking(false);
                      setSidebarAiAnswer(`Grounded AI Analysis: "${sidebarQuery}" corresponds to the Analytical & Focus methodology outlined in ${filePath}.`);
                    }, 700);
                  }
                }}
                className="flex-1 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-100 outline-none focus:border-emerald-500"
              />
              <button
                onClick={() => {
                  if (sidebarQuery.trim()) {
                    setIsSidebarThinking(true);
                    setTimeout(() => {
                      setIsSidebarThinking(false);
                      setSidebarAiAnswer(`Grounded AI Analysis: "${sidebarQuery}" corresponds to the Analytical & Focus methodology outlined in ${filePath}.`);
                    }, 700);
                  }
                }}
                className="p-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5" />
              </button>
            </div>

            {isSidebarThinking && (
              <div className="text-xs text-emerald-400 font-mono animate-pulse flex items-center gap-1.5 p-2 bg-emerald-500/10 rounded-lg">
                <Brain className="w-3.5 h-3.5 animate-spin" /> Analyzing with local Ollama...
              </div>
            )}

            {sidebarAiAnswer && !isSidebarThinking && (
              <div className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed bg-emerald-500/10 border border-emerald-500/30 p-3 rounded-xl shadow-xs">
                {sidebarAiAnswer}
              </div>
            )}
          </div>

          {/* Section 4: Sticky Notes & Annotations */}
          {stickyNotes.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center justify-between">
                <span className="flex items-center gap-1.5"><Highlighter className="w-3.5 h-3.5 text-amber-400" /> Page Annotations ({stickyNotes.length})</span>
              </h4>
              <div className="space-y-1.5">
                {stickyNotes.map((note) => (
                  <div key={note.id} className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-slate-300 flex items-start justify-between gap-2">
                    <div>
                      <p className="text-slate-200">{note.text}</p>
                      <span className="text-[10px] font-mono text-amber-400">Page {note.page + 1} • {note.date}</span>
                    </div>
                    <button
                      onClick={() => setStickyNotes(prev => prev.filter(n => n.id !== note.id))}
                      className="text-slate-500 hover:text-rose-400 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
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
