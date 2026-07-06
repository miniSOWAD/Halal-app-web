"use client";

import Link from "next/link";
import { Eye, EyeOff, MailCheck, UserPlus } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", country: "", phone: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      await api.registerSendOtp({
        name: form.name,
        email: form.email,
        password: form.password,
        country: form.country || undefined,
        phone: form.phone || undefined,
      });
      router.push(`/verify-otp/?purpose=register&email=${encodeURIComponent(form.email)}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not send the verification code.");
    } finally { setBusy(false); }
  }

  return (
    <div className="auth-page page-shell">
      <form className="auth-card auth-card-wide" onSubmit={submit}>
        <div className="auth-icon"><UserPlus /></div><p className="eyebrow">Create an account</p><h1>Start checking food</h1>
        <p className="muted">We will email a six-digit verification code that expires after two minutes.</p>
        <div className="two-cols">
          <label>Full name<input required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
          <label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
        </div>
        <label>Password<div className="password-field"><input type={showPassword ? "text" : "password"} required minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /><button type="button" onClick={() => setShowPassword((value) => !value)} aria-label="Show password">{showPassword ? <EyeOff /> : <Eye />}</button></div></label>
        <div className="two-cols">
          <label>Phone number <small>(optional)</small><input type="tel" maxLength={32} placeholder="+880…" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
          <label>Country code <small>(optional)</small><input maxLength={2} placeholder="US, GB, MY…" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value.toUpperCase() })} /></label>
        </div>
        {error && <p className="form-error">{error}</p>}
        <button className="button full" disabled={busy}><MailCheck /> {busy ? "Sending OTP…" : "Send OTP"}</button>
        <p className="auth-switch">Already registered? <Link href="/login/">Sign in</Link></p>
      </form>
    </div>
  );
}
