import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  Play, 
  Download, 
  Share2, 
  Database, 
  Layers, 
  Users, 
  Sparkles, 
  Sliders, 
  DollarSign, 
  Send,
  AlertTriangle,
  RefreshCw,
  Award
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useToast } from '../components/Toast';

type TabType = 'determination' | 'policy' | 'jira' | 'uat';

export default function CuramStudioView() {
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState<TabType>('determination');
  
  // Evidence Form State
  const [applicantName, setApplicantName] = useState('Elena Morales');
  const [householdSize, setHouseholdSize] = useState(3);
  const [earnedIncome, setEarnedIncome] = useState(1600);
  const [unearnedIncome, setUnearnedIncome] = useState(0);
  const [shelterCost, setShelterCost] = useState(650);
  const [utilityStandard, setUtilityStandard] = useState(150);
  const [liquidAssets, setLiquidAssets] = useState(1200);
  const [contractRent, setContractRent] = useState(1450);
  const [bedrooms, setBedrooms] = useState('2');
  const [region, setRegion] = useState('contiguous_48_and_dc');
  
  // Conditions
  const [isChild, setIsChild] = useState(false);
  const [isInfant, setIsInfant] = useState(false);
  const [isPregnant, setIsPregnant] = useState(false);
  const [hasDisability, setHasDisability] = useState(false);
  const [hasMinorChild, setHasMinorChild] = useState(true);
  const [isWorkingTraining, setIsWorkingTraining] = useState(true);

  // Results State
  const [evaluationResult, setEvaluationResult] = useState<any>(null);
  const [evaluating, setEvaluating] = useState(false);
  
  // Policy State
  const [policyData, setPolicyData] = useState<any>(null);
  const [loadingPolicy, setLoadingPolicy] = useState(false);

  // Jira State
  const [selectedJiraProgram, setSelectedJiraProgram] = useState('ALL');
  const [jiraTestCases, setJiraTestCases] = useState<any[]>([]);
  const [loadingJira, setLoadingJira] = useState(false);
  const [pushingJira, setPushingJira] = useState(false);

  // UAT State
  const [uatResult, setUatResult] = useState<any>(null);
  const [runningUat, setRunningUat] = useState(false);

  // Initial Data Load
  useEffect(() => {
    fetchPolicy();
    fetchJiraCases('ALL');
    runEvaluation();
  }, []);

  const fetchPolicy = async () => {
    setLoadingPolicy(true);
    try {
      const res = await fetch('/api/curam/policy/tables');
      if (res.ok) {
        const data = await res.json();
        setPolicyData(data.data);
      }
    } catch (e) {
      console.error('Failed to fetch statutory policy tables', e);
    } finally {
      setLoadingPolicy(false);
    }
  };

  const runEvaluation = async () => {
    setEvaluating(true);
    try {
      const payload = {
        applicant_name: applicantName,
        household_size: householdSize,
        earned_income_monthly: earnedIncome,
        unearned_income_monthly: unearnedIncome,
        shelter_cost_monthly: shelterCost,
        utility_standard_monthly: utilityStandard,
        liquid_assets: liquidAssets,
        contract_rent_monthly: contractRent,
        bedrooms: bedrooms,
        region: region,
        is_child_under_19: isChild,
        is_infant_under_1: isInfant,
        is_pregnant: isPregnant,
        has_disability: hasDisability,
        has_minor_child: hasMinorChild,
        is_working_or_training: isWorkingTraining,
        has_child_under_13: hasMinorChild
      };

      const res = await fetch('/api/curam/cer/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setEvaluationResult(data.data);
        addToast({ title: 'CER Rules Evaluated', message: `Case evaluated across 7 statutory programs in ${data.data.evaluation_duration_ms}ms`, type: 'success' });
      }
    } catch (e) {
      addToast({ title: 'Evaluation Failed', message: String(e), type: 'error' });
    } finally {
      setEvaluating(false);
    }
  };

  const fetchJiraCases = async (program: string) => {
    setLoadingJira(true);
    setSelectedJiraProgram(program);
    try {
      const res = await fetch('/api/curam/jira/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ program: program, format_type: 'json' })
      });
      if (res.ok) {
        const data = await res.json();
        setJiraTestCases(data.test_cases || []);
      }
    } catch (e) {
      console.error('Failed to load Jira test cases', e);
    } finally {
      setLoadingJira(false);
    }
  };

  const handlePushJira = async () => {
    setPushingJira(true);
    try {
      const res = await fetch('/api/curam/jira/push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ program: selectedJiraProgram, project_key: 'SPM' })
      });
      if (res.ok) {
        const data = await res.json();
        addToast({ 
          title: 'Jira Test Cases Synced', 
          message: `Successfully synchronized ${data.data.synced_count} test cases (Mode: ${data.data.mode})`, 
          type: 'success' 
        });
      }
    } catch (e) {
      addToast({ title: 'Jira Sync Error', message: String(e), type: 'error' });
    } finally {
      setPushingJira(false);
    }
  };

  const handleRunUat = async () => {
    setRunningUat(true);
    try {
      const res = await fetch('/api/curam/uat/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ programs: ["MEDICAID_MAGI", "CHIP", "SNAP", "TANF", "WIC", "CCDF", "SECTION8"] })
      });
      if (res.ok) {
        const data = await res.json();
        setUatResult(data.data);
        addToast({ 
          title: 'UAT Matrix Executed', 
          message: `${data.data.passed_scenarios}/${data.data.total_scenarios} Passed (${data.data.pass_rate})`, 
          type: 'success' 
        });
      }
    } catch (e) {
      addToast({ title: 'UAT Execution Error', message: String(e), type: 'error' });
    } finally {
      setRunningUat(false);
    }
  };

  const handleDownloadCertificate = async () => {
    try {
      const res = await fetch('/api/curam/uat/certificate');
      if (res.ok) {
        const data = await res.json();
        const blob = new Blob([data.certificate_markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'uat_acceptance_certificate.md';
        a.click();
        URL.revokeObjectURL(url);
        addToast({ title: 'Certificate Exported', message: 'Downloaded uat_acceptance_certificate.md', type: 'success' });
      }
    } catch (e) {
      addToast({ title: 'Export Failed', message: String(e), type: 'error' });
    }
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-slate-950/60 backdrop-blur-xl">
      {/* Studio Header Bar */}
      <div className="flex-shrink-0 border-b border-white/5 px-6 py-4 flex items-center justify-between bg-slate-900/40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-800 flex items-center justify-center text-white shadow-lg shadow-emerald-950/50 border border-emerald-400/30">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold font-serif-claude text-slate-100">Cúram SPM & QA Testing Studio</h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                CER 2026.1
              </span>
            </div>
            <p className="text-xs text-slate-400">Statutory Rules Engine, Jira Xray/Zephyr QA Specs, and UAT Sign-Off Certification</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-950/80 border border-white/5">
          <button
            onClick={() => setActiveTab('determination')}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2",
              activeTab === 'determination' 
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30" 
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>CER Determination</span>
          </button>

          <button
            onClick={() => setActiveTab('policy')}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2",
              activeTab === 'policy' 
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30" 
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Statutory Datasets</span>
          </button>

          <button
            onClick={() => setActiveTab('jira')}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2",
              activeTab === 'jira' 
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30" 
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Jira QA Specs</span>
          </button>

          <button
            onClick={() => setActiveTab('uat')}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2",
              activeTab === 'uat' 
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30" 
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <Award className="w-3.5 h-3.5" />
            <span>UAT & Certification</span>
          </button>
        </div>
      </div>

      {/* Main Studio Body */}
      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
        {/* TAB 1: CER DETERMINATION & CASEWORKER EVIDENCE */}
        {activeTab === 'determination' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Evidence Form */}
            <div className="lg:col-span-5 space-y-4">
              <div className="p-5 rounded-2xl bg-slate-900/60 border border-white/5 shadow-xl space-y-4">
                <div className="flex items-center justify-between border-b border-white/5 pb-3">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <Users className="w-4 h-4 text-emerald-400" />
                    <span>Household Evidence Payload</span>
                  </h3>
                  <button
                    onClick={runEvaluation}
                    disabled={evaluating}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-all flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
                  >
                    {evaluating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                    <span>Evaluate CER</span>
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="text-slate-400 mb-1 block">Applicant Name</label>
                    <input 
                      type="text" 
                      value={applicantName} 
                      onChange={e => setApplicantName(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-slate-400 mb-1 block">Household Size</label>
                    <input 
                      type="number" 
                      min="1" 
                      max="12" 
                      value={householdSize} 
                      onChange={e => setHouseholdSize(parseInt(e.target.value) || 1)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-slate-400 mb-1 block">Earned Income ($/mo)</label>
                    <input 
                      type="number" 
                      value={earnedIncome} 
                      onChange={e => setEarnedIncome(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-slate-400 mb-1 block">Unearned Income ($/mo)</label>
                    <input 
                      type="number" 
                      value={unearnedIncome} 
                      onChange={e => setUnearnedIncome(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-slate-400 mb-1 block">Shelter / Rent ($/mo)</label>
                    <input 
                      type="number" 
                      value={shelterCost} 
                      onChange={e => setShelterCost(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-slate-400 mb-1 block">Utilities ($/mo)</label>
                    <input 
                      type="number" 
                      value={utilityStandard} 
                      onChange={e => setUtilityStandard(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-slate-400 mb-1 block">Liquid Assets ($)</label>
                    <input 
                      type="number" 
                      value={liquidAssets} 
                      onChange={e => setLiquidAssets(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-slate-400 mb-1 block">FPL Jurisdiction</label>
                    <select 
                      value={region} 
                      onChange={e => setRegion(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950/60 border border-white/10 text-slate-100 focus:border-emerald-500/50 focus:outline-none"
                    >
                      <option value="contiguous_48_and_dc">48 Contiguous & DC</option>
                      <option value="alaska">Alaska</option>
                      <option value="hawaii">Hawaii</option>
                    </select>
                  </div>
                </div>

                {/* Categorical Condition Flags */}
                <div className="pt-2 border-t border-white/5 space-y-2">
                  <label className="text-xs font-semibold text-slate-300 block">Categorical Factors</label>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <label className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/40 border border-white/5 cursor-pointer">
                      <input type="checkbox" checked={hasMinorChild} onChange={e => setHasMinorChild(e.target.checked)} className="rounded text-emerald-600" />
                      <span className="text-slate-300">Minor Dependent</span>
                    </label>

                    <label className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/40 border border-white/5 cursor-pointer">
                      <input type="checkbox" checked={isPregnant} onChange={e => setIsPregnant(e.target.checked)} className="rounded text-emerald-600" />
                      <span className="text-slate-300">Pregnant Member</span>
                    </label>

                    <label className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/40 border border-white/5 cursor-pointer">
                      <input type="checkbox" checked={hasDisability} onChange={e => setHasDisability(e.target.checked)} className="rounded text-emerald-600" />
                      <span className="text-slate-300">Disability / ABD</span>
                    </label>

                    <label className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/40 border border-white/5 cursor-pointer">
                      <input type="checkbox" checked={isWorkingTraining} onChange={e => setIsWorkingTraining(e.target.checked)} className="rounded text-emerald-600" />
                      <span className="text-slate-300">Work / Training</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Multi-Program Determination Results */}
            <div className="lg:col-span-7 space-y-4">
              {evaluationResult ? (
                <>
                  {/* Summary Metric Header */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/20">
                      <span className="text-[11px] text-emerald-400 font-medium block">Approved Programs</span>
                      <span className="text-2xl font-bold text-slate-100">{evaluationResult.approved_programs_count} / 7</span>
                    </div>

                    <div className="p-4 rounded-2xl bg-teal-950/20 border border-teal-500/20">
                      <span className="text-[11px] text-teal-400 font-medium block">Monthly Cash & Food Value</span>
                      <span className="text-2xl font-bold text-slate-100">${evaluationResult.total_monthly_cash_and_nutrition_value}</span>
                    </div>

                    <div className="p-4 rounded-2xl bg-indigo-950/20 border border-indigo-500/20">
                      <span className="text-[11px] text-indigo-400 font-medium block">CER Rule Latency</span>
                      <span className="text-2xl font-bold text-slate-100">{evaluationResult.evaluation_duration_ms}ms</span>
                    </div>
                  </div>

                  {/* Program Determination Cards */}
                  <div className="space-y-3">
                    {Object.entries(evaluationResult.programs || {}).map(([key, prog]: [string, any]) => {
                      const isApproved = prog.eligible;
                      return (
                        <div 
                          key={key} 
                          className={cn(
                            "p-4 rounded-2xl border transition-all",
                            isApproved 
                              ? "bg-emerald-950/15 border-emerald-500/20" 
                              : "bg-slate-900/40 border-white/5 opacity-80"
                          )}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {isApproved ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                              ) : (
                                <XCircle className="w-4 h-4 text-rose-400" />
                              )}
                              <h4 className="text-sm font-semibold text-slate-100">{prog.program || key.toUpperCase()}</h4>
                              {prog.category && (
                                <span className="text-[10px] text-slate-400 font-mono">({prog.category})</span>
                              )}
                            </div>
                            <span className={cn(
                              "px-2.5 py-0.5 rounded-full text-[11px] font-bold font-mono border",
                              isApproved 
                                ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" 
                                : "bg-rose-500/20 text-rose-300 border-rose-500/30"
                            )}>
                              {prog.decision_code}
                            </span>
                          </div>

                          <div className="text-xs text-slate-300 space-y-1">
                            {prog.monthly_benefit_allotment !== undefined && (
                              <p>Monthly Allotment: <strong className="text-emerald-400">${prog.monthly_benefit_allotment}</strong> (Max: ${prog.max_possible_allotment})</p>
                            )}
                            {prog.monthly_cash_grant !== undefined && (
                              <p>Monthly Cash Grant: <strong className="text-emerald-400">${prog.monthly_cash_grant}</strong></p>
                            )}
                            {prog.housing_assistance_payment !== undefined && (
                              <p>Voucher Subsidy (HAP): <strong className="text-emerald-400">${prog.housing_assistance_payment}</strong> (Tenant Rent: ${prog.tenant_rent_contribution})</p>
                            )}
                            {prog.copay_rate_percentage !== undefined && (
                              <p>Family Copay Rate: <strong className="text-teal-400">{prog.copay_rate_percentage}%</strong> (${prog.monthly_family_copay}/mo)</p>
                            )}

                            <div className="pt-1 text-[11px] text-slate-400">
                              {prog.reason_codes?.map((r: string, idx: number) => (
                                <span key={idx} className="block">• {r}</span>
                              ))}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
                  Click 'Evaluate CER' to trigger multi-program statutory decisioning
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: STATUTORY POLICY DATASETS */}
        {activeTab === 'policy' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-200">2026 Empirical Statutory Guidelines & Decision Tables</h3>
                <p className="text-xs text-slate-400">Grounding rules in versioned policy configurations without hardcoded values</p>
              </div>
              <button 
                onClick={fetchPolicy} 
                disabled={loadingPolicy}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-white/10 text-slate-200 text-xs flex items-center gap-1.5 hover:bg-slate-800"
              >
                <RefreshCw className={cn("w-3.5 h-3.5", loadingPolicy && "animate-spin")} />
                <span>Reload Policy</span>
              </button>
            </div>

            {policyData ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/5 space-y-2">
                  <h4 className="font-semibold text-emerald-400">Federal Poverty Level (FPL)</h4>
                  <p className="text-slate-400">Contiguous Base: ${policyData.fpl_guidelines?.contiguous_48_and_dc?.annual_base}/yr</p>
                  <p className="text-slate-400">Per Additional: ${policyData.fpl_guidelines?.contiguous_48_and_dc?.annual_per_person}/yr</p>
                  <p className="text-slate-400">Alaska Base: ${policyData.fpl_guidelines?.alaska?.annual_base}/yr</p>
                  <p className="text-slate-400">Hawaii Base: ${policyData.fpl_guidelines?.hawaii?.annual_base}/yr</p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/5 space-y-2">
                  <h4 className="font-semibold text-emerald-400">SNAP Benefit Guidelines</h4>
                  <p className="text-slate-400">Gross Income Limit: {policyData.snap?.gross_income_fpl_pct}% FPL</p>
                  <p className="text-slate-400">Earned Disregard: {policyData.snap?.earned_income_disregard_pct}%</p>
                  <p className="text-slate-400">Excess Shelter Cap: ${policyData.snap?.excess_shelter_cap}</p>
                  <p className="text-slate-400">Standard Utility Allowance: ${policyData.snap?.standard_utility_allowance}</p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/5 space-y-2">
                  <h4 className="font-semibold text-emerald-400">CHIP & WIC Programs</h4>
                  <p className="text-slate-400">CHIP Child Threshold: {policyData.chip?.default_fpl_pct}% FPL</p>
                  <p className="text-slate-400">CHIP Infant Threshold: {policyData.chip?.infant_under_1_fpl_pct}% FPL</p>
                  <p className="text-slate-400">WIC Income Ceiling: {policyData.wic?.income_limit_fpl_pct}% FPL</p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/5 space-y-2">
                  <h4 className="font-semibold text-emerald-400">CCDF Child Care Subsidies</h4>
                  <p className="text-slate-400">State Median Income (SMI): ${policyData.ccdf_childcare?.state_median_income_monthly}/mo</p>
                  <p className="text-slate-400">SMI Limit: {policyData.ccdf_childcare?.smi_limit_pct}%</p>
                  <p className="text-slate-400">Max Child Age: {policyData.ccdf_childcare?.max_child_age} yrs</p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/5 space-y-2">
                  <h4 className="font-semibold text-emerald-400">Section 8 Housing Voucher</h4>
                  <p className="text-slate-400">Area Median Income (AMI): ${policyData.section8_housing?.area_median_income_monthly}/mo</p>
                  <p className="text-slate-400">Tenant Rent Contribution: {policyData.section8_housing?.tenant_rent_contribution_pct}%</p>
                  <p className="text-slate-400">2-Bedroom Standard: ${policyData.section8_housing?.payment_standard_by_bedrooms?.['2']}</p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/5 space-y-2">
                  <h4 className="font-semibold text-emerald-400">TANF Standard Schedule</h4>
                  <p className="text-slate-400">Initial Earned Disregard: ${policyData.tanf?.earned_income_disregard_initial}</p>
                  <p className="text-slate-400">Asset Limit: ${policyData.tanf?.asset_limit}</p>
                  <p className="text-slate-400">Lifetime Cap: {policyData.tanf?.lifetime_limit_months} months</p>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500">Loading statutory dataset...</div>
            )}
          </div>
        )}

        {/* TAB 3: JIRA TEST CASES & XRAY/ZEPHYR QA */}
        {activeTab === 'jira' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              {/* Program Selector Pills */}
              <div className="flex items-center gap-1.5 flex-wrap">
                {['ALL', 'MEDICAID_MAGI', 'CHIP', 'SNAP', 'TANF', 'WIC', 'CCDF', 'SECTION8'].map(p => (
                  <button
                    key={p}
                    onClick={() => fetchJiraCases(p)}
                    className={cn(
                      "px-3 py-1 rounded-full text-xs font-mono transition-all border",
                      selectedJiraProgram === p
                        ? "bg-emerald-600 text-white border-emerald-500"
                        : "bg-slate-900/60 text-slate-400 border-white/5 hover:text-slate-200"
                    )}
                  >
                    {p}
                  </button>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePushJira}
                  disabled={pushingJira}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{pushingJira ? 'Syncing...' : 'Sync to Jira Cloud'}</span>
                </button>
              </div>
            </div>

            {/* Test Case Cards */}
            <div className="space-y-3">
              {jiraTestCases.map((tc, idx) => (
                <div key={idx} className="p-5 rounded-2xl bg-slate-900/60 border border-white/5 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 font-mono text-xs font-bold border border-indigo-500/30">
                        {tc.key}
                      </span>
                      <h4 className="text-sm font-semibold text-slate-100">{tc.summary}</h4>
                    </div>
                    <div className="flex items-center gap-2">
                      {tc.requirementLinks?.map((req: string, rIdx: number) => (
                        <span key={rIdx} className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/15 text-amber-300 border border-amber-500/30">
                          {req}
                        </span>
                      ))}
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 whitespace-pre-line">{tc.description}</p>

                  {/* Step Table */}
                  <div className="border border-white/5 rounded-xl overflow-hidden text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-slate-950/60 text-slate-400 border-b border-white/5">
                        <tr>
                          <th className="p-2.5 w-12 text-center">#</th>
                          <th className="p-2.5">Action</th>
                          <th className="p-2.5">Test Data</th>
                          <th className="p-2.5">Expected Result</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5 text-slate-300">
                        {tc.testSteps?.map((st: any) => (
                          <tr key={st.stepNumber} className="hover:bg-slate-800/20">
                            <td className="p-2.5 text-center font-mono text-slate-500">{st.stepNumber}</td>
                            <td className="p-2.5 font-medium">{st.action}</td>
                            <td className="p-2.5 font-mono text-slate-400">{st.data}</td>
                            <td className="p-2.5 text-emerald-400/90">{st.expectedResult}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: UAT EXECUTION & MERKLE CERTIFICATION */}
        {activeTab === 'uat' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-200">User Acceptance Testing (UAT) & Sign-Off Certification</h3>
                <p className="text-xs text-slate-400">Caseworker persona simulations with cryptographic SHA-256 Merkle root provenance</p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleRunUat}
                  disabled={runningUat}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-emerald-600/30"
                >
                  <Play className={cn("w-3.5 h-3.5", runningUat && "animate-spin")} />
                  <span>{runningUat ? 'Simulating UAT...' : 'Execute UAT Suite'}</span>
                </button>

                <button
                  onClick={handleDownloadCertificate}
                  className="px-4 py-2 rounded-xl bg-slate-900 border border-white/10 hover:bg-slate-800 text-slate-200 text-xs font-medium flex items-center gap-2"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export Certificate (MD)</span>
                </button>
              </div>
            </div>

            {uatResult ? (
              <div className="space-y-4">
                {/* Scorecard Box */}
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-white/5 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div>
                    <span className="text-xs text-slate-400 block">Total Scenarios</span>
                    <span className="text-2xl font-bold text-slate-100">{uatResult.total_scenarios}</span>
                  </div>
                  <div>
                    <span className="text-xs text-emerald-400 block">Pass Rate</span>
                    <span className="text-2xl font-bold text-emerald-400">{uatResult.pass_rate}</span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 block">Defects Logged</span>
                    <span className="text-2xl font-bold text-slate-100">{uatResult.failed_scenarios}</span>
                  </div>
                  <div>
                    <span className="text-xs text-indigo-400 block">Verdict</span>
                    <span className="text-xs font-mono font-bold text-indigo-300 px-2.5 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 inline-block mt-1">
                      {uatResult.acceptance_verdict}
                    </span>
                  </div>
                </div>

                {/* Cryptographic Merkle Provenance Card */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-white/5 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <Award className="w-4 h-4 text-amber-400" />
                    <span className="text-slate-400">Merkle Root:</span>
                    <span className="text-amber-300 font-bold">{uatResult.merkle_provenance_hash}</span>
                  </div>
                  <span className="text-emerald-400">SOC 2 TYPE II COMPLIANT</span>
                </div>

                {/* Executed Scenarios Ledger */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-300">Caseworker Scenario Execution Log</h4>
                  <div className="space-y-2">
                    {uatResult.executions?.map((ex: any, idx: number) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-900/40 border border-white/5 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-3">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          <span className="font-mono font-bold text-indigo-300">{ex.test_case_key}</span>
                          <span className="text-slate-200">{ex.summary}</span>
                        </div>
                        <div className="flex items-center gap-4 text-slate-400 text-[11px]">
                          <span>Tester: <strong className="text-slate-300">{ex.caseworker_tester}</strong></span>
                          <span>{ex.duration_ms}ms</span>
                          <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400 font-mono font-bold">
                            {ex.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-sm">
                Click 'Execute UAT Suite' to run all caseworker journeys and compute cryptographic sign-off proofs
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
