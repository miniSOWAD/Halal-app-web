import Link from "next/link";
import { Database, Globe2, HeartPulse, Scale, ShieldCheck } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="page-shell page-content">
      <div className="about-hero">
        <p className="eyebrow">About HalalFit</p>
        <h1>A clearer way to understand packaged food.</h1>
        <p>HalalFit is designed for Muslims and health-conscious users who want transparent ingredient, certification and nutrition information before choosing a product.</p>
      </div>
      <section className="about-grid">
        <div className="card"><ShieldCheck /><h2>Our halal approach</h2><p>We use halal, haram, doubtful and unknown states. We do not claim official certification unless certificate evidence is available.</p></div>
        <div className="card"><HeartPulse /><h2>Our health approach</h2><p>Nutrition quality is scored separately using available sugar, sodium, saturated fat, fibre, protein and other label values.</p></div>
        <div className="card"><Database /><h2>Our data approach</h2><p>Products can come from the HalalFit database, trusted administrator entries and external food databases. Sources may be incomplete, so confidence is shown.</p></div>
        <div className="card"><Globe2 /><h2>International by design</h2><p>The app supports products from different countries and avoids assuming that one certification authority represents every market.</p></div>
      </section>
      <section className="card methodology-card"><Scale /><div><p className="eyebrow">Important limitation</p><h2>Food-label analysis is information, not a fatwa or diagnosis.</h2><p>A package image cannot always prove slaughter method, cross-contamination, processing aids or complete supply-chain details. Medical decisions should be discussed with a qualified professional.</p><Link className="button" href="/contact/">Contact the team</Link></div></section>
    </div>
  );
}
