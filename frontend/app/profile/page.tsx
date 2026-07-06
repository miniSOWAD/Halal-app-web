"use client";

import Link from "next/link";
import { Eye, EyeOff, KeyRound, LogOut, Mail, Settings, Shield, Smartphone } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Loading from "@/components/Loading";
import { logout } from "@/lib/auth";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState({ name: "", country: "", phone: "" });
  const [newEmail, setNewEmail] = useState("");
  const [passwords, setPasswords] = useState({ oldPassword: "", newPassword: "" });
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  useEffect(() => {
    api.me().then((value) => {
      setUser(value);
      setProfile({ name: value.name, country: value.country || "", phone: value.phone || "" });
      setNewEmail(value.email);
      if (new URLSearchParams(window.location.search).get("emailChanged")) setNotice("Email address updated.");
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Sign in required."));
  }, []);

  async function saveProfile(event: FormEvent) {
    event.preventDefault(); setBusy("profile"); setError(""); setNotice("");
    try {
      const updated = await api.updateMe({ name: profile.name, country: profile.country || undefined, phone: profile.phone || undefined });
      setUser(updated); setNotice("Profile details updated.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not update profile."); }
    finally { setBusy(""); }
  }

  async function sendEmailOtp(event: FormEvent) {
    event.preventDefault(); setBusy("email"); setError(""); setNotice("");
    try {
      await api.emailChangeSendOtp(newEmail);
      router.push(`/verify-otp/?purpose=email-change&email=${encodeURIComponent(newEmail)}`);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not send email verification."); }
    finally { setBusy(""); }
  }

  async function changePassword(event: FormEvent) {
    event.preventDefault(); setBusy("password"); setError(""); setNotice("");
    try {
      const result = await api.changePassword(passwords.oldPassword, passwords.newPassword);
      setPasswords({ oldPassword: "", newPassword: "" }); setNotice(result.message);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not change password."); }
    finally { setBusy(""); }
  }

  async function signOut() { await logout(); router.push("/"); }

  if (error && !user) return <div className="page-shell page-content"><div className="empty-state"><h2>Sign in required</h2><p>{error}</p><Link className="button" href="/login/">Sign in</Link></div></div>;
  if (!user) return <div className="page-shell page-content"><Loading /></div>;

  return (
    <div className="page-shell page-content profile-page">
      <div className="page-heading"><p className="eyebrow">Account</p><h1>Your profile</h1><p>Manage your personal details, verified email and password.</p></div>
      <section className="card profile-card"><div className="profile-avatar">{user.name.charAt(0).toUpperCase()}</div><div><h2>{user.name}</h2><p>{user.email}</p><div className="status-row"><span className="status-pill good">Email verified</span><span className="status-pill neutral">{user.is_admin ? "Administrator" : "User"}</span></div></div></section>
      {error && <p className="form-error">{error}</p>}{notice && <p className="notice inline">{notice}</p>}
      <div className="profile-settings-grid">
        <form className="card form-card" onSubmit={saveProfile}><div className="form-title"><Settings /><div><h2>Personal details</h2><p>Update your name, country and phone.</p></div></div><label>Name<input required minLength={2} value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} /></label><label>Phone number<div className="input-with-icon"><Smartphone /><input type="tel" maxLength={32} value={profile.phone} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} placeholder="+880…" /></div></label><label>Country code<input maxLength={2} value={profile.country} onChange={(e) => setProfile({ ...profile, country: e.target.value.toUpperCase() })} placeholder="US" /></label><button className="button" disabled={busy === "profile"}>{busy === "profile" ? "Saving…" : "Save details"}</button></form>
        <form className="card form-card" onSubmit={sendEmailOtp}><div className="form-title"><Mail /><div><h2>Change email</h2><p>The new address must be verified by OTP.</p></div></div><label>New email<input type="email" required value={newEmail} onChange={(e) => setNewEmail(e.target.value)} /></label><button className="button" disabled={busy === "email" || newEmail === user.email}>{busy === "email" ? "Sending…" : "Send verification OTP"}</button></form>
        <form className="card form-card" onSubmit={changePassword}><div className="form-title"><KeyRound /><div><h2>Change password</h2><p>Confirm the old password before setting a new one.</p></div></div><label>Old password<input type="password" required minLength={8} value={passwords.oldPassword} onChange={(e) => setPasswords({ ...passwords, oldPassword: e.target.value })} /></label><label>New password<div className="password-field"><input type={showNewPassword ? "text" : "password"} required minLength={8} value={passwords.newPassword} onChange={(e) => setPasswords({ ...passwords, newPassword: e.target.value })} /><button type="button" onClick={() => setShowNewPassword((value) => !value)} aria-label="Show new password">{showNewPassword ? <EyeOff /> : <Eye />}</button></div></label><button className="button" disabled={busy === "password"}>{busy === "password" ? "Changing…" : "Change password"}</button></form>
      </div>
      {user.is_admin && <Link className="card admin-link" href="/admin/"><Shield /><div><strong>Open admin panel</strong><span>Manage ingredients, products, certificates and reports.</span></div></Link>}
      <button className="button danger full" onClick={signOut}><LogOut /> Sign out</button>
    </div>
  );
}
