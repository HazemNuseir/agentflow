import React from 'react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between">
      {/* Navigation Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-teal-500 flex items-center justify-center font-bold text-slate-950 text-xl">
            AF
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-wide">DME AgentFlow</h1>
            <p className="text-xs text-teal-400 font-medium">Digital Mind Engineering • Jordan</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-xs bg-slate-800 text-slate-300 px-3 py-1 rounded-full border border-slate-700">
            Air-Gapped Sovereign AI
          </span>
          <span className="text-xs bg-blue-900 text-blue-300 px-3 py-1 rounded-full border border-blue-700">V2 LAN Edition</span>
          <Link
            href="/login"
            className="px-4 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-sm transition"
          >
            Launch Console
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-8 py-16 text-center flex-1 flex flex-col items-center justify-center">
        <div className="inline-flex items-center space-x-2 bg-teal-950/60 border border-teal-800/80 px-4 py-1.5 rounded-full text-xs text-teal-300 font-medium mb-8">
          <span>Sovereign Local Inference</span>
          <span>•</span>
          <span>Google Gemma 4 Architecture</span>
        </div>
        <h2 className="text-5xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          Your Business. Your Data. <span className="text-teal-400">Your AI.</span>
        </h2>
        <p className="text-lg text-slate-300 max-w-2xl mb-10 leading-relaxed">
          Intelligent, multi-tenant enterprise workflow automation executing 100% locally on your infrastructure. Zero external API leakage, strict tenant isolation, and private document intelligence.
        </p>

        <div className="flex flex-wrap justify-center gap-4 mb-16">
          <Link
            href="/login"
            className="px-8 py-3.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-base shadow-lg shadow-teal-500/20 transition"
          >
            Open Mission Control
          </Link>
          <a
            href="/api/v1/docs"
            target="_blank"
            rel="noreferrer"
            className="px-8 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-base border border-slate-700 transition"
          >
            Interactive API Specs
          </a>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left w-full">
          <div className="p-6 rounded-2xl bg-slate-950/50 border border-slate-800">
            <h3 className="text-lg font-bold text-white mb-2">Private AI Inference</h3>
            <p className="text-sm text-slate-400">
              Native llama-cpp-python GGUF models. Optimized for Gemma 4 E4B, 12B, 26B, and 31B parameter models without cloud dependencies.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-slate-950/50 border border-slate-800">
            <h3 className="text-lg font-bold text-white mb-2">Visual Automation Studio</h3>
            <p className="text-sm text-slate-400">
              29 domain-specific node blocks across triggers, branch conditions, AI logic, human approvals, and CRM integrations.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-slate-950/50 border border-slate-800">
            <h3 className="text-lg font-bold text-white mb-2">Local Knowledge Hub</h3>
            <p className="text-sm text-slate-400">
              Air-gapped document intelligence with private chunking, local vector embedding projections, and semantic cosine search.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950/90 py-6 px-8 text-center text-xs text-slate-500">
        <p>© 2026 Digital Mind Engineering (DME), Amman, Jordan. All rights reserved.</p>
        <p className="mt-1">DME AgentFlow • Sovereign Intelligent Business Automation</p>
      </footer>
    </div>
  );
}
