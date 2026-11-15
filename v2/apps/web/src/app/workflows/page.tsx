"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "../../lib/api";

type Workflow = { id: string; name: string; is_published: boolean; is_active: boolean };
type Execution = { id: string; status: string; workflow_id: string };
type Template = { id: string; title: string };

async function read<T>(res: Response): Promise<T> {
  if (res.status === 401) {
    window.location.assign("/login");
    throw new Error("Sign in to continue.");
  }
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(typeof error.detail === "string" ? error.detail : "Request failed.");
  }
  return res.json();
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selected, setSelected] = useState("");
  const [input, setInput] = useState("{}");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const [flows, runs, catalog] = await Promise.all([
      apiClient.get("/api/v1/workflows/").then(read<Workflow[]>),
      apiClient.get("/api/v1/executions/").then(read<Execution[]>),
      apiClient.get("/api/v1/templates/").then(read<Template[]>),
    ]);
    setWorkflows(flows);
    setExecutions(runs);
    setTemplates(catalog);
  }

  useEffect(() => { void refresh().catch((e) => setError(e.message)); }, []);

  async function act(task: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      await task();
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed.");
    } finally {
      setBusy(false);
    }
  }

  function run(event: FormEvent) {
    event.preventDefault();
    void act(async () => {
      const payload = JSON.parse(input);
      if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
        throw new Error("Workflow input must be a JSON object.");
      }
      await read(await apiClient.post("/api/v1/executions/trigger", { workflow_id: selected, payload }));
    });
  }

  return <main className="lan-page">
    <Link href="/dashboard">Back to dashboard</Link>
    <h1>Workflows</h1>
    {error && <p role="alert">{error}</p>}
    <section>
      <h2>Run a workflow</h2>
      <form onSubmit={run}>
        <label>Published workflow<select required value={selected} onChange={(e) => setSelected(e.target.value)}>
          <option value="">Choose a workflow</option>
          {workflows.filter((w) => w.is_published && w.is_active).map((w) =>
            <option key={w.id} value={w.id}>{w.name}</option>)}
        </select></label>
        <label>Input (JSON)<textarea value={input} onChange={(e) => setInput(e.target.value)} /></label>
        <button disabled={busy || !selected}>Run workflow</button>
      </form>
    </section>
    <section>
      <h2>Workflow library</h2>
      {workflows.map((w) => <p key={w.id}>{w.name} · {w.is_published ? (w.is_active ? "Published" : "Inactive") :
        <button disabled={busy} onClick={() => void act(async () => read(await apiClient.post('/api/v1/workflows/' + w.id + '/publish', {})))}>Publish draft</button>}</p>)}
      <h3>Install a template</h3>
      {templates.map((t) => <p key={t.id}><button disabled={busy} onClick={() => void act(async () => read(await apiClient.post('/api/v1/templates/' + t.id + '/install', {})))}>{t.title}</button></p>)}
    </section>
    <section>
      <h2>Recent executions</h2>
      <button disabled={busy} onClick={() => void act(async () => undefined)}>Refresh</button>
      {executions.length === 0 && <p>No executions yet.</p>}
      {executions.map((run) => <details key={run.id}><summary>{workflows.find((w) => w.id === run.workflow_id)?.name ?? run.workflow_id} · {run.status}</summary><ExecutionDetails id={run.id} /></details>)}
    </section>
  </main>;
}

function ExecutionDetails({ id }: { id: string }) {
  const [data, setData] = useState<unknown>(null);
  const [error, setError] = useState("");
  return <div>
    <button onClick={() => {
      setError("");
      void apiClient.get("/api/v1/executions/" + id).then(read).then(setData).catch((e) => setError(e.message));
    }}>Load execution details</button>
    {error && <p role="alert">{error}</p>}
    {data !== null && <pre>{JSON.stringify(data, null, 2)}</pre>}
  </div>;
}
