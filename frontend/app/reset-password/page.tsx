"use client";

import Link from "next/link";
import { Eye, EyeOff, KeyRound } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { api } from "@/lib/api";

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  useEffect(() => setToken(new URLSearchParams(window.location.search).get("token") || ""), []);
  async function submit(event: FormEvent) {
    event.preventDefault(); setError("");
    if (password !== confirm) { setError("Passwords do not match."); return; }
    setBusy(true);
    try { await api.resetPassword(token, password); setDone(true); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not reset the password."); }
    finally { setBusy(false); }
  }
  if (done) return <div className="auth-page page-shell"><div className="auth-card"><div className="auth-icon"><KeyRound /></div><h1>Password updated</h1><p className="muted">Your new password is ready.</p><Link className="button full" href="/login/">Sign in</Link></div></div>;
  return <div className="auth-page page-shell"><form className="auth-card" onSubmit={submit}><div className="auth-icon"><KeyRound /></div><p className="eyebrow">New password</p><h1>Choose a secure password</h1><label>New password<div className="password-field"><input type={show ? "text" : "password"} required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} /><button type="button" onClick={() => setShow((value) => !value)}>{show ? <EyeOff /> : <Eye />}</button></div></label><label>Confirm password<input type={show ? "text" : "password"} required minLength={8} value={confirm} onChange={(e) => setConfirm(e.target.value)} /></label>{error && <p className="form-error">{error}</p>}<button className="button full" disabled={busy || !token}>{busy ? "Updating…" : "Update password"}</button></form></div>;
}
