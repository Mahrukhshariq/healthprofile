"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { request } from "@/lib/api";
import type { Profile } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      const r = await request<Profile>("/profiles/me", "GET", undefined, true);
      if (!r.ok) {
        if (r.status === 401) router.push("/login");
        else setError(r.error);
        return;
      }
      setProfile(r.data);
    }
    load();
  }, [router]);

  function update<K extends keyof Profile>(key: K, value: Profile[K]) {
    setProfile((p) => (p ? { ...p, [key]: value } : p));
    setSaved(false);
  }

  async function onSave(e: FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setError("");
    const body = {
      full_name: profile.full_name,
      date_of_birth: profile.date_of_birth || null,
      contact_preference: profile.contact_preference,
      wellness_goals: profile.wellness_goals,
      allergies: profile.allergies,
      emergency_contact_name: profile.emergency_contact_name,
      emergency_contact_phone: profile.emergency_contact_phone,
      lifestyle_notes: profile.lifestyle_notes,
    };
    const r = await request<Profile>("/profiles/me", "PATCH", body, true);
    if (!r.ok) {
      setError(r.error);
      return;
    }
    setProfile(r.data);
    setSaved(true);
  }

  async function onLogout() {
    await request("/auth/logout", "POST");
    router.push("/login");
  }

  if (!profile) return <div className="card">{error || "Loading..."}</div>;

  return (
    <form className="card" onSubmit={onSave}>
      <h1>My profile</h1>
      <p>Status: <span className={`badge ${profile.status}`}>{profile.status}</span></p>

      <label htmlFor="full_name">Full name</label>
      <input id="full_name" required value={profile.full_name}
        onChange={(e) => update("full_name", e.target.value)} />

      <label htmlFor="dob">Date of birth</label>
      <input id="dob" type="date" value={profile.date_of_birth ?? ""}
        onChange={(e) => update("date_of_birth", e.target.value)} />

      <label htmlFor="contact">Contact preference</label>
      <select id="contact" value={profile.contact_preference}
        onChange={(e) => update("contact_preference", e.target.value as Profile["contact_preference"])}>
        <option value="email">Email</option>
        <option value="phone">Phone</option>
        <option value="sms">SMS</option>
      </select>

      <label htmlFor="goals">Wellness goals</label>
      <textarea id="goals" rows={2} value={profile.wellness_goals}
        onChange={(e) => update("wellness_goals", e.target.value)} />

      <label htmlFor="allergies">Allergies (optional)</label>
      <textarea id="allergies" rows={2} value={profile.allergies}
        onChange={(e) => update("allergies", e.target.value)} />

      <label htmlFor="ecname">Emergency contact name (fictional)</label>
      <input id="ecname" value={profile.emergency_contact_name}
        onChange={(e) => update("emergency_contact_name", e.target.value)} />

      <label htmlFor="ecphone">Emergency contact phone (fictional)</label>
      <input id="ecphone" value={profile.emergency_contact_phone}
        onChange={(e) => update("emergency_contact_phone", e.target.value)} />

      <label htmlFor="notes">Lifestyle notes (optional)</label>
      <textarea id="notes" rows={3} value={profile.lifestyle_notes}
        onChange={(e) => update("lifestyle_notes", e.target.value)} />

      {error && <div className="error" role="alert">{error}</div>}
      {saved && <div className="success">Profile saved.</div>}
      <div className="row">
        <button>Save changes</button>
        <button type="button" className="secondary" onClick={onLogout}>Log out</button>
      </div>
      <p style={{ fontSize: 12 }}>Last updated: {new Date(profile.updated_at).toLocaleString()}</p>
    </form>
  );
}