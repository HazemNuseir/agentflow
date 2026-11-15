"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { isLoggedIn } from "../../lib/auth";
import { apiClient } from "../../lib/api";

interface Approval {
  id: string;
  created_at?: string;
  status?: string;
  context_payload?: Record<string, unknown>;
  [key: string]: unknown;
}

export default function ApprovalsPage() {
  const router = useRouter();
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deciding, setDeciding] = useState<Set<string>>(new Set());
  const [decisions, setDecisions] = useState<Record<string, string>>({});

  async function fetchApprovals() {
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.get("/api/v1/approvals/?status=PENDING");
      if (!res.ok) {
        setError("Failed to load approvals.");
        setLoading(false);
        return;
      }
      const data = await res.json();
      const items: Approval[] = Array.isArray(data) ? data : data.items ?? [];
      setApprovals(items);
    } catch {
      setError("Network error loading approvals.");
    }
    setLoading(false);
  }

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    fetchApprovals();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function decide(id: string, decision: string) {
    setDeciding((prev) => new Set(prev).add(id));
    try {
      const res = await apiClient.post(`/api/v1/approvals/${id}/decision`, {
        decision,
        comment: "",
      });

      let message = "";
      if (res.status === 200) {
        message = "Decision recorded";
        // Reload approvals after a short delay
        setTimeout(() => fetchApprovals(), 500);
      } else if (res.status === 403) {
        message = "Not authorized to decide this approval";
      } else if (res.status === 409) {
        message = "Already decided";
      } else {
        const data = await res.json().catch(() => ({}));
        message = data.detail || `Error (${res.status})`;
      }

      setDecisions((prev) => ({ ...prev, [id]: message }));
    } catch {
      setDecisions((prev) => ({ ...prev, [id]: "Network error" }));
    }
    setDeciding((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard" className="text-slate-400 hover:text-slate-200 text-sm transition">
            ← Back to Dashboard
          </Link>
          <div className="w-px h-5 bg-slate-700" />
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-teal-500 flex items-center justify-center font-bold text-slate-950 text-sm">
              AF
            </div>
            <div>
              <h1 className="text-white font-bold text-sm leading-tight">Approvals Center</h1>
              <p className="text-teal-400 text-xs">DME AgentFlow V2</p>
            </div>
          </div>
        </div>
        <span className="text-xs bg-blue-900 text-blue-300 px-3 py-1 rounded-full border border-blue-700">
          V2 LAN Edition
        </span>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">Pending Approvals</h2>
            <p className="text-slate-400 text-sm mt-1">
              Human-in-the-loop decisions required for running workflows.
            </p>
          </div>
          <button
            onClick={fetchApprovals}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition border border-slate-700"
          >
            {loading ? "Refreshing…" : "↻ Refresh"}
          </button>
        </div>

        {/* Error state */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl px-5 py-4 text-red-300 text-sm mb-6">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-16 text-slate-400">Loading approvals…</div>
        )}

        {/* Empty state */}
        {!loading && !error && approvals.length === 0 && (
          <div className="text-center py-16">
            <div className="text-5xl mb-4">✅</div>
            <p className="text-xl font-semibold text-white mb-2">No pending approvals — all clear!</p>
            <p className="text-slate-400 text-sm">
              All workflow steps are either completed or awaiting other conditions.
            </p>
          </div>
        )}

        {/* Approval cards */}
        {!loading && approvals.length > 0 && (
          <div className="space-y-4">
            {approvals.map((approval) => (
              <div
                key={approval.id}
                className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden"
              >
                <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-400 font-mono">
                      ID: {approval.id.slice(0, 8)}…{approval.id.slice(-4)}
                    </p>
                    {approval.created_at && (
                      <p className="text-xs text-slate-500 mt-0.5">
                        {new Date(approval.created_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                  <span className="text-xs bg-yellow-900/50 border border-yellow-700 text-yellow-300 px-2.5 py-1 rounded-full font-semibold">
                    PENDING
                  </span>
                </div>

                {/* Context payload */}
                {approval.context_payload && (
                  <div className="px-6 py-4 border-b border-slate-700">
                    <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-2">
                      Context
                    </p>
                    <pre className="text-xs text-slate-300 bg-slate-900 rounded-lg p-4 overflow-auto max-h-40 font-mono leading-relaxed">
                      {JSON.stringify(approval.context_payload, null, 2)}
                    </pre>
                  </div>
                )}

                {/* Decision result message */}
                {decisions[approval.id] && (
                  <div
                    className={`px-6 py-3 text-sm font-medium border-b border-slate-700 ${
                      decisions[approval.id] === "Decision recorded"
                        ? "bg-green-900/30 text-green-300"
                        : "bg-red-900/30 text-red-300"
                    }`}
                  >
                    {decisions[approval.id]}
                  </div>
                )}

                {/* Action buttons */}
                <div className="px-6 py-4 flex items-center space-x-3">
                  <button
                    onClick={() => decide(approval.id, "APPROVED")}
                    disabled={deciding.has(approval.id)}
                    className="px-5 py-2 rounded-lg bg-green-700 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition"
                  >
                    ✓ Approve
                  </button>
                  <button
                    onClick={() => decide(approval.id, "REJECTED")}
                    disabled={deciding.has(approval.id)}
                    className="px-5 py-2 rounded-lg bg-red-700 hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition"
                  >
                    ✗ Reject
                  </button>
                  <button
                    onClick={() => decide(approval.id, "CLARIFY")}
                    disabled={deciding.has(approval.id)}
                    className="px-5 py-2 rounded-lg bg-yellow-700 hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition"
                  >
                    ? Clarify
                  </button>
                  {deciding.has(approval.id) && (
                    <span className="text-slate-400 text-sm ml-2">Processing…</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
