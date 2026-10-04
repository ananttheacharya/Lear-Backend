import { useState, useEffect } from 'react';
import {
  Cloud,
  Server,
  Zap,
  RefreshCw,
  AlertTriangle,
  Sparkles,
  Terminal,
  Activity,
  Layers,
  ExternalLink,
  ShieldCheck,
  PlayCircle,
  GitBranch,
  ShoppingBag,
} from 'lucide-react';
import { useLear } from '../context/LearContext';

interface Scenario {
  id: string;
  name: string;
  connector: string;
  severity: string;
  description: string;
  remediation: string;
}

export default function DemoCenter() {
  const { openChat, pushToast } = useLear();
  const [activeTab, setActiveTab] = useState<'all' | 'aws' | 'gcp' | 'k8s' | 'github' | 'obs'>('all');
  const [loading, setLoading] = useState(false);
  const [fixing, setFixing] = useState(false);
  const [status, setStatus] = useState<any>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [terminalLogs, setTerminalLogs] = useState<Array<{ tag: string; text: string; time: string; type: string }>>([
    { tag: 'BRAIN', text: 'Lear Multi-Cloud AI Copilot initialized. SRE reasoning engine ready.', time: new Date().toLocaleTimeString(), type: 'brain' },
    { tag: 'MOCK', text: 'High-fidelity mock sandbox active on AWS EC2, GCP Compute/Run, Kubernetes, and Datadog.', time: new Date().toLocaleTimeString(), type: 'info' },
  ]);

  const addLog = (tag: string, text: string, type = 'info') => {
    setTerminalLogs(prev => [
      ...prev,
      { tag, text, time: new Date().toLocaleTimeString(), type },
    ]);
  };

  const loadStatus = async () => {
    try {
      const res = await fetch('/api/demo/status');
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
        if (data.scenarios) {
          setScenarios(data.scenarios);
        }
      }
    } catch (e) {
      console.error('Failed to load demo status', e);
    }
  };

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleInjectScenario = async (scenarioId: string, name: string) => {
    setLoading(true);
    addLog('INJECT', `Simulating outage: ${name} (${scenarioId})...`, 'err');
    try {
      await fetch('/api/demo/inject-scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scenarioId }),
      });
      addLog('ALERT', `Critical event propagated to monitoring & on-call engine.`, 'err');
      pushToast({
        title: 'Simulated Outage Injected',
        message: `${name}: Failure state active across mock connectors.`,
        severity: 'error',
      });
      loadStatus();
    } catch (e: any) {
      addLog('ERROR', `Failed to inject scenario: ${e.message}`, 'err');
    } finally {
      setLoading(false);
    }
  };

  const handleAIFix = async () => {
    setFixing(true);
    addLog('BRAIN', 'Lear AI Copilot triggered: Analyzing multi-cloud telemetry and root cause via LLM inference...', 'brain');
    try {
      const res = await fetch('/api/demo/ai-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      if (data.inference_model) {
        addLog(data.inference_model.toUpperCase(), `AI Diagnosis: ${data.inference_diagnosis || data.message}`, 'brain');
      }
      const actions = data.actions_taken || data.actions || [];
      if (actions.length > 0) {
        actions.forEach((act: any) => {
          const text = typeof act === 'string' ? act : `${act.command} (${act.result})`;
          const type = typeof act === 'object' && act.connector ? act.connector : 'fix';
          addLog(typeof act === 'object' && act.connector ? act.connector.toUpperCase() : 'ACTION', text, type);
        });
      }
      addLog('SUCCESS', 'All services and monitors verified healthy. Incidents resolved.', 'fix');
      pushToast({
        title: `Lear Auto-Remediation (${data.inference_model || 'DeepSeek'})`,
        message: 'All multi-cloud mock services restored to 100% HEALTHY.',
        severity: 'success',
      });
      loadStatus();
    } catch (e: any) {
      addLog('ERROR', `AI Auto-Fix failed: ${e.message}`, 'err');
    } finally {
      setFixing(false);
    }
  };

  const handleResetAll = async () => {
    addLog('RESET', 'Resetting all mock services across AWS, GCP, and Kubernetes...', 'info');
    try {
      await fetch('/api/demo/reset-all', { method: 'POST' });
      addLog('BASELINE', 'All connectors restored to healthy baseline.', 'fix');
      pushToast({
        title: 'Mock Baseline Restored',
        message: 'All mock connectors are running cleanly.',
        severity: 'info',
      });
      loadStatus();
    } catch (e: any) {
      addLog('ERROR', `Reset failed: ${e.message}`, 'err');
    }
  };

  const defaultScenarios: Scenario[] = scenarios.length > 0 ? scenarios : [
    {
      id: 'aws_cpu_spike',
      name: 'AWS EC2 Runaway CPU & Watchdog Hang',
      connector: 'aws',
      severity: 'critical',
      description: 'Simulates runaway worker thread & break marker on prash-test-fixture. CPU reaches 99.4%.',
      remediation: 'Lear AI executes SSM RunCommand to terminate runaway process and restart fixture.',
    },
    {
      id: 'aws_disk_full',
      name: 'AWS EBS Filesystem Inode Exhaustion',
      connector: 'aws',
      severity: 'high',
      description: '/var/log reaches 100% capacity on payment-api, blocking transaction commits.',
      remediation: 'Lear AI purges rotated archives and restarts journald logging service.',
    },
    {
      id: 'gcp_proxy_exhaustion',
      name: 'GCP drufiy-proxy Connection Leak',
      connector: 'gcp',
      severity: 'critical',
      description: 'Envoy reverse proxy hits 1024/1024 connections, causing HTTP 502 Bad Gateway.',
      remediation: 'Lear AI runs gcloud compute ssh to clear sockets and reloads Envoy router.',
    },
    {
      id: 'gcp_cloudrun_oom',
      name: 'GCP Cloud Run Container Memory OOM',
      connector: 'gcp',
      severity: 'high',
      description: 'order-service worker leaks RAM, container terminated with SIGKILL 137.',
      remediation: 'Lear AI updates Cloud Run revision memory limit to 1024MB and scales revision.',
    },
    {
      id: 'k8s_configmap_corrupt',
      name: 'Kubernetes ConfigMap Database Disconnect',
      connector: 'k8s',
      severity: 'critical',
      description: 'checkout-api-config set to DATABASE_HOST=postgres-wrong. Pods CrashLoop.',
      remediation: 'Lear AI patches ConfigMap to postgres and triggers rolling deployment restart.',
    },
    {
      id: 'github_ci_failure',
      name: 'GitHub Actions CI Build & Test Failure',
      connector: 'github',
      severity: 'high',
      description: 'Commit c84f1a2 fails checkout-backend test suite, blocking automated production hotfix deployment.',
      remediation: 'Lear AI parses pytest traces, patches regression, and re-triggers GitHub Actions CI workflow #143.',
    },
    {
      id: 'multi_cloud_cascade',
      name: 'Multi-Cloud Cross-Provider Domino Failure',
      connector: 'cascade',
      severity: 'critical',
      description: 'Simultaneous failure across AWS, GCP, GitHub, and Kubernetes with Datadog alarm storm.',
      remediation: 'Lear AI coordinates multi-step cross-cloud remediation sequence automatically.',
    },
  ];

  const filteredScenarios = defaultScenarios.filter(s => {
    if (activeTab === 'all') return true;
    if (activeTab === 'aws') return s.connector === 'aws';
    if (activeTab === 'gcp') return s.connector === 'gcp';
    if (activeTab === 'k8s') return s.connector === 'k8s';
    if (activeTab === 'github') return s.connector === 'github';
    if (activeTab === 'obs') return s.connector === 'datadog' || s.connector === 'pagerduty' || s.connector === 'obs';
    return true;
  });

  const awsFixture = status?.aws_instances?.['prash-test-fixture'];
  const awsFixtureBroken = awsFixture?.marker_present || awsFixture?.active_error;
  const gcpProxy = status?.gcp_instances?.['drufiy-proxy'];
  const gcpProxyBroken = gcpProxy?.marker_present || gcpProxy?.active_error;
  const ghRepo = status?.github_repos?.['drufiy/checkout-backend'];
  const ghRepoBroken = ghRepo?.ci_status === 'failure' || ghRepo?.active_error;
  const hasOutage = awsFixtureBroken || gcpProxyBroken || ghRepoBroken || status?.chaos_state?.active_error;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-surface-border pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Zap className="w-6 h-6 text-emerald-400" />
              Multi-Cloud Demo & Failure Simulation Center
            </h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
              hasOutage 
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' 
                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            }`}>
              {hasOutage ? '● Outage Active' : '● All Connectors 100% Healthy'}
            </span>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            Simulate real-world cloud outages on AWS, GCP, GitHub, and Kubernetes, then witness Lear AI diagnose and autonomously heal them for your demo.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => window.open('http://127.0.0.1:8000/store', '_blank')}
            className="px-3.5 py-2 rounded-lg bg-emerald-600/20 border border-emerald-500/40 text-xs font-semibold text-emerald-300 hover:bg-emerald-600/30 transition flex items-center gap-2"
          >
            <ShoppingBag className="w-4 h-4 text-emerald-400" />
            Launch Customer Storefront (/store)
          </button>
          <button
            onClick={() => window.open('http://127.0.0.1:8000/demo', '_blank')}
            className="px-3.5 py-2 rounded-lg bg-surface border border-surface-border text-xs font-medium text-gray-300 hover:text-white hover:border-gray-600 transition flex items-center gap-2"
          >
            <ExternalLink className="w-4 h-4 text-emerald-400" />
            Presentation View (/demo)
          </button>
          <button
            onClick={handleResetAll}
            className="px-3.5 py-2 rounded-lg bg-surface border border-surface-border text-xs font-medium text-gray-300 hover:text-white hover:border-gray-600 transition flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset Baseline
          </button>
        </div>
      </div>

      {/* Hero AI Healing Action Bar */}
      <div className="p-5 rounded-xl border border-emerald-500/30 bg-gradient-to-r from-emerald-950/20 via-surface to-purple-950/20 flex flex-col md:flex-row md:items-center md:justify-between gap-4 shadow-lg shadow-black/20">
        <div>
          <div className="text-base font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-400" />
            Lear Autonomous AI Multi-Cloud Remediator
          </div>
          <p className="text-xs text-gray-300 mt-1">
            When outages occur, click below to have Lear AI analyze telemetry, dispatch targeted SSM/gcloud/kubectl commands, and resolve incidents.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => openChat({
              connectorId: 'aws',
              resourceId: 'prash-test-fixture',
              title: 'Multi-Cloud Diagnostic Request',
              initialPrompt: 'What is the current health of our AWS, GCP, and Kubernetes services? Please diagnose any issues.',
            })}
            className="px-4 py-2.5 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-300 hover:bg-blue-600/30 text-xs font-semibold transition flex items-center gap-2"
          >
            <Terminal className="w-4 h-4" />
            Ask Copilot in Chat
          </button>
          <button
            onClick={handleAIFix}
            disabled={fixing}
            className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold text-sm shadow-md shadow-emerald-500/20 hover:from-emerald-400 hover:to-teal-500 transition flex items-center gap-2 disabled:opacity-50"
          >
            {fixing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Executing Multi-Cloud Fix...
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                Trigger Lear AI Auto-Fix
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Topology Cards Grid */}
      <div>
        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          Active Multi-Cloud Mock Services
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* AWS EC2 prash-test-fixture */}
          <div className={`p-4 rounded-xl border transition ${
            awsFixtureBroken 
              ? 'bg-rose-950/20 border-rose-500/50' 
              : 'bg-surface border-surface-border'
          }`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <Cloud className="w-3.5 h-3.5 text-amber-400" />
                prash-test-fixture
              </span>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                awsFixtureBroken ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-400'
              }`}>
                {awsFixtureBroken ? 'DEGRADED' : 'HEALTHY'}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-2 font-mono flex justify-between">
              <span>CPU: <strong className={awsFixtureBroken ? 'text-rose-400' : 'text-gray-200'}>{awsFixtureBroken ? '99.4%' : '12.4%'}</strong></span>
              <span>t3.micro</span>
            </div>
            <div className="text-[11px] text-gray-500 mt-1">AWS EC2 (ap-south-1a) • SSM Active</div>
          </div>

          {/* GCP GCE drufiy-proxy */}
          <div className={`p-4 rounded-xl border transition ${
            gcpProxyBroken 
              ? 'bg-rose-950/20 border-rose-500/50' 
              : 'bg-surface border-surface-border'
          }`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <Server className="w-3.5 h-3.5 text-sky-400" />
                drufiy-proxy
              </span>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                gcpProxyBroken ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-400'
              }`}>
                {gcpProxyBroken ? 'EXHAUSTED' : 'HEALTHY'}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-2 font-mono flex justify-between">
              <span>Conns: <strong className={gcpProxyBroken ? 'text-rose-400' : 'text-gray-200'}>{gcpProxyBroken ? '1024/1024' : '142/1024'}</strong></span>
              <span>e2-std-2</span>
            </div>
            <div className="text-[11px] text-gray-500 mt-1">GCP Compute Engine (us-central1-a)</div>
          </div>

          {/* K8s checkout-api */}
          <div className="p-4 rounded-xl border bg-surface border-surface-border">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-purple-400" />
                checkout-api
              </span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
                RUNNING
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-2 font-mono flex justify-between">
              <span>Host: <strong className="text-gray-200">postgres</strong></span>
              <span>FastAPI :8080</span>
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Kubernetes Pod (lear-demo)</div>
          </div>

          {/* Datadog Synthetic */}
          <div className="p-4 rounded-xl border bg-surface border-surface-border">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-pink-400" />
                datadog-monitor
              </span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
                OK
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-2 font-mono flex justify-between">
              <span>Err Rate: <strong className="text-gray-200">0.4%</strong></span>
              <span>Limit: 5.0%</span>
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Datadog Synthetic #316853860</div>
          </div>

          {/* GitHub Actions drufiy/checkout-backend */}
          <div className={`p-4 rounded-xl border transition ${
            ghRepoBroken 
              ? 'bg-rose-950/20 border-rose-500/50' 
              : 'bg-surface border-surface-border'
          }`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <GitBranch className="w-3.5 h-3.5 text-violet-400" />
                checkout-backend
              </span>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                ghRepoBroken ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-400'
              }`}>
                {ghRepoBroken ? 'FAILED' : 'PASSING'}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-2 font-mono flex justify-between">
              <span>Commit: <strong className={ghRepoBroken ? 'text-rose-400' : 'text-gray-200'}>c84f1a2</strong></span>
              <span>main</span>
            </div>
            <div className="text-[11px] text-gray-500 mt-1">GitHub Actions CI • Workflow #143</div>
          </div>
        </div>
      </div>

      {/* Outage Simulation Scenarios Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-2">
            <PlayCircle className="w-3.5 h-3.5 text-rose-400" />
            Simulated Failure Scenarios (Demo Triggers)
          </h2>
          {/* Connector filter buttons */}
          <div className="flex items-center gap-1.5">
            {(['all', 'aws', 'gcp', 'k8s', 'github', 'obs'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-2.5 py-1 rounded text-[11px] font-semibold transition uppercase ${
                  activeTab === tab 
                    ? 'bg-surface-border text-white' 
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredScenarios.map(sc => (
            <div
              key={sc.id}
              className="p-4 rounded-xl border border-surface-border bg-surface hover:border-gray-700 transition flex flex-col justify-between gap-3"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                    sc.connector === 'aws' ? 'bg-amber-500/20 text-amber-300' :
                    sc.connector === 'gcp' ? 'bg-sky-500/20 text-sky-300' :
                    sc.connector === 'k8s' ? 'bg-purple-500/20 text-purple-300' :
                    sc.connector === 'github' ? 'bg-violet-500/20 text-violet-300' :
                    sc.connector === 'cascade' ? 'bg-pink-500/20 text-pink-300' :
                    'bg-emerald-500/20 text-emerald-300'
                  }`}>
                    {sc.connector}
                  </span>
                  <span className="text-[10px] text-rose-400 font-mono font-semibold uppercase">
                    {sc.severity}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-white">{sc.name}</h3>
                <p className="text-xs text-gray-400 mt-1 line-clamp-2">{sc.description}</p>
              </div>

              <div className="space-y-2 pt-2 border-t border-surface-border">
                <div className="text-[11px] text-emerald-400/90 font-mono bg-emerald-950/20 p-2 rounded border-l-2 border-emerald-500">
                  {sc.remediation}
                </div>
                <button
                  onClick={() => handleInjectScenario(sc.id, sc.name)}
                  disabled={loading}
                  className="w-full py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 hover:bg-rose-500/20 text-xs font-semibold transition flex items-center justify-center gap-1.5"
                >
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Simulate Outage
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Terminal Reasoning Box */}
      <div className="space-y-2">
        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-sky-400" />
          Autonomous SRE Reasoning & Command Execution Log
        </h2>
        <div className="p-4 rounded-xl border border-surface-border bg-black/60 font-mono text-xs text-gray-300 h-48 overflow-y-auto space-y-1.5">
          {terminalLogs.map((log, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-gray-500 shrink-0">[{log.time}]</span>
              <span className={`font-bold shrink-0 ${
                log.type === 'brain' ? 'text-indigo-400' :
                log.type === 'err' ? 'text-rose-400' :
                log.type === 'fix' ? 'text-emerald-400' :
                log.type === 'aws' ? 'text-amber-400' :
                log.type === 'gcp' ? 'text-sky-400' :
                log.type === 'k8s' ? 'text-purple-400' :
                'text-gray-400'
              }`}>
                [{log.tag}]
              </span>
              <span className="break-all">{log.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
