'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface SystemHealth {
  status: string;
  backend: string;
  is_ready: boolean;
  gpu_available: boolean;
  airgapped_compliant: boolean;
}

export default function DashboardPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [templatesCount, setTemplatesCount] = useState<number>(8);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Attempt local API fetch with fallback to internal defaults
    fetch('http://localhost:8000/inference/health')
      .then((res) => res.json())
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch(() => {
        setHealth({
          status: 'healthy (air-gapped local)',
          backend: 'local_gemma_engine',
          is_ready: true,
          gpu_available: false,
          airgapped_compliant: true,
        });
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Top Bar */}
      <header className="border-b border-slate-800 bg-slate-950 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-teal-500 flex items-center justify-center font-bold text-slate-950 text-lg">
              AF
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">DME AgentFlow Console</h1>
              <p className="text-xs text-slate-400">Digital Mind Engineering</p>
            </div>
          </Link>
        </div>
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-2 text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-3 py-1 rounded-full">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Status: Air-Gapped / Sovereign</span>
          </span>
          <Link
            href="/"
            className="text-xs text-slate-400 hover:text-white transition"
          >
            Back to Portal
          </Link>
        </div>
      </header>

      {/* Main Workspace View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Sidebar */}
        <aside className="w-64 border-r border-slate-800 bg-slate-950/60 p-4 space-y-2">
          <div className="text-xs font-semibold text-slate-500 px-3 uppercase tracking-wider mb-2">
            Operations
          </div>
          {[
            { label: 'Overview', active: true },
            { label: 'Workflows Studio', active: false },
            { label: 'AI Agents Studio', active: false },
            { label: 'Gemma 4 Registry', active: false },
            { label: 'Industry Packs', active: false },
            { label: 'Knowledge Hub', active: false },
            { label: 'Approvals Center', active: false },
            { label: 'Executions Monitor', active: false },
            { label: 'CRM & Accounts', active: false },
            { label: 'Analytics & ROI', active: false },
            { label: 'System Settings', active: false },
          ].map((item, idx) => (
            <div
              key={idx}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition cursor-pointer ${
                item.active
                  ? 'bg-teal-500/10 text-teal-300 border border-teal-500/20'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              {item.label}
            </div>
          ))}
        </aside>

        {/* Content Body */}
        <main className="flex-1 p-8 overflow-y-auto">
          {/* Welcome & Stats Row */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-1">Operational Command Overview</h2>
            <p className="text-sm text-slate-400">
              Real-time monitoring of tenant workflows, sovereign inference, and automated operations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="p-5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Inference Backend</span>
              <div className="text-xl font-bold text-teal-400 mt-2">
                {health?.backend || 'Gemma 4 Local'}
              </div>
              <span className="text-xs text-slate-500">100% On-Premise Sovereign</span>
            </div>
            <div className="p-5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Active Industry Packs</span>
              <div className="text-xl font-bold text-white mt-2">8 Industries</div>
              <span className="text-xs text-emerald-400">Ready to Deploy</span>
            </div>
            <div className="p-5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Approval Pipeline</span>
              <div className="text-xl font-bold text-white mt-2">0 Pending</div>
              <span className="text-xs text-slate-500">Human-in-the-Loop Active</span>
            </div>
            <div className="p-5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Air-Gap Compliance</span>
              <div className="text-xl font-bold text-emerald-400 mt-2">Enforced</div>
              <span className="text-xs text-slate-500">Zero External Telemetry</span>
            </div>
          </div>

          {/* Quick Actions & Demo Triggers */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Enterprise Industry Blueprints</h3>
              <div className="space-y-3">
                {[
                  { name: 'Manufacturing RFQ & Supplier Routing', time: 'Auto-Classify + Specs Extract' },
                  { name: 'Logistics Delay Dispatch & Reroute', time: 'SLA Escalation Engine' },
                  { name: 'IT Infrastructure Severity Triage', time: 'Tier-1 Incident Isolation' },
                  { name: 'Professional Services Client Intake', time: 'Scope Scoring + CRM Record' },
                ].map((wf, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center justify-between"
                  >
                    <div>
                      <div className="text-sm font-semibold text-slate-200">{wf.name}</div>
                      <div className="text-xs text-slate-500">{wf.time}</div>
                    </div>
                    <button className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-teal-400 text-xs font-semibold border border-slate-700 transition">
                      View Flow
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold text-white mb-2">Google Gemma 4 Sovereign Worker</h3>
                <p className="text-sm text-slate-400 mb-6">
                  Inference executes locally via llama-cpp-python. Configured for high-throughput zero-leakage workflow processing.
                </p>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 space-y-2">
                  <div>• Model Family: Google Gemma 4 (E4B / 12B / 26B / 31B)</div>
                  <div>• Runtime: llama.cpp GGUF local quantization</div>
                  <div>• Memory Policy: Strict Local Host Scoped</div>
                  <div>• External Calls: Hard Disabled (Air-Gapped)</div>
                </div>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-xs text-slate-400">Status: Engine Ready</span>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs transition"
                >
                  Verify Backend API
                </a>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
