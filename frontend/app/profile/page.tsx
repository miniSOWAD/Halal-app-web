"use client";

import Link from "next/link";
import { LogOut, Settings, Shield } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Loading from "@/components/Loading";
import { logout } from "@/lib/auth";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  useEffect(() => { api.me().then((value) => { setUser(value); setName(value.name); setCountry(value.country || ""); }).catch((reason) => setError(reason instanceof Error ? reason.message : "Sign in required.")); }, []);
  async function save(event: FormEvent) { event.preventDefault(); const updated = await api.updateMe({ name, country: country || undefined }); setUser(updated); setNotice("Profile updated."); }
  async function signOut() { await logout(); router.push("/"); }
  if (error) return <div className="page-shell page-content"><div className="empty-state"><h2>Sign in required</h2><p>{error}</p><Link className="button" href="/login/">Sign in</Link></div></div>;
  if (!user) return <div className="page-shell page-content"><Loading /></div>;
  return <div className="page-shell page-content narrow"><div className="page-heading"><p className="eyebrow">Account</p><h1>Your profile</h1></div><section className="card profile-card"><div className="profile-avatar">{user.name.charAt(0).toUpperCase()}</div><div><h2>{user.name}</h2><p>{user.email}</p><span className="status-pill neutral">{user.is_admin ? "Administrator" : "User"}</span></div></section><form className="card form-card" onSubmit={save}><div className="form-title"><Settings /><div><h2>Preferences</h2><p>Basic account and regional details.</p></div></div><label>Name<input value={name} onChange={(e) => setName(e.target.value)} /></label><label>Country code<input maxLength={2} value={country} onChange={(e) => setCountry(e.target.value.toUpperCase())} placeholder="US" /></label>{notice && <p className="notice inline">{notice}</p>}<button className="button">Save changes</button></form>{user.is_admin && <Link className="card admin-link" href="/admin/"><Shield /><div><strong>Open admin panel</strong><span>Manage ingredients, products, certificates and reports.</span></div></Link>}<button className="button danger full" onClick={signOut}><LogOut /> Sign out</button></div>;
}
