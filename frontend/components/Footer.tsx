import Link from "next/link";
import { HeartPulse, Mail, ScanLine, ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="page-shell footer-grid">
        <div className="footer-brand">
          <Link className="brand footer-logo" href="/">
            <span className="brand-mark">H</span>
            <span><strong>HalalFit</strong><small>Know what you eat.</small></span>
          </Link>
          <p>A transparent food assistant that separates halal screening from nutrition quality.</p>
          <div className="footer-badges"><span><ShieldCheck /> Evidence-led</span><span><HeartPulse /> Health-aware</span></div>
        </div>
        <div>
          <h3>Check food</h3>
          <Link href="/search/">Search products</Link>
          <Link href="/scan/">Scan barcode or QR</Link>
          <Link href="/ingredients/">Check ingredients</Link>
          <Link href="/history/">Scan history</Link>
        </div>
        <div>
          <h3>Company</h3>
          <Link href="/about/">About us</Link>
          <Link href="/contact/">Contact us</Link>
          <Link href="/favorites/">Saved products</Link>
          <Link href="/profile/">Account settings</Link>
        </div>
        <div>
          <h3>Important</h3>
          <p>HalalFit provides ingredient and certificate information, not a religious ruling or medical diagnosis.</p>
          <a className="footer-contact" href="mailto:baisakh2015@gmail.com"><Mail /> baisakh2015@gmail.com</a>
        </div>
      </div>
      <div className="footer-bottom page-shell">
        <span>© {new Date().getFullYear()} HalalFit. All rights reserved.</span>
        <span><ScanLine size={15} /> Built for web and Android</span>
      </div>
    </footer>
  );
}
