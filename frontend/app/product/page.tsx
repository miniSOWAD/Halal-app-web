"use client";

import Link from "next/link";
import { ExternalLink, Heart, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";

import Loading from "@/components/Loading";
import { api } from "@/lib/api";
import type { Product } from "@/lib/types";

function statusClass(status: string) {
  if (["CERTIFIED_HALAL", "NO_PROHIBITED_INGREDIENT_FOUND", "HEALTHY"].includes(status)) return "good";
  if (["HARAM", "UNHEALTHY"].includes(status)) return "bad";
  if (["DOUBTFUL", "MODERATE"].includes(status)) return "warn";
  return "neutral";
}

export default function ProductPage() {
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("id");
    if (!id) { setError("Product ID is missing."); return; }
    api.getProduct(id).then(setProduct).catch((reason) => setError(reason instanceof Error ? reason.message : "Could not load product."));
  }, []);

  async function save() {
    if (!product) return;
    try { await api.addFavorite(product.id); setNotice("Saved to favorites."); }
    catch (reason) { setNotice(reason instanceof Error ? reason.message : "Could not save product."); }
  }

  if (error) return <div className="page-shell page-content"><p className="form-error">{error}</p></div>;
  if (!product) return <div className="page-shell page-content"><Loading label="Loading product…" /></div>;

  return <div className="page-shell page-content"><section className="card product-detail-header"><div className="product-image xlarge">{product.image_url ? <img src={product.image_url} alt="" /> : <ShieldCheck size={58} />}</div><div className="product-detail-copy"><p className="eyebrow">{product.brand || "Unbranded"}</p><h1>{product.name}</h1><p className="muted">{product.category || "Food product"}{product.barcode ? ` · ${product.barcode}` : ""}</p><div className="status-row"><span className={`status-pill ${statusClass(product.halal_status)}`}>{product.halal_status.replaceAll("_", " ")}</span><span className={`status-pill ${statusClass(product.health_status)}`}>{product.health_status} · {product.health_score}/100</span></div><div className="button-row"><button className="button secondary" onClick={save}><Heart size={18} /> Save product</button>{product.ingredient_text && <Link className="button" href={`/ingredients/?text=${encodeURIComponent(product.ingredient_text)}`}>Recheck ingredients</Link>}</div>{notice && <p className="notice inline">{notice}</p>}</div></section><div className="detail-grid"><section className="card"><p className="eyebrow">Ingredients</p><h2>Label information</h2><p className="ingredient-copy">{product.ingredient_text || "No ingredient list is available."}</p></section><section className="card"><p className="eyebrow">Nutrition</p><h2>Available values</h2>{product.nutrition_data && Object.keys(product.nutrition_data).length ? <dl className="nutrition-list">{Object.entries(product.nutrition_data).map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{String(value)}</dd></div>)}</dl> : <p className="muted">No nutrition values are available.</p>}</section></div><section className="card"><p className="eyebrow">Certification</p><h2>Certificate records</h2>{product.certifications?.length ? <div className="certificate-list">{product.certifications.map((certificate) => <div className="certificate-item" key={certificate.id}><div><strong>{certificate.authority_name}</strong><span>#{certificate.certificate_number} · {certificate.status}</span></div>{certificate.verification_url && <a href={certificate.verification_url} target="_blank" rel="noreferrer"><ExternalLink size={17} /> Verify</a>}</div>)}</div> : <p className="muted">No active certificate record is stored for this product.</p>}</section><p className="disclaimer">Stored product results can become outdated when ingredients or certificates change. Recheck the package label when accuracy matters.</p></div>;
}
