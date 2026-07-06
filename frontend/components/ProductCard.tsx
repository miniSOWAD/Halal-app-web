import Link from "next/link";
import { ChevronRight, ShieldCheck } from "lucide-react";

import type { Product } from "@/lib/types";

function statusClass(status: string) {
  if (status === "CERTIFIED_HALAL" || status === "NO_PROHIBITED_INGREDIENT_FOUND" || status === "HEALTHY") return "good";
  if (status === "HARAM" || status === "UNHEALTHY") return "bad";
  if (status === "DOUBTFUL" || status === "MODERATE") return "warn";
  return "neutral";
}

function label(status: string) {
  return status.replaceAll("_", " ").toLowerCase().replace(/^\w/, (letter) => letter.toUpperCase());
}

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link className="product-card" href={`/product/?id=${product.id}`}>
      <div className="product-image">
        {product.image_url ? <img src={product.image_url} alt="" /> : <ShieldCheck size={34} />}
      </div>
      <div className="product-card-body">
        <p className="eyebrow">{product.brand || "Unbranded"}</p>
        <h3>{product.name}</h3>
        <div className="status-row">
          <span className={`status-pill ${statusClass(product.halal_status)}`}>{label(product.halal_status)}</span>
          <span className={`status-pill ${statusClass(product.health_status)}`}>{product.health_score}/100</span>
        </div>
      </div>
      <ChevronRight className="card-arrow" />
    </Link>
  );
}
