import Link from "next/link";
import { ArrowRight, Camera, HeartPulse, ListChecks, ScanBarcode, ShieldCheck } from "lucide-react";

import SearchBox from "@/components/SearchBox";

export default function HomePage() {
  return (
    <div>
      <section className="hero page-shell">
        <div className="hero-copy">
          <p className="eyebrow light">Eat halal. Eat healthy. Eat with confidence.</p>
          <h1>Know what is inside your food before you eat it.</h1>
          <p className="hero-text">Search a product, paste ingredients, scan a barcode or photograph a food label. HalalFit gives separate halal and nutrition results with clear reasons.</p>
          <SearchBox large />
          <div className="hero-actions">
            <Link className="button peach" href="/scan/"><ScanBarcode size={19} /> Scan a product</Link>
            <Link className="button outline-light" href="/ingredients/"><ListChecks size={19} /> Check ingredients</Link>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="phone-card">
            <div className="phone-top"><span /><span /><span /></div>
            <div className="mini-product"><ShieldCheck size={38} /><div><small>Chocolate wafer</small><strong>Doubtful / Mushbooh</strong></div></div>
            <div className="mini-score"><div><b>68%</b><span>Halal confidence</span></div><div><b>34</b><span>Health score</span></div></div>
            <div className="mini-warning">E471 source needs verification</div>
          </div>
          <div className="floating-badge badge-one"><Camera /> Label OCR</div>
          <div className="floating-badge badge-two"><HeartPulse /> Health score</div>
        </div>
      </section>

      <section className="page-shell section-block">
        <div className="section-heading centered">
          <div><p className="eyebrow">Four ways to check</p><h2>Use the information available on the package</h2></div>
        </div>
        <div className="feature-grid">
          <Link className="feature-card" href="/search/"><SearchIcon /><h3>Search by name</h3><p>Find products, brands and ingredients already stored in the database.</p><span>Start searching <ArrowRight size={16} /></span></Link>
          <Link className="feature-card" href="/ingredients/"><ListChecks /><h3>Paste ingredients</h3><p>Check each ingredient and identify prohibited, doubtful or unknown items.</p><span>Check a list <ArrowRight size={16} /></span></Link>
          <Link className="feature-card" href="/scan/"><Camera /><h3>Photograph a label</h3><p>OCR reads the ingredient and nutrition label, then sends the text to the rules engine.</p><span>Use camera <ArrowRight size={16} /></span></Link>
          <Link className="feature-card" href="/scan/"><ScanBarcode /><h3>Scan barcode or QR</h3><p>Look up the product, certificate number or supported product URL.</p><span>Open scanner <ArrowRight size={16} /></span></Link>
        </div>
      </section>

      <section className="principle-section">
        <div className="page-shell principle-grid">
          <div><p className="eyebrow light">Two separate answers</p><h2>Halal does not automatically mean healthy.</h2><p>HalalFit avoids one confusing verdict. It checks religious permissibility and nutrition quality independently.</p></div>
          <div className="principle-cards"><div><ShieldCheck /><strong>Halal result</strong><span>Certified, no prohibited ingredient found, doubtful, haram or unknown.</span></div><div><HeartPulse /><strong>Health result</strong><span>Score from available sugar, salt, fat, fibre, protein and ingredient data.</span></div></div>
        </div>
      </section>
    </div>
  );
}

function SearchIcon() {
  return <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>;
}
