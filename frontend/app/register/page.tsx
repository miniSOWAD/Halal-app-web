"use client";

import Link from "next/link";
import { UserPlus } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { register } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", country: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try { await register(form.name, form.email, form.password, form.country || undefined); router.push("/"); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not create the account."); }
    finally { setBusy(false); }
  }

  return <div className="auth-page page-shell"><form className="auth-card" onSubmit={submit}><div className="auth-icon"><UserPlus /></div><p className="eyebrow">Create an account</p><h1>Start checking food</h1><label>Name<input required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label><label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Password<input type="password" required minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label><label>Country code <small>(optional)</small><input maxLength={2} placeholder="US, GB, MY…" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value.toUpperCase() })} /></label>{error && <p className="form-error">{error}</p>}<button className="button full" disabled={busy}>{busy ? "Creating…" : "Create account"}</button><p className="auth-switch">Already registered? <Link href="/login/">Sign in</Link></p></form></div>;
}
