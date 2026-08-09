import React, { useState, useEffect } from 'react';
import { glassCardClasses } from '../lib/utils';
import { DatabaseZap, FileText, UploadCloud, RefreshCw, Layers, CheckCircle2, XCircle, Clock, Workflow } from 'lucide-react';
import { api } from '../lib/api';

export default function IngestionView() {
  const [recentJobs, setRecentJobs] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    api.stats().then(data => {
      setStats(data);
      if (data?.timeline) {
        setRecentJobs(data.timeline.map((item: any, i: number) => ({
          id: `file-${i}`,
          source: item.filename,
          status: 'completed',
          time: new Date(item.modified_at * 1000).toLocaleTimeString(),
          chunks: data.total_chunks ? Math.floor(data.total_chunks / (data.total_files || 1)) : 0,
          vectors: data.total_chunks ? Math.floor(data.total_chunks / (data.total_files || 1)) : 0
        })));
      }
    }).catch(console.error);
  }, []);

  return (
    <div className="p-8 h-full overflow-y-auto space-y-6 max-w-[1600px] mx-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Ingestion & RAG Pipeline</h2>
        <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">Monitor document parsing, chunking, and vector embedding processes.</p>
      </header>

      {/* Pipeline Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard icon={<UploadCloud className="text-blue-600 dark:text-blue-400" />} title="Queue" value="0" sub="Files waiting" />
        <StatCard icon={<FileText className="text-indigo-600 dark:text-indigo-400" />} title="Parsing" value="0" sub="Active extractors" />
        <StatCard icon={<Layers className="text-purple-600 dark:text-purple-400" />} title="Chunking" value="0/s" sub="Tokens processed" />
        <StatCard icon={<DatabaseZap className="text-cyan-600 dark:text-cyan-400" />} title="Embedding" value="0/s" sub="Vectors generated" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Active Pipeline Flow Visualizer */}
        <div className={`${glassCardClasses} p-6 col-span-1 lg:col-span-2 flex flex-col`}>
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2">
              <Workflow className="w-5 h-5 text-indigo-600 dark:text-indigo-400" /> Pipeline Architecture
            </h3>
            <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-medium rounded-lg flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Operational
            </span>
          </div>
          
          <div className="flex-1 bg-slate-50/50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-white/5 p-8 flex items-center justify-between relative">
            {/* Connecting Line */}
            <div className="absolute left-10 right-10 top-1/2 h-0.5 bg-slate-100 dark:bg-slate-800 -z-10" />
            <div className="absolute left-10 right-10 top-1/2 h-0.5 bg-gradient-to-r from-blue-500/50 via-purple-500/50 to-cyan-500/50 -z-10 animate-pulse" />

            {/* Nodes */}
            <PipelineNode icon={<UploadCloud />} title="Ingest" desc="Webhooks & Uploads" color="blue" />
            <PipelineNode icon={<FileText />} title="Parse" desc="OCR & Text Ext" color="indigo" active />
            <PipelineNode icon={<Layers />} title="Chunk" desc="Semantic Splitter" color="purple" />
            <PipelineNode icon={<DatabaseZap />} title="Embed" desc="Vectorization" color="cyan" />
          </div>
        </div>

        {/* Quick Actions & Status */}
        <div className={`${glassCardClasses} p-6 col-span-1 flex flex-col`}>
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200 mb-6">Pipeline Controls</h3>
          
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-4 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/80 dark:bg-slate-800/80 border border-slate-300 dark:border-white/10 rounded-xl transition-colors group">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-lg group-hover:bg-indigo-500/20 transition-colors"><RefreshCw className="w-4 h-4" /></div>
                <div className="text-left">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-200">Force Re-index</p>
                  <p className="text-xs text-slate-500">Rebuild vectors for all files</p>
                </div>
              </div>
            </button>

            <button className="w-full flex items-center justify-between p-4 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/80 dark:bg-slate-800/80 border border-slate-300 dark:border-white/10 rounded-xl transition-colors group">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-500/10 text-red-600 dark:text-red-400 rounded-lg group-hover:bg-red-500/20 transition-colors"><XCircle className="w-4 h-4" /></div>
                <div className="text-left">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-200">Clear Queue</p>
                  <p className="text-xs text-slate-500">Cancel pending items</p>
                </div>
              </div>
            </button>
          </div>

          <div className="mt-auto pt-6 border-t border-slate-200 dark:border-white/5">
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-600 dark:text-slate-400">Embedding Model</span>
              <span className="text-slate-900 dark:text-slate-200 font-medium">text-embedding-3-small</span>
            </div>
            <div className="flex justify-between items-center text-sm mt-2">
              <span className="text-slate-600 dark:text-slate-400">Chunk Size</span>
              <span className="text-slate-900 dark:text-slate-200 font-medium">1024 tokens</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Jobs Table */}
      <div className={`${glassCardClasses} p-6`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-600 dark:text-indigo-400" /> Recent Ingestion Jobs
          </h3>
          <button className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-300">View All Logs</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead>
              <tr className="text-slate-500 border-b border-slate-200 dark:border-white/5">
                <th className="pb-3 font-medium">Job ID</th>
                <th className="pb-3 font-medium">Source Document</th>
                <th className="pb-3 font-medium">Time</th>
                <th className="pb-3 font-medium">Chunks</th>
                <th className="pb-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {recentJobs.map((job) => (
                <tr key={job.id} className="text-slate-700 dark:text-slate-300 hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 font-mono text-xs text-slate-500">{job.id}</td>
                  <td className="py-3 font-medium text-slate-900 dark:text-slate-200">{job.source}</td>
                  <td className="py-3 text-slate-500">{job.time}</td>
                  <td className="py-3">{job.chunks}</td>
                  <td className="py-3 text-right">
                    {job.status === 'completed' && (
                      <span className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20 text-xs font-medium">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Success
                      </span>
                    )}
                    {job.status === 'processing' && (
                      <span className="inline-flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20 text-xs font-medium">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Processing
                      </span>
                    )}
                    {job.status === 'failed' && (
                      <span className="inline-flex items-center gap-1.5 text-red-600 dark:text-red-400 bg-red-500/10 px-2.5 py-1 rounded-lg border border-red-500/20 text-xs font-medium">
                        <XCircle className="w-3.5 h-3.5" /> Failed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, sub, active = false }: { icon: React.ReactNode, title: string, value: string, sub: string, active?: boolean }) {
  return (
    <div className={`${glassCardClasses} p-5 flex items-start space-x-4 border ${active ? 'border-indigo-500/30' : 'border-slate-200 dark:border-white/5'}`}>
      <div className="p-3 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-300 dark:border-white/10 relative">
        {icon}
        {active && <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse border-2 border-slate-900" />}
      </div>
      <div>
        <p className="text-sm text-slate-600 dark:text-slate-400 font-medium">{title}</p>
        <p className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mt-0.5">{value}</p>
        <p className="text-xs text-slate-500 mt-1">{sub}</p>
      </div>
    </div>
  );
}

function PipelineNode({ icon, title, desc, color, active = false }: { icon: React.ReactNode, title: string, desc: string, color: string, active?: boolean }) {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/30',
    indigo: 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/30',
    purple: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30',
    cyan: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/30',
  };

  return (
    <div className={`flex flex-col items-center bg-slate-50 dark:bg-slate-900 p-4 rounded-xl border shadow-xl z-10 w-32 ${active ? colorMap[color] : 'border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-400'}`}>
      <div className={`mb-3 ${active ? 'animate-bounce' : ''}`}>
        {icon}
      </div>
      <p className={`font-semibold text-sm ${active ? 'text-slate-900 dark:text-white' : 'text-slate-700 dark:text-slate-300'}`}>{title}</p>
      <p className="text-[10px] text-center mt-1 opacity-70 leading-tight">{desc}</p>
    </div>
  );
}
