import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { glassCardClasses } from '../lib/utils';
import { Activity, HardDrive, FileText, Zap, Clock, CheckCircle2, XCircle, Search } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';

export default function DashboardView() {
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
      if (!data) return setStorage({ totalDocuments: 0, distribution: [] });
      const distribution = Object.entries(data.by_mime || {})
        .map(([mime, count]) => ({ mime: mime || 'unknown', count: count as number }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);
      
      const totalDocuments = Object.values(data.by_mime || {}).reduce((acc: number, val: any) => acc + (val as number), 0);
      setStorage({ totalDocuments, distribution });
    }).catch(() => setStorage({ totalDocuments: 0, distribution: [] }));

    api.searchActivity().then(data => {
      if (!data) return setActivity({ timeline: [] });
      setActivity(data);
    }).catch(() => setActivity({ timeline: [] }));

    api.recentSearches().then(data => {
      setRecent(Array.isArray(data) ? data : []);
    }).catch(() => setRecent([]));

    api.workflowTriggers().then(data => setTriggers(Array.isArray(data) ? data : [])).catch(() => setTriggers([]));
  }, []);

  const pieColors = ['#818CF8', '#22D3EE', '#34D399', '#FBBF24'];

  return (
    <div className="p-8 space-y-6 max-w-[1600px] mx-auto h-full overflow-y-auto">
      <header className="mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">System Analytics</h2>
          <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">Platform overview and active operations.</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Uroboros Engine v2.4.1</p>
          <p className="text-xs text-emerald-600 dark:text-emerald-400 flex items-center justify-end gap-1 mt-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse" /> All Systems Nominal
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={<Activity className="text-indigo-600 dark:text-indigo-400" />} title="System Status" value={stats?.status || 'Loading...'} sub="Uptime: 99.9%" />
        <StatCard icon={<HardDrive className="text-cyan-600 dark:text-cyan-400" />} title="Files Indexed" value={storage ? `${storage.totalDocuments.toLocaleString()}` : '...'} sub="Across Vault Directories" />
        <StatCard icon={<FileText className="text-emerald-600 dark:text-emerald-400" />} title="Tags Processed" value={systemStats?.total_tags?.toLocaleString() ?? '...'} sub="Semantic cluster mapped" />
        <StatCard icon={<Zap className="text-amber-600 dark:text-amber-400" />} title="Active Triggers" value={triggers.length.toString()} sub="Workflow automations" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={`${glassCardClasses} p-6 col-span-1 lg:col-span-2 flex flex-col`}>
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200">Search Telemetry & Indexing</h3>
            <select aria-label="Telemetry Date Range" className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-lg text-sm text-slate-700 dark:text-slate-300 px-3 py-1 outline-none">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="flex-1 min-h-[300px]">
            {activity ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={activity.timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSearches" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#818CF8" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#818CF8" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorIndexed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22D3EE" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#22D3EE" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="date" stroke="#64748b" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} />
                  <YAxis stroke="#64748b" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                  <Area type="monotone" dataKey="searches" stroke="#818CF8" strokeWidth={2} fillOpacity={1} fill="url(#colorSearches)" name="Queries" />
                  <Area type="monotone" dataKey="indexed" stroke="#22D3EE" strokeWidth={2} fillOpacity={1} fill="url(#colorIndexed)" name="Files Indexed" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
        </div>
        
        <div className={`${glassCardClasses} p-6 col-span-1 flex flex-col`}>
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200 mb-6">Storage Analytics</h3>
          <div className="flex-1 min-h-[220px] mb-4">
            {storage ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={storage.distribution} dataKey="count" nameKey="mime" cx="50%" cy="50%" innerRadius={70} outerRadius={90} paddingAngle={5} stroke="none">
                    {storage.distribution.map((_: any, i: number) => (
                      <Cell key={`cell-${i}`} fill={pieColors[i % pieColors.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    formatter={(value: number) => `${value.toLocaleString()} files`}
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
          {storage && (
            <div className="space-y-3">
              {storage.distribution.map((item: any, i: number) => (
                <div key={item.mime} className="flex justify-between items-center text-sm">
                  <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: pieColors[i % pieColors.length] }} />
                    {item.mime.split('/')[1]?.toUpperCase() || item.mime}
                  </div>
                  <span className="text-slate-600 dark:text-slate-400">{item.count.toLocaleString()} files</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className={`${glassCardClasses} p-6`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" /> Active Workflow Triggers
          </h3>
          <button className="text-sm bg-amber-500/20 text-amber-600 dark:text-amber-400 px-3 py-1.5 rounded-lg hover:bg-amber-500/30 transition-colors">New Rule</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead>
              <tr className="text-slate-500 border-b border-slate-200 dark:border-white/5">
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Event Type</th>
                <th className="pb-3 font-medium">Target Webhook</th>
                <th className="pb-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {triggers.map((t: any) => (
                <tr key={t.id} className="text-slate-700 dark:text-slate-300 hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 font-medium">{t.name}</td>
                  <td className="py-3"><span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded border border-slate-200 dark:border-white/5 text-xs">{t.event_type}</span></td>
                  <td className="py-3 text-slate-500 font-mono text-xs">{t.webhook_url}</td>
                  <td className="py-3 text-right">
                    {t.is_active ? <span className="text-emerald-500">Active</span> : <span className="text-slate-500">Disabled</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {triggers.length === 0 && <div className="py-6 text-center text-slate-500">No workflow triggers defined.</div>}
        </div>
      </div>

      <div className={`${glassCardClasses} p-6`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-500 dark:text-indigo-400" /> Recent Execution History
          </h3>
          <button className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300">View All</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead>
              <tr className="text-slate-500 border-b border-slate-200 dark:border-white/5">
                <th className="pb-3 font-medium">Query String</th>
                <th className="pb-3 font-medium">Search Mode</th>
                <th className="pb-3 font-medium">Time</th>
                <th className="pb-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {recent.map((req: any) => (
                <tr key={req.id} className="text-slate-700 dark:text-slate-300 hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 flex items-center gap-2">
                    <Search className="w-4 h-4 text-slate-500" />
                    "{req.query}"
                  </td>
                  <td className="py-3">
                    <span className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-white/5 text-xs font-medium text-slate-700 dark:text-slate-300">
                      {req.mode}
                    </span>
                  </td>
                  <td className="py-3 text-slate-500">{req.time}</td>
                  <td className="py-3 text-right">
                    {req.status === 'success' ? (
                      <span className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                        <CheckCircle2 className="w-4 h-4" /> Success
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-red-600 dark:text-red-400">
                        <XCircle className="w-4 h-4" /> Failed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {recent.length === 0 && (
            <div className="py-8 text-center text-slate-500">No recent searches found.</div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, sub }: { icon: React.ReactNode, title: string, value: string, sub: string }) {
  return (
    <div className={`${glassCardClasses} p-5 flex items-start space-x-4 hover:border-indigo-400 dark:hover:border-indigo-500/30 transition-colors group`}>
      <div className="p-3 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/10 group-hover:bg-slate-200 dark:group-hover:bg-white/10 transition-colors">
        {icon}
      </div>
      <div>
        <p className="text-sm text-slate-600 dark:text-slate-400 font-medium">{title}</p>
        <p className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mt-0.5">{value}</p>
        <p className="text-xs text-slate-500 mt-1">{sub}</p>
      </div>
    </div>
  );
}
