"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "../../lib/api";

type Member = { id: string; user_id: string; full_name: string; email: string; role: string };
const roles = ["VIEWER", "APPROVER", "WORKFLOW_EDITOR", "ORGANIZATION_ADMIN"];

export default function TeamPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [error, setError] = useState("");
  const [role, setRole] = useState("");
  const [userId, setUserId] = useState("");
  const [busy, setBusy] = useState(false);
  const admin = ["ORGANIZATION_OWNER", "ORGANIZATION_ADMIN"].includes(role);
  const refresh = useCallback(async () => {
    const [me, list] = await Promise.all([apiClient.get("/api/v1/auth/me"), apiClient.get("/api/v1/organizations/members")]);
    if (me.status === 401) { window.location.assign("/login"); return; }
    if (!me.ok || !list.ok) throw new Error("Could not load members.");
    const user = await me.json();
    setRole(user.role);
    setUserId(user.user_id);
    setMembers(await list.json());
  }, []);

  useEffect(() => { void refresh().catch((e) => setError(e.message)); }, [refresh]);

  async function submit(request: () => Promise<Response>) {
    setBusy(true);
    setError("");
    try {
      const response = await request();
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(typeof error.detail === "string" ? error.detail : "Could not save the change.");
      }
      await refresh();
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save the change.");
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function add(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const values = Object.fromEntries(new FormData(form));
    if (await submit(() => apiClient.post("/api/v1/organizations/members", values))) form.reset();
  }

  return <main className="lan-page">
    <Link href="/dashboard">Back to dashboard</Link>
    <h1>Team</h1>
    {error && <p role="alert">{error}</p>}
    <section>
      <h2>Members</h2>
      {members.map((member) => <div key={member.id}>
        <p>{member.full_name} · {member.email} · {member.role}</p>
        {admin && member.user_id !== userId && member.role !== "ORGANIZATION_OWNER" &&
          <select aria-label={"Role for " + member.email} disabled={busy} value={member.role}
            onChange={(e) => { const next = e.target.value; void submit(() =>
              apiClient.put("/api/v1/organizations/members/" + member.id + "/role", { role: next })); }}>
            {roles.map((item) => <option key={item}>{item}</option>)}
          </select>}
      </div>)}
    </section>
    {admin && <section>
      <h2>Add a member</h2>
      <form onSubmit={add}>
        <label>Name<input name="full_name" required /></label>
        <label>Email<input name="email" type="email" required /></label>
        <label>Initial password<input name="password" type="password" minLength={12} autoComplete="new-password" required /></label>
        <label>Role<select name="role">{roles.map((item) => <option key={item}>{item}</option>)}</select></label>
        <button disabled={busy}>Add member</button>
      </form>
    </section>}
  </main>;
}
