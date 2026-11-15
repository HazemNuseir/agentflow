"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { clearToken, getUser, isLoggedIn } from "../../lib/auth";
import { apiClient } from "../../lib/api";

interface HealthData {
  status?: string;
  inference_mode?: string;
  backend?: string;
}

interface AnalyticsData {
  total_workflows?: number;
  total_executions?: number;
  active_agents?: number;
  [key: string]: unknown;
}

interface Workflow {
  id: string;
  name: string;
  is_published: boolean;
  is_active: boolean;
  [key: string]: unknown;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<Record<string, unknown> | null>(null);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");

    // Health check
    try {
      const healthRes = await fetch("/health");
      if (healthRes.ok) {
        const h = await healthRes.json();
        setHealth(h);
      }
    } catch {
      // non-fatal
    }

    // Analytics
    try {
      const aRes = await apiClient.get("/api/v1/analytics/summary");
      if (aRes.ok) {
        const a = await aRes.json();
        setAnalytics(a.recorded_metrics ?? a);
      }
    } catch {
      // non-fatal
    }

    // Workflows
    try {
      const wRes = await apiClient.get("/api/v1/workflows/");
      if (wRes.ok) {
        const w = await wRes.json();
        setWorkflows(Array.isArray(w) ? w : w.items ?? []);
      }
    } catch {
      // non-fatal
    }

