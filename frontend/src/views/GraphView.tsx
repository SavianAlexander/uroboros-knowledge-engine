import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { glassCardClasses, debounce, emeraldBadgeClasses, goldBadgeClasses, wineBadgeClasses } from '../lib/utils';
import { Filter, Maximize, RotateCcw, Download, Sparkles, Share2 } from 'lucide-react';
import { api } from '../lib/api';
import { useToast } from '../components/Toast';
import { useApp } from '../store/AppContext';

export default function GraphView() {
  const { toast } = useToast();
  const { activeWorkspace, setActiveView, setSearchQuery } = useApp();

  const handleExportGraphML = async () => {
    try {
      toast('Exporting GraphML', 'Generating XML topology payload...', 'info');
      const blob = await api.exportGraphML();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge_graph_${new Date().toISOString().slice(0, 10)}.graphml`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast('GraphML Exported', 'Downloaded GraphML XML payload', 'success');
    } catch (e: any) {
      toast('Export Failed', e.message || 'Could not export GraphML', 'error');
    }
  };

  const handleCommunityClusters = async () => {
    try {
      toast('Computing Clusters', 'Evaluating Louvain modularity partitions...', 'info');
      const res = await api.communityClusters();
      toast('Community Clusters Ready', `Detected ${(res?.clusters || []).length} dense graph communities`, 'success');
    } catch (e: any) {
      toast('Cluster Error', e.message || 'Failed to detect clusters', 'error');
    }
  };

  const handleKnowledgeGaps = async () => {
    try {
      toast('Discovering Gaps', 'Finding unlinked concepts and orphaned nodes...', 'info');
      const res = await api.knowledgeGaps();
      toast('Knowledge Gaps Audit', `Discovered ${(res?.orphaned_concepts || res?.gaps || []).length} knowledge opportunities`, 'success');
    } catch (e: any) {
      toast('Gap Discovery Error', e.message || 'Failed to discover gaps', 'error');
    }
  };

  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<any>();
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [filter, setFilter] = useState<string>('');
  const [searchInput, setSearchInput] = useState<string>('');
  const [categoryFilters, setCategoryFilters] = useState<Record<string, boolean>>({
    document: true, tag: true, concept: true,
  });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  const debouncedSetFilter = useCallback(debounce((val: string) => setFilter(val), 150), []);

  useEffect(() => {
    setLoading(true);
    api.graphClusters().catch(() => {});
    api.graphWikilinks().catch(() => {});
    api.graphData()
      .then(data => {
        if (!data) throw new Error('No data');
        const n = (data.nodes || []).map((d: any) => ({
          ...d,
          type: d.type || d.category || 'document',
          name: d.label || d.title || d.filename || d.id,
        }));
        const e = (data.edges || data.links || []).map((d: any) => ({ 
          ...d,
          source: d.source,
          target: d.target,
          name: d.type || d.relation || ''
        }));
        setNodes(n);
        setEdges(e);
        setLoading(false);
      })
      .catch(() => {
        setNodes([]);
        setEdges([]);
        setLoading(false);
      });
  }, [activeWorkspace]);

  useEffect(() => {
    if (!containerRef.current) return;
    
    const handleResize = debounce((entries: ResizeObserverEntry[]) => {
      if (entries[0]) {
        setDimensions({
          width: entries[0].contentRect.width,
          height: entries[0].contentRect.height
        });
      }
    }, 150);
    
    const observer = new ResizeObserver(handleResize);
    observer.observe(containerRef.current);
    
    setDimensions({
       width: containerRef.current.clientWidth,
       height: containerRef.current.clientHeight
    });

    return () => observer.disconnect();
  }, [loading]);

  const filteredNodes = useMemo(() => {
    return nodes.filter(n => {
      if (!categoryFilters[n.type]) return false;
      if (filter && !n.name.toLowerCase().includes(filter.toLowerCase())) return false;
      return true;
    });
  }, [nodes, filter, categoryFilters]);

  const filteredEdges = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    return edges.filter(e => {
      const sid = typeof e.source === 'object' ? e.source.id : e.source;
      const tid = typeof e.target === 'object' ? e.target.id : e.target;
      return nodeIds.has(sid) && nodeIds.has(tid);
    });
  }, [edges, filteredNodes]);

  const graphData = useMemo(() => {
    return { nodes: filteredNodes, links: filteredEdges };
  }, [filteredNodes, filteredEdges]);

  const materialCache = useRef<Record<string, THREE.SpriteMaterial>>({});

  useEffect(() => {
    return () => {
      Object.values(materialCache.current).forEach((mat: any) => {
        mat.map?.dispose();
        mat.dispose();
      });
    };
  }, []);

  const nodeThreeObject = useCallback((node: any) => {
    const type = node.type || 'document';
    const isSelected = selectedNode && selectedNode.id === node.id;
    const cacheKey = `${type}-${isSelected}`;

    if (!materialCache.current[cacheKey]) {
      const size = 128;
      const canvas = document.createElement('canvas');
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext('2d');
      if (!ctx) return false;

      let color = '#059669'; // Emerald
      let icon = '📄';
      
      if (type === 'document') {
        color = '#059669'; // Emerald
        icon = '📄';
      } else if (type === 'tag') {
        color = '#9F1239'; // Wine Red
        icon = '🏷️';
      } else if (type === 'concept') {
        color = '#D97706'; // Mustard Gold
        icon = '💡';
      }

      ctx.beginPath();
      ctx.arc(size / 2, size / 2, size / 2 - 4, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();

      if (isSelected) {
        ctx.lineWidth = 6;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();
      } else {
        ctx.lineWidth = 4;
        ctx.strokeStyle = '#020617';
        ctx.stroke();
      }

      ctx.font = '60px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(icon, size / 2, size / 2 + 6);

      const texture = new THREE.CanvasTexture(canvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      const material = new THREE.SpriteMaterial({ map: texture, depthTest: false });
      materialCache.current[cacheKey] = material;
    }

    const sprite = new THREE.Sprite(materialCache.current[cacheKey]);
    const scale = type === 'document' ? 14 : 10;
    sprite.scale.set(scale, scale, 1);
    
    return sprite;
  }, [selectedNode]);

  const linkColor = useCallback((link: any) => {
    const type = link.type || link.relation || link.name;
    if (type === 'tagged_with') return '#10B98170'; // Emerald
    if (type === 'wikilink_to') return '#0D948870'; // Teal
    if (type === 'shared_tag_cluster') return '#F59E0B70'; // Gold
    if (type === 'mentions') return '#BE123C70'; // Wine Red
    return '#47556960';
  }, []);

  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node);
    const distance = 80;
    const distRatio = 1 + distance / (Math.hypot(node.x, node.y, node.z) || 1);
    
    fgRef.current?.cameraPosition(
      { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
      node,
      1000
    );
  }, [fgRef]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center gap-2 text-slate-400 text-sm">
        <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <span>Initializing 3D Vector Knowledge Graph...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full relative font-sans" ref={containerRef}>
      {/* Floating Top Controls */}
      <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-2.5 pointer-events-auto">
          <input
            type="text"
            placeholder="Filter knowledge graph..."
            value={searchInput}
            onChange={(e) => {
              setSearchInput(e.target.value);
              debouncedSetFilter(e.target.value);
            }}
            className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:border-emerald-500/60 shadow-lg w-56"
          />
          <div className="flex gap-1 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl p-1 shadow-lg">
            {(['document', 'tag', 'concept'] as const).map(cat => (
              <button
                key={cat}
                onClick={() => setCategoryFilters(prev => ({ ...prev, [cat]: !prev[cat] }))}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                  categoryFilters[cat]
                    ? cat === 'document' ? 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30'
                      : cat === 'tag' ? 'bg-rose-500/20 text-rose-700 dark:text-rose-300 border border-rose-500/30'
                      : 'bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 pointer-events-auto">
            <button
              onClick={handleCommunityClusters}
              className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2 text-xs font-semibold text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/10 transition-colors shadow-lg flex items-center gap-1.5"
              title="Compute Louvain Community Clusters"
            >
              <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
              <span>Clusters</span>
            </button>
            <button
              onClick={handleKnowledgeGaps}
              className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2 text-xs font-semibold text-amber-700 dark:text-amber-300 hover:bg-amber-500/10 transition-colors shadow-lg flex items-center gap-1.5"
              title="Discover Vault Knowledge Gaps"
            >
              <Filter className="w-3.5 h-3.5 text-amber-500" />
              <span>Knowledge Gaps</span>
            </button>
            <button onClick={() => {
              fgRef.current?.zoomToFit(400);
              toast('Graph Reset', 'Zoomed to fit node boundaries', 'info');
            }} className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl p-2.5 text-slate-600 dark:text-slate-400 hover:text-emerald-500 transition-colors shadow-lg" title="Zoom to Fit">
               <Maximize className="w-4 h-4" />
            </button>
            <button onClick={() => {
               fgRef.current?.cameraPosition({ x: 0, y: 0, z: 200 }, { x: 0, y: 0, z: 0 }, 1000);
               toast('Camera Reset', 'Camera centered at origin', 'info');
            }} className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl p-2.5 text-slate-600 dark:text-slate-400 hover:text-emerald-500 transition-colors shadow-lg" title="Reset Camera">
               <RotateCcw className="w-4 h-4" />
            </button>
            <button onClick={handleExportGraphML} className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl px-3.5 py-2 text-slate-700 dark:text-slate-200 hover:text-emerald-500 transition-colors text-xs font-medium flex items-center gap-1.5 shadow-lg" title="Export GraphML XML">
               <Download className="w-3.5 h-3.5 text-emerald-500" />
               <span>GraphML</span>
            </button>
        </div>
      </div>

      {/* 3D Force Canvas */}
      <div className="flex-1 bg-transparent overflow-hidden cursor-move">
         <ForceGraph3D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            nodeId="id"
            nodeLabel="name"
            nodeThreeObject={nodeThreeObject}
            nodeRelSize={6}
            linkColor={linkColor}
            linkWidth={1.5}
            onNodeClick={handleNodeClick}
            backgroundColor="rgba(0,0,0,0)"
            showNavInfo={false}
         />
      </div>

      {/* Bottom Counter Bar */}
      <div className="absolute bottom-4 left-4 flex gap-3 text-xs text-slate-400 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl px-3.5 py-2 pointer-events-none z-20 shadow-lg font-mono">
        <span>{filteredNodes.length} nodes</span>
        <span>•</span>
        <span>{filteredEdges.length} semantic edges</span>
        <span>•</span>
        <span className="text-emerald-500 font-semibold">WebGL 3D</span>
      </div>

      {/* Selected Node Panel */}
      {selectedNode && (
        <div className="absolute bottom-4 right-4 w-80 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-2xl z-20 pointer-events-auto font-sans">
          <div className="flex justify-between items-start mb-3">
            <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate max-w-[220px] font-serif-claude">
              {selectedNode.name || selectedNode.label}
            </h4>
            <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs">✕</button>
          </div>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-500">Category:</span>
              <span className={`font-semibold uppercase tracking-wider ${
                selectedNode.type === 'document' ? 'text-emerald-500' : selectedNode.type === 'tag' ? 'text-rose-500' : 'text-amber-500'
              }`}>{selectedNode.type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Node ID:</span>
              <span className="text-slate-400 truncate max-w-[140px]">{selectedNode.id}</span>
            </div>
            {selectedNode.filepath && (
              <div className="flex justify-between">
                <span className="text-slate-500">File:</span>
                <span className="text-slate-400 truncate ml-2 max-w-[150px]">{selectedNode.filepath}</span>
              </div>
            )}
            <div className="flex justify-between pt-1 border-t border-slate-200 dark:border-white/5">
              <span className="text-slate-500">Linked Nodes:</span>
              <span className="text-emerald-500 font-bold">{
                filteredEdges.filter(e => (e.source?.id || e.source) === selectedNode.id || (e.target?.id || e.target) === selectedNode.id).length
              }</span>
            </div>

            {/* Bi-Directional Cross-View Actions */}
            <div className="pt-3 border-t border-slate-200 dark:border-white/5 flex flex-col gap-1.5 font-sans">
              <button
                onClick={() => {
                  toast('Opening Workstation', `Navigating to ${selectedNode.name || 'document'}...`, 'info');
                  setActiveView('workspace');
                }}
                className="w-full py-1.5 px-2.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
              >
                <span>Open in Workstation</span>
              </button>

              <div className="flex gap-1.5">
                <button
                  onClick={() => {
                    toast('Spawning AI Studio', `Grounded on ${selectedNode.name}...`, 'info');
                    setActiveView('chat');
                  }}
                  className="flex-1 py-1.5 px-2 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-700 dark:text-amber-300 border border-amber-500/30 text-[11px] font-semibold flex items-center justify-center gap-1 transition-all"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Chat Concept</span>
                </button>
                <button
                  onClick={() => {
                    setSearchQuery(selectedNode.name || selectedNode.id);
                    setActiveView('search');
                  }}
                  className="flex-1 py-1.5 px-2 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 text-[11px] font-medium flex items-center justify-center gap-1 transition-all"
                >
                  <span>Search Vault</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
