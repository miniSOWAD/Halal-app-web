import Link from "next/link";
import {
  ArrowRight,
  BadgeCheck,
  Camera,
  CheckCircle2,
  Clock3,
  Database,
  FileSearch,
  Globe2,
  HeartPulse,
  ListChecks,
  ScanBarcode,
  Search,
  ShieldCheck,
  Sparkles,
  Utensils,
} from "lucide-react";

import SearchBox from "@/components/SearchBox";

export default function HomePage() {
  return (
    <div>
      <section className="hero page-shell compact-hero">
        <div className="hero-copy">
          <p className="eyebrow light">Eat halal. Eat healthy. Eat with confidence.</p>
          <h1>Check food before it reaches your plate.</h1>
          <p className="hero-text">
            Scan a barcode or QR code, search by product name, photograph a label, or paste ingredients. HalalFit separates halal status from nutrition quality and explains every warning.
          </p>
          <SearchBox large />
          <div className="hero-actions">
            <Link className="button peach" href="/scan/"><ScanBarcode size={19} /> Fast scan</Link>
            <Link className="button outline-light" href="/ingredients/"><ListChecks size={19} /> Check ingredients</Link>
          </div>
          <div className="hero-data-row">
            <div><strong>4</strong><span>check modes</span></div>
            <div><strong>2</strong><span>separate verdicts</span></div>
            <div><strong>100</strong><span>health score scale</span></div>
          </div>
          <div className="hero-trust-row">
            <span><CheckCircle2 /> Halal + health shown separately</span>
            <span><CheckCircle2 /> Neon product history</span>
            <span><CheckCircle2 /> Explainable results</span>
          </div>
        </div>
        <div className="hero-visual dense" aria-hidden="true">
          <div className="phone-card dense-card">
            <div className="phone-top"><span /><span /><span /></div>
            <div className="mini-product"><ShieldCheck size={34} /><div><small>Chocolate wafer</small><strong>Doubtful / Mushbooh</strong></div></div>
            <div className="mini-score"><div><b>68%</b><span>Halal confidence</span></div><div><b>34</b><span>Health score</span></div></div>
            <div className="mini-warning">E471 source needs verification</div>
            <div className="mini-list"><span>High added sugar</span><span>No active certificate found</span><span>Lower-sugar alternative suggested</span></div>
          </div>
          <div className="hero-mini-panel panel-top"><ScanBarcode /><strong>Fast scanner</strong><span>QR, EAN, UPC, Code 128</span></div>
          <div className="hero-mini-panel panel-bottom"><HeartPulse /><strong>Nutrition logic</strong><span>Sugar, salt, fat, fibre, protein</span></div>
        </div>
      </section>

      <section className="quick-stats page-shell" aria-label="HalalFit capabilities">
        <div><Globe2 /><strong>International lookup</strong><span>Local Neon first, external data when needed</span></div>
        <div><Database /><strong>Editable database</strong><span>Products, ingredients, rules and certificates</span></div>
        <div><BadgeCheck /><strong>Transparent verdicts</strong><span>Confidence, reasons and certificate info</span></div>
        <div><Sparkles /><strong>Practical guidance</strong><span>Warnings, alternatives and scan history</span></div>
      </section>

      <section className="home-control-panel page-shell" aria-label="HalalFit data and checks">
        <div className="control-card wide">
          <div><p className="eyebrow">After each scan</p><h2>Everything shown in one result page</h2></div>
          <div className="result-preview-grid">
            <span><ShieldCheck /> Halal label</span>
            <span><HeartPulse /> Health score</span>
            <span><FileSearch /> Ingredient breakdown</span>
            <span><BadgeCheck /> Certificate status</span>
            <span><Utensils /> Better choices</span>
            <span><Clock3 /> Saved history</span>
          </div>
        </div>
        <div className="control-card">
          <Camera />
          <strong>Small-code scanning</strong>
          <span>Uses a high-resolution rear-camera stream and native detection where the phone supports it.</span>
        </div>
        <div className="control-card">
          <Database />
          <strong>Cloud data flow</strong>
          <span>Frontend calls FastAPI; FastAPI reads and writes Neon PostgreSQL through SQLAlchemy.</span>
        </div>
        <div className="control-card">
          <ListChecks />
          <strong>Ingredient matching</strong>
          <span>Known, unknown, doubtful and source-dependent items are separated clearly.</span>
        </div>
        <div className="control-card">
          <Search />
          <strong>Product search</strong>
          <span>Search name, brand, category, barcode or ingredient text before buying.</span>
        </div>
      </section>

      <section className="page-shell section-block compact-section">
        <div className="section-heading centered"><div><p className="eyebrow">Four ways to check</p><h2>Use whatever information is available</h2><p className="section-intro">Every check uses the same backend analysis engine, so results stay consistent whether you type, scan or upload.</p></div></div>
        <div className="feature-grid dense-grid">
          <Link className="feature-card compact" href="/search/"><Search /><h3>Search by name</h3><p>Find products, brands and ingredients stored in Neon or imported from food databases.</p><span>Start searching <ArrowRight size={16} /></span></Link>
          <Link className="feature-card compact" href="/ingredients/"><ListChecks /><h3>Paste ingredients</h3><p>Check each ingredient and highlight prohibited, doubtful or unknown items.</p><span>Check a list <ArrowRight size={16} /></span></Link>
          <Link className="feature-card compact" href="/scan/"><Camera /><h3>Photograph a label</h3><p>OCR reads package text so the backend can analyze ingredients and nutrition facts.</p><span>Use camera <ArrowRight size={16} /></span></Link>
          <Link className="feature-card compact" href="/scan/"><ScanBarcode /><h3>Scan barcode or QR</h3><p>Identify a product, certificate number or supported product link in seconds.</p><span>Open scanner <ArrowRight size={16} /></span></Link>
        </div>
      </section>

      <section className="how-section compact-how">
        <div className="page-shell">
          <div className="section-heading"><div><p className="eyebrow">Simple workflow</p><h2>From package to clear result</h2></div></div>
          <div className="steps-grid dense-steps">
            <div><span>01</span><h3>Provide food information</h3><p>Search, scan, upload a label, or paste ingredients.</p></div>
            <div><span>02</span><h3>Analyze the evidence</h3><p>The backend checks ingredient rules, product data, certificates and nutrition values.</p></div>
            <div><span>03</span><h3>See two verdicts</h3><p>Halal status and health status are displayed separately with confidence and reasons.</p></div>
          </div>
        </div>
      </section>

      <section className="principle-section compact-principle">
        <div className="page-shell principle-grid">
          <div><p className="eyebrow light">Two separate answers</p><h2>Halal does not automatically mean healthy.</h2><p>HalalFit avoids one confusing score. Religious permissibility and nutrition quality are evaluated independently.</p><Link href="/about/" className="button peach">Read our method <ArrowRight size={17} /></Link></div>
          <div className="principle-cards"><div><ShieldCheck /><strong>Halal result</strong><span>Certified halal, no prohibited ingredient found, doubtful, haram or unknown.</span></div><div><HeartPulse /><strong>Health result</strong><span>A score based on available sugar, salt, fat, fibre, protein and ingredient data.</span></div></div>
        </div>
      </section>

      <section className="page-shell category-strip" aria-label="Common product checks">
        <span>Snacks</span><span>Chocolate</span><span>Instant noodles</span><span>Drinks</span><span>Biscuits</span><span>Supplements</span><span>Sauces</span><span>Frozen food</span>
      </section>

      <section className="page-shell section-block cta-section compact-cta">
        <div><p className="eyebrow">Ready to check?</p><h2>Make your next food choice with more information.</h2><p>Start with a product name, barcode, QR code or ingredient list.</p></div>
        <div className="button-row"><Link className="button" href="/search/">Search products</Link><Link className="button secondary" href="/register/">Create free account</Link></div>
      </section>
    </div>
  );
}
