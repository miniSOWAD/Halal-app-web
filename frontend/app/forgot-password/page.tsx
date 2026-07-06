"use client";

import Link from "next/link";
import { KeyRound, MailCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      await api.forgotPasswordSendOtp(email);
      router.push(`/verify-otp/?purpose=password-reset&email=${encodeURIComponent(email)}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not send the code.");
    } finally { setBusy(false); }
  }

  return <div className="auth-page page-shell"><form className="auth-card" onSubmit={submit}><div className="auth-icon"><KeyRound /></div><p className="eyebrow">Password recovery</p><h1>Reset your password</h1><p className="muted">Enter your registered email. The OTP expires in two minutes.</p><label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>{error && <p className="form-error">{error}</p>}<button className="button full" disabled={busy}><MailCheck /> {busy ? "Sending…" : "Send OTP"}</button><p className="auth-switch"><Link href="/login/">Return to sign in</Link></p></form></div>;
}
