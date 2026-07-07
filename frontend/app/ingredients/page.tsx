"use client";

import { FlaskConical, ListChecks } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";
import { rememberScanResult } from "@/lib/scan-cache";

export default function IngredientsPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [text, setText] = useState("");
  const [nutrition, setNutrition] = useState({ sugars_100g: "", saturated_fat_100g: "", sodium_100g: "", fiber_100g: "", proteins_100g: "" });
  const [showNutrition, setShowNutrition] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const initialText = new URLSearchParams(window.location.search).get("text");
    if (initialText) setText(initialText);
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    const values = Object.fromEntries(Object.entries(nutrition).filter(([, value]) => value !== "").map(([key, value]) => [key, Number(value)]));
    try { const result = await api.analyzeIngredients({ ingredient_text: text, product_name: name || undefined, nutrition_data: values }); rememberScanResult(result); router.push(`/result/?id=${encodeURIComponent(result.scan_id)}`); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not analyze ingredients."); }
    finally { setBusy(false); }
  }

  return <div className="page-shell page-content narrow"><div className="page-heading centered"><p className="eyebrow">Manual checker</p><h1>Paste the ingredient list</h1><p>Copy the exact label text. Unknown or source-dependent ingredients will not be guessed.</p></div><form className="card form-card" onSubmit={submit}><label>Product name <small>(optional)</small><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Example: Chocolate wafer" /></label><label>Ingredients<textarea required minLength={2} rows={8} value={text} onChange={(e) => setText(e.target.value)} placeholder="Sugar, wheat flour, vegetable oil, gelatin, E471…" /></label><button type="button" className="text-button" onClick={() => setShowNutrition((value) => !value)}><FlaskConical size={18} /> {showNutrition ? "Hide" : "Add"} nutrition per 100 g</button>{showNutrition && <div className="nutrition-input-grid"><label>Sugar (g)<input type="number" min="0" step="0.1" value={nutrition.sugars_100g} onChange={(e) => setNutrition({ ...nutrition, sugars_100g: e.target.value })} /></label><label>Saturated fat (g)<input type="number" min="0" step="0.1" value={nutrition.saturated_fat_100g} onChange={(e) => setNutrition({ ...nutrition, saturated_fat_100g: e.target.value })} /></label><label>Sodium (mg)<input type="number" min="0" step="1" value={nutrition.sodium_100g} onChange={(e) => setNutrition({ ...nutrition, sodium_100g: e.target.value })} /></label><label>Fibre (g)<input type="number" min="0" step="0.1" value={nutrition.fiber_100g} onChange={(e) => setNutrition({ ...nutrition, fiber_100g: e.target.value })} /></label><label>Protein (g)<input type="number" min="0" step="0.1" value={nutrition.proteins_100g} onChange={(e) => setNutrition({ ...nutrition, proteins_100g: e.target.value })} /></label></div>}{error && <p className="form-error">{error}</p>}<button className="button full" disabled={busy || text.trim().length < 2}><ListChecks size={19} /> {busy ? "Analyzing…" : "Check ingredients"}</button></form></div>;
}
