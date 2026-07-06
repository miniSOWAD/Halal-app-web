"use client";

import Link from "next/link";
import { Mail, MessageSquareText, Send } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { User } from "@/lib/types";

export default function ContactPage() {
  const [user, setUser] = useState<User | null>(null);
  const [form, setForm] = useState({ subject: "", category: "GENERAL", message: "" });
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  useEffect(() => { api.me().then(setUser).catch(() => setUser(null)); }, []);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      await api.createReport(form);
      setNotice("Your message was sent and saved for review.");
      setForm({ subject: "", category: "GENERAL", message: "" });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not send your message.");
    } finally { setBusy(false); }
  }

  return (
    <div className="page-shell page-content contact-layout">
      <section className="contact-copy">
        <p className="eyebrow">Contact us</p><h1>Report a problem or ask a question.</h1>
        <p>Registered users can send product-data corrections, technical issues, account questions or general feedback directly to the HalalFit review queue.</p>
        <div className="contact-detail"><Mail /><div><strong>Email</strong><a href="mailto:baisakh2015@gmail.com">baisakh2015@gmail.com</a></div></div>
        <div className="contact-detail"><MessageSquareText /><div><strong>Reports are tracked</strong><span>Your message is stored in the database so the admin can review its status.</span></div></div>
      </section>
      {user ? (
        <form className="card form-card" onSubmit={submit}>
          <div className="form-title"><Send /><div><h2>Send a report</h2><p>Signed in as {user.email}</p></div></div>
          <label>Subject<input required minLength={3} maxLength={180} value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} /></label>
          <label>Category<select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}><option value="GENERAL">General</option><option value="PRODUCT_DATA">Incorrect product data</option><option value="TECHNICAL">Technical problem</option><option value="ACCOUNT">Account help</option><option value="OTHER">Other</option></select></label>
          <label>Message<textarea required minLength={5} maxLength={4000} rows={7} value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} /></label>
          {error && <p className="form-error">{error}</p>}{notice && <p className="notice inline">{notice}</p>}
          <button className="button full" disabled={busy}>{busy ? "Sending…" : "Send report"}</button>
        </form>
      ) : (
        <div className="card sign-in-contact"><MessageSquareText /><h2>Sign in to send a report</h2><p>This keeps reports linked to a real account and allows administrators to follow up accurately.</p><Link className="button" href="/login/">Sign in</Link></div>
      )}
    </div>
  );
}
