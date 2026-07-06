"use client";

import Link from "next/link";
import { Clock3, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import Loading from "@/components/Loading";
import { api } from "@/lib/api";
import type { HistoryItem } from "@/lib/types";

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => { api.history().then(setItems).catch((reason) => setError(reason instanceof Error ? reason.message : "Sign in to view scan history.")).finally(() => setBusy(false)); }, []);
  async function remove(id: string) { await api.deleteHistory(id); setItems((current) => current.filter((item) => item.id !== id)); }
  return <div className="page-shell page-content"><div className="page-heading"><p className="eyebrow">Your account</p><h1>Scan history</h1><p>Open previous ingredient, barcode, QR and image results.</p></div>{busy ? <Loading /> : error ? <div className="empty-state"><h2>History requires sign in</h2><p>{error}</p><Link className="button" href="/login/">Sign in</Link></div> : items.length ? <div className="history-list">{items.map((item) => <div className="history-item" key={item.id}><Link href={`/result/?id=${item.id}`}><div className="history-icon"><Clock3 /></div><div><strong>{item.product?.name || item.input_type.replaceAll("_", " ")}</strong><span>{new Date(item.created_at).toLocaleString()}</span><div className="status-row"><small>{item.halal_status.replaceAll("_", " ")} · {item.halal_confidence}%</small><small>{item.health_status} · {item.health_score}/100</small></div></div></Link><button className="icon-button" onClick={() => void remove(item.id)} aria-label="Delete scan"><Trash2 size={18} /></button></div>)}</div> : <div className="empty-state"><h2>No scans yet</h2><p>Your saved scan results will appear here.</p><Link className="button" href="/scan/">Scan food</Link></div>}</div>;
}
