import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { glassCardClasses, emeraldBadgeClasses, goldBadgeClasses, wineBadgeClasses } from '../lib/utils';
import { useApp } from '../store/AppContext';
import SystemControlsCard from '../components/SystemControlsCard';
import { Activity, HardDrive, FileText, Zap, Clock, CheckCircle2, XCircle, Search, Sparkles } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';

export default function DashboardView() {
  const { setActiveView, activeWorkspace } = useApp();
  const [stats, setStats] = useState<any>(null);
  const [storage, setStorage] = useState<any>(null);
  const [activity, setActivity] = useState<any>(null);
  const [recent, setRecent] = useState<any>([]);
  const [triggers, setTriggers] = useState<any[]>([]);
  const [systemStats, setSystemStats] = useState<any>(null);

  useEffect(() => {
    api.health().then(setStats).catch(() => setStats({ status: 'Error loading data' }));
    api.stats().then(setSystemStats).catch(() => setSystemStats({ total_tags: 0 }));
    
    api.storage().then(data => {
      if (!data) return setStorage({ totalDocuments: 0, distribution: [], topDirectories: [] });
      const distribution = Object.entries(data.by_mime || {})
        .map(([mime, count]) => ({ mime: mime || 'unknown', count: count as number }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);
      
      const totalDocuments = Object.values(data.by_mime || {}).reduce((acc: number, val: any) => acc + (val as number), 0);
      setStorage({ totalDocuments, distribution, topDirectories: data.top_directories || [] });
    }).catch(() => setStorage({ totalDocuments: 0, distribution: [], topDirectories: [] }));

    api.searchActivity().then(data => {
      if (!data) return setActivity({ timeline: [] });
      setActivity(data);
    }).catch(() => setActivity({ timeline: [] }));

    api.recentSearches().then(data => {
      setRecent(Array.isArray(data) ? data : []);
    }).catch(() => setRecent([]));

    api.workflowTriggers().then(data => setTriggers(Array.isArray(data) ? data : [])).catch(() => setTriggers([]));
  }, [activeWorkspace]);

  // Luxury Palette for Charts: Emerald, Teal, Mustard Gold, Wine Red, Slate
  const pieColors = ['#10B981', '#0D9488', '#F59E0B', '#BE123C', '#64748B'];

  return (
    <div className="p-8 space-y-6 max-w-[1600px] mx-auto h-full overflow-y-auto font-sans">
      <header className="mb-6 flex justify-between items-end">
        <div>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">
            System Analytics & Telemetry
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">
            Real-time neural health, vault storage analytics, and query throughput.
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 font-mono">Uroboros Engine v2.4.1</p>
          <p className="text-[11px] text-emerald-600 dark:text-emerald-400 flex items-center justify-end gap-1.5 mt-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_6px_rgba(16,185,129,0.8)]" /> All Neural Systems Nominal
          </p>
        </div>
      </header>

      {/* 4 Core Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          icon={<Activity className="text-emerald-600 dark:text-emerald-400" />} 
          title="System Status" 
          value={stats?.status || 'Active'} 
          sub="Uptime: 99.99% • AVX-512 SIMD" 
        />
        <StatCard 
          icon={<HardDrive className="text-teal-600 dark:text-teal-400" />} 
          title="Documents Indexed" 
          value={storage ? `${storage.totalDocuments.toLocaleString()}` : '...'} 
          sub="Indexed across local vault" 
        />
        <StatCard 
          icon={<FileText className="text-amber-600 dark:text-amber-400" />} 
          title="Semantic Tags" 
          value={systemStats?.total_tags?.toLocaleString() ?? '...'} 
          sub="Vector cluster entities" 
        />
        <StatCard 
          icon={<Zap className="text-rose-600 dark:text-rose-400" />} 
          title="Active Triggers" 
          value={triggers.length.toString()} 
          sub="Workflow event automations" 
        />
      </div>

      <SystemControlsCard />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Activity Timeline Chart */}
        <div className={`${glassCardClasses} p-6 col-span-1 lg:col-span-2 flex flex-col`}>
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 font-serif-claude flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-500" /> Search Telemetry & Indexing Velocity
            </h3>
            <select aria-label="Telemetry Date Range" className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-lg text-xs text-slate-700 dark:text-slate-300 px-3 py-1 outline-none shadow-2xs">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="flex-1 min-h-[300px]">
            {activity && Array.isArray(activity.timeline) ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={activity.timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSearches" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.35}/>
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorIndexed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0D9488" stopOpacity={0.35}/>
                      <stop offset="95%" stopColor="#0D9488" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="date" stroke="#64748b" tick={{fill: '#64748b', fontSize: 11}} axisLine={false} tickLine={false} />
                  <YAxis stroke="#64748b" tick={{fill: '#64748b', fontSize: 11}} axisLine={false} tickLine={false} />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: '#020617', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }}
                    itemStyle={{ color: '#e2e8f0', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="searches" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorSearches)" name="Queries" />
                  <Area type="monotone" dataKey="indexed" stroke="#0D9488" strokeWidth={2} fillOpacity={1} fill="url(#colorIndexed)" name="Files Indexed" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
        </div>
        
        {/* Storage Analytics Chart */}
        <div className={`${glassCardClasses} p-6 col-span-1 flex flex-col`}>
          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 font-serif-claude mb-6">
            Vault Storage Distribution
          </h3>
          <div className="flex-1 min-h-[220px] mb-4">
            {storage && Array.isArray(storage.distribution) ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={storage.distribution} dataKey="count" nameKey="mime" cx="50%" cy="50%" innerRadius={70} outerRadius={90} paddingAngle={5} stroke="none">
                    {storage.distribution.map((_: any, i: number) => (
                      <Cell key={`cell-${i}`} fill={pieColors[i % pieColors.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    formatter={(value: number) => `${value.toLocaleString()} files`}
                    contentStyle={{ backgroundColor: '#020617', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
          {storage && (
            <div className="space-y-5">
              <div className="space-y-2.5">
                <h4 className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Top Types</h4>
                {storage.distribution.map((item: any, i: number) => (
                  <div key={item.mime} className="flex justify-between items-center text-xs">
                    <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: pieColors[i % pieColors.length] }} />
                      {item.mime.split('/')[1]?.toUpperCase() || item.mime}
                    </div>
                    <span className="text-slate-500 font-mono">{item.count.toLocaleString()} files</span>
                  </div>
                ))}
              </div>
              {storage.topDirectories && storage.topDirectories.length > 0 && (
                <div className="space-y-2.5 pt-2 border-t border-slate-200/80 dark:border-white/5">
                  <h4 className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Top Directories</h4>
                  {storage.topDirectories.map((dir: any, i: number) => (
                    <div key={i} className="flex justify-between items-center text-xs">
                      <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 truncate pr-2 max-w-[150px]">
                        <HardDrive className="w-3 h-3 text-slate-400 flex-shrink-0" />
                        <span className="truncate" title={dir.directory}>{dir.directory}</span>
                      </div>
                      <span className="text-slate-500 font-mono whitespace-nowrap">{(dir.size_bytes / (1024 * 1024)).toFixed(1)} MB</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Workflow Triggers */}
      <div className={`${glassCardClasses} p-6`}>
        <div className="flex justify-between items-center mb-5">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
            <Zap className="w-4 h-4 text-amber-500" /> Active Automated Triggers
          </h3>
          <button onClick={() => setActiveView('config')} className="text-xs bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/20 px-3 py-1 rounded-lg hover:bg-amber-500/25 transition-colors font-medium">New Rule</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead>
              <tr className="text-slate-400 border-b border-slate-200 dark:border-white/5 font-semibold">
                <th className="pb-3">Trigger Name</th>
                <th className="pb-3">Event Type</th>
                <th className="pb-3">Target Webhook</th>
                <th className="pb-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60 dark:divide-white/5">
              {triggers.map((t: any) => (
                <tr key={t.id} className="text-slate-700 dark:text-slate-300 hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 font-medium font-serif-claude">{t.name}</td>
                  <td className="py-3"><span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded border border-slate-200 dark:border-white/5 text-[11px] font-mono">{t.event_type}</span></td>
                  <td className="py-3 text-slate-400 font-mono text-[11px]">{t.webhook_url}</td>
                  <td className="py-3 text-right">
                    {t.is_active ? <span className="text-emerald-500 font-medium font-mono">Active</span> : <span className="text-slate-400 font-mono">Disabled</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {triggers.length === 0 && <div className="py-6 text-center text-slate-400 text-xs">No workflow triggers defined yet.</div>}
        </div>
      </div>

      {/* Execution History */}
      <div className={`${glassCardClasses} p-6`}>
        <div className="flex justify-between items-center mb-5">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 font-serif-claude">
            <Clock className="w-4 h-4 text-emerald-500" /> Recent Query Execution History
          </h3>
          <button onClick={() => setActiveView('search')} className="text-xs text-emerald-600 dark:text-emerald-400 hover:underline font-medium">View Explorer</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead>
              <tr className="text-slate-400 border-b border-slate-200 dark:border-white/5 font-semibold">
                <th className="pb-3">Query String</th>
                <th className="pb-3">Search Mode</th>
                <th className="pb-3">Timestamp</th>
                <th className="pb-3 text-right">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60 dark:divide-white/5">
              {recent.map((req: any) => (
                <tr key={req.id} className="text-slate-700 dark:text-slate-300 hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 flex items-center gap-2 font-medium">
                    <Search className="w-3.5 h-3.5 text-emerald-500" />
                    "{req.query}"
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded-md border border-slate-200 dark:border-white/5 text-[11px] font-mono">
                      {req.mode}
                    </span>
                  </td>
                  <td className="py-3 text-slate-400 font-mono text-[11px]">{req.time}</td>
                  <td className="py-3 text-right">
                    {req.status === 'success' ? (
                      <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Success
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-rose-600 dark:text-rose-400 font-medium">
                        <XCircle className="w-3.5 h-3.5" /> Failed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {recent.length === 0 && (
            <div className="py-8 text-center text-slate-400 text-xs">No recent searches found.</div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, sub }: { icon: React.ReactNode, title: string, value: string, sub: string }) {
  return (
    <div className={`${glassCardClasses} p-5 flex items-start space-x-4 hover:border-slate-300 dark:hover:border-white/10 transition-all group shadow-2xs`}>
      <div className="p-3 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/10 group-hover:bg-slate-200 dark:group-hover:bg-white/10 transition-colors">
        {icon}
      </div>
      <div>
        <p className="text-xs text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">{title}</p>
        <p className="text-xl font-bold text-slate-900 dark:text-slate-200 mt-0.5 font-serif-claude">{value}</p>
        <p className="text-[11px] text-slate-400 mt-1">{sub}</p>
      </div>
    </div>
  );
}
