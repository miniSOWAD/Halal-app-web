import Link from "next/link";
import {
  ArrowRight,
  BadgeCheck,
  Camera,
  CheckCircle2,
  Database,
  Globe2,
  HeartPulse,
  ListChecks,
  ScanBarcode,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import SearchBox from "@/components/SearchBox";

export default function HomePage() {
  return (
    <div>
      <section className="hero page-shell">
        <div className="hero-copy">
          <p className="eyebrow light">Eat halal. Eat healthy. Eat with confidence.</p>
          <h1>Understand your food before it reaches your plate.</h1>
          <p className="hero-text">
            Search products, scan a barcode or QR code, photograph an ingredient label, or paste ingredients. HalalFit gives separate halal and nutrition results with clear reasons.
          </p>
          <SearchBox large />
          <div className="hero-actions">
            <Link className="button peach" href="/scan/"><ScanBarcode size={19} /> Scan a product</Link>
            <Link className="button outline-light" href="/ingredients/"><ListChecks size={19} /> Check ingredients</Link>
          </div>
          <div className="hero-trust-row">
            <span><CheckCircle2 /> Separate halal and health results</span>
            <span><CheckCircle2 /> International product lookup</span>
            <span><CheckCircle2 /> Explainable warnings</span>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="phone-card">
            <div className="phone-top"><span /><span /><span /></div>
            <div className="mini-product"><ShieldCheck size={38} /><div><small>Chocolate wafer</small><strong>Doubtful / Mushbooh</strong></div></div>
            <div className="mini-score"><div><b>68%</b><span>Halal confidence</span></div><div><b>34</b><span>Health score</span></div></div>
            <div className="mini-warning">E471 source needs verification</div>
            <div className="mini-list"><span>High added sugar</span><span>No active certificate found</span><span>Choose a lower-sugar alternative</span></div>
          </div>
          <div className="floating-badge badge-one"><Camera /> Label OCR</div>
          <div className="floating-badge badge-two"><HeartPulse /> Health score</div>
        </div>
      </section>

      <section className="quick-stats page-shell" aria-label="HalalFit capabilities">
        <div><Globe2 /><strong>International</strong><span>Search products across markets</span></div>
        <div><Database /><strong>Evidence-based</strong><span>Rules, ingredients and certificates</span></div>
        <div><BadgeCheck /><strong>Transparent</strong><span>Reasons and confidence shown</span></div>
        <div><Sparkles /><strong>Practical</strong><span>Better alternatives suggested</span></div>
      </section>

      <section className="page-shell section-block">
        <div className="section-heading centered"><div><p className="eyebrow">Four ways to check</p><h2>Use whatever information is available</h2><p className="section-intro">Every check uses the same analysis engine, so results stay consistent whether you type, scan or upload.</p></div></div>
        <div className="feature-grid">
          <Link className="feature-card" href="/search/"><Search /><h3>Search by name</h3><p>Find products, brands and ingredients stored in Neon or imported from food databases.</p><span>Start searching <ArrowRight size={16} /></span></Link>
          <Link className="feature-card" href="/ingredients/"><ListChecks /><h3>Paste ingredients</h3><p>Check each ingredient and highlight prohibited, doubtful or unknown items.</p><span>Check a list <ArrowRight size={16} /></span></Link>
          <Link className="feature-card" href="/scan/"><Camera /><h3>Photograph a label</h3><p>OCR reads package text so the backend can analyze ingredients and nutrition facts.</p><span>Use camera <ArrowRight size={16} /></span></Link>
          <Link className="feature-card" href="/scan/"><ScanBarcode /><h3>Scan barcode or QR</h3><p>Identify a product, certificate number or supported product link in seconds.</p><span>Open scanner <ArrowRight size={16} /></span></Link>
        </div>
      </section>

      <section className="how-section">
        <div className="page-shell">
          <div className="section-heading"><div><p className="eyebrow">Simple workflow</p><h2>From package to clear result</h2></div></div>
          <div className="steps-grid">
            <div><span>01</span><h3>Provide food information</h3><p>Search, scan, upload a label, or paste ingredients.</p></div>
            <div><span>02</span><h3>Analyze the evidence</h3><p>The backend checks ingredient rules, product data, certificates and nutrition values.</p></div>
            <div><span>03</span><h3>See two verdicts</h3><p>Halal status and health status are displayed separately with confidence and reasons.</p></div>
          </div>
        </div>
      </section>

      <section className="principle-section">
        <div className="page-shell principle-grid">
          <div><p className="eyebrow light">Two separate answers</p><h2>Halal does not automatically mean healthy.</h2><p>HalalFit avoids one confusing score. Religious permissibility and nutrition quality are evaluated independently.</p><Link href="/about/" className="button peach">Read our method <ArrowRight size={17} /></Link></div>
          <div className="principle-cards"><div><ShieldCheck /><strong>Halal result</strong><span>Certified halal, no prohibited ingredient found, doubtful, haram or unknown.</span></div><div><HeartPulse /><strong>Health result</strong><span>A score based on available sugar, salt, fat, fibre, protein and ingredient data.</span></div></div>
        </div>
      </section>

      <section className="page-shell section-block cta-section">
        <div><p className="eyebrow">Ready to check?</p><h2>Make your next food choice with more information.</h2><p>Start with a product name, barcode, QR code or ingredient list.</p></div>
        <div className="button-row"><Link className="button" href="/search/">Search products</Link><Link className="button secondary" href="/register/">Create free account</Link></div>
      </section>
    </div>
  );
}
