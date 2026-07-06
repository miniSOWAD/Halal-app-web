"use client";

import Link from "next/link";
import { AlertTriangle, CheckCircle2, ExternalLink, Heart, Info, ShieldAlert, ShieldCheck } from "lucide-react";
import { useState } from "react";

import IngredientTable from "@/components/IngredientTable";
import { api } from "@/lib/api";
import type { AnalysisResult } from "@/lib/types";

function resultClass(status: string) {
  if (["CERTIFIED_HALAL", "NO_PROHIBITED_INGREDIENT_FOUND", "HEALTHY"].includes(status)) return "good";
  if (["HARAM", "UNHEALTHY"].includes(status)) return "bad";
  if (["DOUBTFUL", "MODERATE"].includes(status)) return "warn";
  return "neutral";
}

function ResultIcon({ status }: { status: string }) {
  if (["CERTIFIED_HALAL", "NO_PROHIBITED_INGREDIENT_FOUND", "HEALTHY"].includes(status)) return <CheckCircle2 />;
  if (["HARAM", "UNHEALTHY"].includes(status)) return <ShieldAlert />;
  if (["DOUBTFUL", "MODERATE"].includes(status)) return <AlertTriangle />;
  return <Info />;
}

export default function ScanResult({ result }: { result: AnalysisResult }) {
  const [notice, setNotice] = useState("");
  const [reportOpen, setReportOpen] = useState(false);
  const [report, setReport] = useState("");

  async function saveProduct() {
    if (!result.product?.id) return;
    try {
      await api.addFavorite(result.product.id);
      setNotice("Product saved to favorites.");
    } catch (reason) {
      setNotice(reason instanceof Error ? reason.message : "Could not save the product.");
    }
  }

  async function submitReport() {
    if (report.trim().length < 5) return;
    try {
      await api.createReport({ product_id: result.product?.id ?? undefined, subject: "Incorrect scan result", category: "PRODUCT_DATA", message: report.trim() });
      setReport("");
      setReportOpen(false);
      setNotice("Report submitted for review.");
    } catch (reason) {
      setNotice(reason instanceof Error ? reason.message : "Could not send the report.");
    }
  }

  return (
    <div className="result-stack">
      <section className="result-hero card">
        <div className="result-product">
          <div className="product-image large">
            {result.product?.image_url ? <img src={result.product.image_url} alt="" /> : <ShieldCheck size={48} />}
          </div>
          <div>
            <p className="eyebrow">{result.product?.brand || result.input_type.replaceAll("_", " ")}</p>
            <h1>{result.product?.name || "Food analysis"}</h1>
            {result.product?.barcode && <p className="muted">Barcode: {result.product.barcode}</p>}
          </div>
        </div>
        <div className="button-row">
          {result.product?.id && <button className="button secondary" onClick={saveProduct}><Heart size={18} /> Save</button>}
          <button className="button ghost" onClick={() => setReportOpen((value) => !value)}>Report a problem</button>
        </div>
      </section>

      {notice && <div className="notice">{notice}</div>}
      {reportOpen && (
        <section className="card report-box">
          <h3>What looks wrong?</h3>
          <textarea value={report} onChange={(event) => setReport(event.target.value)} placeholder="Explain the incorrect ingredient, certificate or health result." />
          <div className="button-row"><button className="button" onClick={submitReport}>Send report</button></div>
        </section>
      )}

      <div className="result-grid">
        <section className={`result-card ${resultClass(result.halal.status)}`}>
          <div className="result-card-heading"><ResultIcon status={result.halal.status} /><span>Halal status</span></div>
          <h2>{result.halal.label}</h2>
          <div className="confidence"><span>Confidence</span><strong>{result.halal.confidence}%</strong></div>
          <div className="progress"><span style={{ width: `${result.halal.confidence}%` }} /></div>
          <h3>Why?</h3>
          <ul>{result.halal.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>
          <div className="certificate-box">
            <strong>{result.halal.certificate.found ? "Certificate found" : "No active certificate verified"}</strong>
            {result.halal.certificate.authority && <span>{result.halal.certificate.authority}</span>}
            {result.halal.certificate.certificate_number && <span>#{result.halal.certificate.certificate_number}</span>}
            {result.halal.certificate.verification_url && (
              <a href={result.halal.certificate.verification_url} target="_blank" rel="noreferrer">Verify <ExternalLink size={15} /></a>
            )}
          </div>
        </section>

        <section className={`result-card ${resultClass(result.health.status)}`}>
          <div className="result-card-heading"><ResultIcon status={result.health.status} /><span>Health status</span></div>
          <div className="score-ring" style={{ "--score": `${result.health.score * 3.6}deg` } as React.CSSProperties}>
            <strong>{result.health.score}</strong><span>/100</span>
          </div>
          <h2>{result.health.status.charAt(0) + result.health.status.slice(1).toLowerCase()}</h2>
          <div className="confidence"><span>Confidence</span><strong>{result.health.confidence}%</strong></div>
          <h3>Why?</h3>
          <ul>{result.health.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>
        </section>
      </div>

      <section className="recommendation">
        <Info size={22} />
        <div><strong>Recommendation</strong><p>{result.recommendation}</p></div>
      </section>

      <section className="card">
        <div className="section-heading"><div><p className="eyebrow">Ingredient breakdown</p><h2>What the app checked</h2></div><span>{result.ingredients.length} ingredients</span></div>
        <IngredientTable ingredients={result.ingredients} />
      </section>

      {result.alternatives.length > 0 && (
        <section className="card">
          <div className="section-heading"><div><p className="eyebrow">Better choices</p><h2>Suggested alternatives</h2></div></div>
          <div className="alternative-grid">
            {result.alternatives.map((item) => (
              <Link className="alternative-card" href={`/product/?id=${item.id}`} key={item.id}>
                <strong>{item.name}</strong><span>{item.brand || ""}</span><b>{item.health_score}/100</b>
              </Link>
            ))}
          </div>
        </section>
      )}

      {result.extracted_text && (
        <details className="card raw-text"><summary>View extracted text</summary><pre>{result.extracted_text}</pre></details>
      )}
      <p className="disclaimer">Ingredient screening does not replace an official halal certificate, qualified religious guidance, or professional medical advice.</p>
    </div>
  );
}
