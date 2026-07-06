"use client";

import Link from "next/link";
import { LogIn } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true); setError("");
    try { await login(email, password); router.push("/"); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not sign in."); }
    finally { setBusy(false); }
  }

  return <div className="auth-page page-shell"><form className="auth-card" onSubmit={submit}><div className="auth-icon"><LogIn /></div><p className="eyebrow">Welcome back</p><h1>Sign in to HalalFit</h1><p className="muted">Save scans, favorites and reports across devices.</p><label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" /></label><label>Password<input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" /></label>{error && <p className="form-error">{error}</p>}<button className="button full" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button><p className="auth-switch">No account? <Link href="/register/">Create one</Link></p></form></div>;
}
