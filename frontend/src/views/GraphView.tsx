import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { glassCardClasses, debounce } from '../lib/utils';
import { Filter, Maximize, RotateCcw } from 'lucide-react';
import { api } from '../lib/api';

export default function GraphView() {
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

  // ponytail: debounce graph physics recalculation
  const debouncedSetFilter = useCallback(debounce((val: string) => setFilter(val), 150), []);

  useEffect(() => {
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
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;
    
    // ponytail: debounce resize events to prevent webgl thrashing
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
    
    // Initial size setup
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

  // ponytail: cache materials to avoid webgl memory leak
  const materialCache = useRef<Record<string, THREE.SpriteMaterial>>({});

  useEffect(() => {
    return () => {
      Object.values(materialCache.current).forEach(mat => {
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

      let color = '#64748b';
      let icon = '📄';
      
      if (type === 'document') {
        color = '#818CF8';
        icon = '📄';
      } else if (type === 'tag') {
        color = '#34D399';
        icon = '🏷️';
      } else if (type === 'concept') {
        color = '#FBBF24';
        icon = '💡';
      }

      // Draw background circle
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
        ctx.strokeStyle = '#0f172a';
        ctx.stroke();
      }

      // Draw icon
      ctx.font = '64px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(icon, size / 2, size / 2 + 6);

      const texture = new THREE.CanvasTexture(canvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      const material = new THREE.SpriteMaterial({ map: texture, depthTest: false });
      materialCache.current[cacheKey] = material;
    }

    const sprite = new THREE.Sprite(materialCache.current[cacheKey]);
    
    // Set scale relative to node importance or standard size
    const scale = type === 'document' ? 14 : 10;
    sprite.scale.set(scale, scale, 1);
    
    return sprite;
  }, [selectedNode]);

  const linkColor = useCallback((link: any) => {
    const type = link.type || link.relation || link.name;
    if (type === 'tagged_with') return '#818CF880';
    if (type === 'wikilink_to') return '#A78BFA80';
    if (type === 'shared_tag_cluster') return '#FBBF2480';
    if (type === 'mentions') return '#22D3EE80';
    return '#47556980';
  }, []);

  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node);
    
    // Aim at node from outside it
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
      <div className="h-full flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full relative" ref={containerRef}>
      {/* Toolbar */}
      <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          <input
            type="text"
            placeholder="Filter nodes..."
            value={searchInput}
            onChange={(e) => {
              setSearchInput(e.target.value);
              debouncedSetFilter(e.target.value);
            }}
            className="bg-slate-900/80 backdrop-blur-md border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 w-52"
          />
          <div className="flex gap-1 bg-slate-900/80 backdrop-blur-md border border-white/10 rounded-lg p-1">
            {(['document', 'tag', 'concept'] as const).map(cat => (
              <button
                key={cat}
                onClick={() => setCategoryFilters(prev => ({ ...prev, [cat]: !prev[cat] }))}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  categoryFilters[cat]
                    ? cat === 'document' ? 'bg-indigo-500/20 text-indigo-400'
                      : cat === 'tag' ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-amber-500/20 text-amber-400'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 pointer-events-auto">
           <button onClick={() => fgRef.current?.zoomToFit(400)} className="bg-slate-900/80 backdrop-blur-md border border-white/10 rounded-lg p-2 text-slate-400 hover:text-white transition-colors" title="Zoom to Fit">
              <Maximize className="w-4 h-4" />
           </button>
           <button onClick={() => {
              fgRef.current?.cameraPosition({ x: 0, y: 0, z: 200 }, { x: 0, y: 0, z: 0 }, 1000);
           }} className="bg-slate-900/80 backdrop-blur-md border border-white/10 rounded-lg p-2 text-slate-400 hover:text-white transition-colors" title="Reset Camera">
              <RotateCcw className="w-4 h-4" />
           </button>
        </div>
      </div>

      {/* Canvas */}
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

      {/* Stats bar */}
      <div className="absolute bottom-4 left-4 flex gap-3 text-xs text-slate-500 bg-slate-900/80 backdrop-blur-md border border-white/10 rounded-lg px-3 py-2 pointer-events-none z-20">
        <span>{filteredNodes.length} nodes</span>
        <span>•</span>
        <span>{filteredEdges.length} edges</span>
        <span>•</span>
        <span>3D Engine</span>
      </div>

      {/* Selected Node Panel */}
      {selectedNode && (
        <div className="absolute bottom-4 right-4 w-72 bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl z-20 pointer-events-auto">
          <div className="flex justify-between items-start mb-3">
            <h4 className="text-sm font-semibold text-slate-100 truncate max-w-[200px]">{selectedNode.name || selectedNode.label}</h4>
            <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-slate-300 text-xs">✕</button>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between"><span className="text-slate-500">Type</span><span className={`font-medium ${
              selectedNode.type === 'document' ? 'text-indigo-400' : selectedNode.type === 'tag' ? 'text-emerald-400' : 'text-amber-400'
            }`}>{selectedNode.type}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">ID</span><span className="text-slate-300 font-mono">{selectedNode.id}</span></div>
            {selectedNode.filepath && (
              <div className="flex justify-between"><span className="text-slate-500">Path</span><span className="text-slate-300 truncate ml-2">{selectedNode.filepath}</span></div>
            )}
            <div className="flex justify-between"><span className="text-slate-500">Connections</span><span className="text-slate-300">{
              filteredEdges.filter(e => e.source.id === selectedNode.id || e.target.id === selectedNode.id).length
            }</span></div>
          </div>
        </div>
      )}
    </div>
  );
}