    // Pending approvals
    try {
      const aRes = await apiClient.get("/api/v1/approvals/?status=PENDING");
      if (aRes.ok) {
        const data = await aRes.json();
        const items = Array.isArray(data) ? data : data.items ?? [];
        setPendingCount(items.length);
      }
    } catch {
      // non-fatal
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    setUser(getUser());
    fetchData();
  }, [fetchData, router]);

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  const inferenceMode = health?.inference_mode || health?.backend || null;
  const inferenceBadgeColor =
    inferenceMode === "NATIVE"
      ? "bg-green-900/50 border-green-700 text-green-300"
      : inferenceMode === "SIMULATED_DEVELOPMENT"
      ? "bg-yellow-900/50 border-yellow-700 text-yellow-300"
      : inferenceMode
      ? "bg-slate-700 border-slate-600 text-slate-300"
      : "bg-red-900/50 border-red-700 text-red-300";

  const displayName =
    typeof user?.full_name === "string"
      ? user.full_name
      : typeof user?.email === "string"
      ? user.email
      : "User";

  const totalWorkflows =
    analytics?.total_workflows ?? workflows.length;

  return (
    <div className="min-h-screen bg-slate-900 flex">
      {/* Sidebar */}
      <aside className="w-60 bg-slate-950 border-r border-slate-800 flex flex-col flex-shrink-0">
        {/* Logo */}
        <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-teal-500 flex items-center justify-center font-bold text-slate-950 text-base">
            AF
          </div>
          <div>
            <p className="text-white font-bold text-sm leading-tight">DME AgentFlow</p>
            <p className="text-teal-400 text-xs">V2 LAN Edition</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4 px-3 space-y-1">
          <Link
            href="/dashboard"
            className="flex items-center space-x-3 px-3 py-2.5 rounded-lg bg-teal-500/10 text-teal-400 font-medium text-sm"
          >
            <span>📊</span>
            <span>Overview</span>
          </Link>
          <Link
            href="/workflows"
            className="flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium text-sm transition"
          >
            <span>⚡</span>
            <span>Workflows</span>
          </Link>
          <Link
            href="/approvals"
            className="flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium text-sm transition"
          >
            <span>✅</span>
            <span>Approvals Center</span>
            {pendingCount > 0 && (
              <span className="ml-auto bg-teal-500 text-slate-950 text-xs font-bold px-1.5 py-0.5 rounded-full">
                {pendingCount}
              </span>
            )}
          </Link>
          <Link
            href="/workflows"
            className="flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium text-sm transition"
          >
            <span>🤖</span>
            <span>Run a workflow</span>
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium text-sm transition"
          >
            <span>📈</span>
            <span>Analytics</span>
          </Link>
          <Link
            href="/team"
            className="flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium text-sm transition"
          >
            <span>⚙️</span>
            <span>Team</span>
          </Link>
        </nav>

        {/* User at bottom */}
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-teal-700 flex items-center justify-center text-white text-xs font-bold">
              {displayName.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-slate-200 text-sm font-medium truncate">{displayName}</p>
              <p className="text-slate-500 text-xs truncate">{String(user?.role ?? "member")}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left px-3 py-1.5 text-xs text-slate-400 hover:text-red-400 hover:bg-red-900/20 rounded-lg transition"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {/* Top header */}
        <header className="sticky top-0 z-10 bg-slate-900/90 backdrop-blur border-b border-slate-800 px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">Mission Control</h1>
            <p className="text-slate-400 text-sm">Welcome back, {displayName}</p>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-xs bg-blue-900 text-blue-300 px-3 py-1 rounded-full border border-blue-700">
              V2 LAN Edition
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition"
            >
              Logout
            </button>
          </div>
        </header>

        <div className="p-8">
          {loading && (
            <div className="text-center py-16 text-slate-400">Loading dashboard data…</div>
          )}

          {!loading && (
            <>
              {error && (
                <div className="mb-6 bg-red-900/30 border border-red-700 rounded-xl px-5 py-4 text-red-300 text-sm">
                  {error}
                </div>
              )}

              {/* Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
                {/* Inference Mode */}
                <div className={`p-5 rounded-2xl border ${inferenceBadgeColor} bg-opacity-50`}>
                  <p className="text-xs font-semibold uppercase tracking-widest mb-2 opacity-70">
                    Inference Mode
                  </p>
                  <p className="text-xl font-bold leading-tight">
                    {inferenceMode ?? "Unavailable"}
                  </p>
                  <p className="text-xs mt-1 opacity-60">
                    {health?.status ?? "No health data"}
                  </p>
                </div>

                {/* Pending Approvals */}
                <Link href="/approvals">
                  <div className="p-5 rounded-2xl bg-slate-800 border border-slate-700 hover:border-teal-600 transition cursor-pointer">
                    <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">
                      Pending Approvals
                    </p>
                    <p className="text-3xl font-bold text-white">{pendingCount}</p>
                    <p className="text-xs text-teal-400 mt-1">View all →</p>
                  </div>
                </Link>

                {/* Workflows */}
                <div className="p-5 rounded-2xl bg-slate-800 border border-slate-700">
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">
                    Total Workflows
                  </p>
                  <p className="text-3xl font-bold text-white">{totalWorkflows}</p>
                  <p className="text-xs text-slate-500 mt-1">Configured automations</p>
                </div>

                {/* Executions */}
                <div className="p-5 rounded-2xl bg-slate-800 border border-slate-700">
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">
                    Total Executions
                  </p>
                  <p className="text-3xl font-bold text-white">
                    {analytics?.total_executions ?? "—"}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">All-time runs</p>
                </div>
              </div>

              {/* Workflows Table */}
              <div className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
                  <h2 className="text-white font-semibold">Recent Workflows</h2>
                  <Link
                    href="/workflows"
                    className="text-xs text-teal-400 hover:text-teal-300 transition"
                  >
                    View all →
                  </Link>
                </div>

                {workflows.length === 0 ? (
                  <div className="p-10 text-center text-slate-500 text-sm">
                    No workflows found. Create your first workflow to get started.
                  </div>
                ) : (
                  <div className="divide-y divide-slate-700">
                    {workflows.slice(0, 10).map((wf) => (
                      <div
                        key={wf.id}
                        className="px-6 py-4 flex items-center justify-between hover:bg-slate-700/40 transition"
                      >
                        <div>
                          <p className="text-slate-200 font-medium text-sm">{wf.name}</p>
                          <p className="text-slate-500 text-xs font-mono mt-0.5">{wf.id}</p>
                        </div>
                        <span
                          className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                            wf.is_published && wf.is_active
                              ? "bg-green-900/60 text-green-300"
                              : !wf.is_published
                              ? "bg-yellow-900/60 text-yellow-300"
                              : "bg-slate-700 text-slate-400"
                          }`}
                        >
                          {wf.is_published ? (wf.is_active ? "ACTIVE" : "INACTIVE") : "DRAFT"}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
