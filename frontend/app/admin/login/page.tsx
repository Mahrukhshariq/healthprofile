"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { request } from "@/lib/api";

export default function AdminLoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    await request("/admin/csrf"); // sets the csrftoken cookie
    const r = await request("/admin/login", "POST", form);
    setBusy(false);
    if (!r.ok) {
      setError(r.error);
      return;
    }
    router.push("/admin");
  }

  return (
    <form className="card" onSubmit={onSubmit}>
      <h1>Admin login</h1>
      <p>Admin accounts are created by the server (no public signup).</p>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" required value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })} />
      <label htmlFor="password">Password</label>
      <input id="password" type="password" required value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })} />
      {error && <div className="error" role="alert">{error}</div>}
      <div className="row">
        <button disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button>
      </div>
    </form>
  );
}