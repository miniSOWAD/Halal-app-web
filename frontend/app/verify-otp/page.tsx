"use client";

import { MailCheck, RefreshCw } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { verifyEmailChange, verifyRegistration } from "@/lib/auth";
import { api } from "@/lib/api";

export default function VerifyOtpPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [purpose, setPurpose] = useState("register");
  const [otp, setOtp] = useState("");
  const [expires, setExpires] = useState(120);
  const [resend, setResend] = useState(60);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setEmail(params.get("email") || "");
    setPurpose(params.get("purpose") || "register");
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setExpires((value) => Math.max(0, value - 1));
      setResend((value) => Math.max(0, value - 1));
    }, 1000);
    return () => window.clearInterval(timer);
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      if (purpose === "register") {
        await verifyRegistration(email, otp);
        router.push("/");
      } else if (purpose === "password-reset") {
        const result = await api.forgotPasswordVerifyOtp(email, otp);
        router.push(`/reset-password/?token=${encodeURIComponent(result.reset_token)}`);
      } else {
        await verifyEmailChange(email, otp);
        router.push("/profile/?emailChanged=1");
      }
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Verification failed."); }
    finally { setBusy(false); }
  }

  async function resendCode() {
    setBusy(true); setError(""); setNotice("");
    try {
      if (purpose === "register") await api.registerResendOtp(email);
      else if (purpose === "password-reset") await api.forgotPasswordResendOtp(email);
      else await api.emailChangeResendOtp(email);
      setExpires(120); setResend(60); setNotice("A new OTP was sent.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not resend the code."); }
    finally { setBusy(false); }
  }

  const format = (seconds: number) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;

  return (
    <div className="auth-page page-shell"><form className="auth-card otp-card" onSubmit={submit}><div className="auth-icon"><MailCheck /></div><p className="eyebrow">Email verification</p><h1>Enter the six-digit OTP</h1><p className="muted">We sent the code to <strong>{email || "your email"}</strong>.</p><input className="otp-input" inputMode="numeric" autoComplete="one-time-code" maxLength={6} pattern="[0-9]{6}" required value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))} placeholder="000000" /><div className={expires ? "otp-timer" : "otp-timer expired"}>{expires ? `Code expires in ${format(expires)}` : "Code expired. Request a new one."}</div>{error && <p className="form-error">{error}</p>}{notice && <p className="notice inline">{notice}</p>}<button className="button full" disabled={busy || otp.length !== 6 || expires === 0}>{busy ? "Checking…" : "Verify OTP"}</button><button className="button secondary full" type="button" onClick={resendCode} disabled={busy || resend > 0}><RefreshCw /> {resend > 0 ? `Resend OTP in ${format(resend)}` : "Resend OTP"}</button></form></div>
  );
}
