"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { request } from "@/lib/api";
import type { AdminProfile, Page } from "@/lib/types";

export default function AdminDashboard() {
  const router = useRouter();
  const [draft, setDraft] = useState("");
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [reload, setReload] = useState(0);
  const [data, setData] = useState<Page<AdminProfile> | null>(null);
  const [detail, setDetail] = useState<AdminProfile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      const q = new URLSearchParams({ page: String(page) });
      if (search) q.set("search", search);
      if (status) q.set("status", status);
      const r = await request<Page<AdminProfile>>(`/admin/profiles?${q}`);
      if (!r.ok) {
        // No valid admin session -> back to admin login (server enforces this too).
        if (r.status === 401 || r.status === 403) router.push("/admin/login");
        else setError(r.error);
        return;
      }
      setError("");
      setData(r.data);
    }
    load();
  }, [search, status, page, reload, router]);

  function onSearch(e: FormEvent) {
    e.preventDefault();
    setPage(1);
    setSearch(draft.trim());
  }

  async function view(id: number) {
    const r = await request<AdminProfile>(`/admin/profiles/${id}`);
    if (r.ok) setDetail(r.data);
    else setError(r.error);
  }

  async function deactivate(id: number) {
    if (!confirm("Deactivate this profile?")) return;
    const r = await request<AdminProfile>(`/admin/profiles/${id}/deactivate`, "PATCH");
    if (!r.ok) {
      setError(r.error);
      return;
    }
    if (detail?.id === id) setDetail(r.data);
    setReload((n) => n + 1);
  }

  async function logout() {
    await request("/admin/logout", "POST");
    router.push("/admin/login");
  }

  return (
    <div>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h1>Admin dashboard</h1>
        <button className="secondary" onClick={logout}>Log out</button>
      </div>

      <form className="row" onSubmit={onSearch}>
        <input style={{ maxWidth: 280 }} placeholder="Search name or email"
          aria-label="Search" value={draft} onChange={(e) => setDraft(e.target.value)} />
        <button>Search</button>
        <select style={{ maxWidth: 160 }} aria-label="Status filter" value={status}
          onChange={(e) => { setPage(1); setStatus(e.target.value); }}>
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </form>

      {error && <div className="error" role="alert">{error}</div>}

      {data && (
        <>
          <table>
            <thead>
              <tr><th>Name</th><th>Email</th><th>Status</th><th>Created</th><th></th></tr>
            </thead>
            <tbody>
              {data.results.map((p) => (
                <tr key={p.id}>
                  <td>{p.full_name}</td>
                  <td>{p.user_email}</td>
                  <td><span className={`badge ${p.status}`}>{p.status}</span></td>
                  <td>{new Date(p.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="row" style={{ margin: 0 }}>
                      <button className="secondary" onClick={() => view(p.id)}>View</button>
                      {p.status === "active" && (
                        <button className="danger" onClick={() => deactivate(p.id)}>Deactivate</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {data.results.length === 0 && (
                <tr><td colSpan={5}>No profiles found.</td></tr>
              )}
            </tbody>
          </table>
          <div className="row">
            <button className="secondary" disabled={!data.previous} onClick={() => setPage(page - 1)}>Previous</button>
            <span>Page {page} · {data.count} profiles</span>
            <button className="secondary" disabled={!data.next} onClick={() => setPage(page + 1)}>Next</button>
          </div>
        </>
      )}

      {detail && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="row" style={{ justifyContent: "space-between", marginTop: 0 }}>
            <h2>Profile details</h2>
            <button className="secondary" onClick={() => setDetail(null)}>Close</button>
          </div>
          <dl>
            {Object.entries(detail).map(([k, v]) => (
              <div key={k} style={{ display: "contents" }}>
                <dt>{k}</dt>
                <dd>{String(v ?? "")}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}