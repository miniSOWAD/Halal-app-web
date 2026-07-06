"use client";

import Link from "next/link";
import { Heart } from "lucide-react";
import { useEffect, useState } from "react";

import Loading from "@/components/Loading";
import ProductCard from "@/components/ProductCard";
import { api } from "@/lib/api";
import type { Product } from "@/lib/types";

export default function FavoritesPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => { api.favorites().then(setProducts).catch((reason) => setError(reason instanceof Error ? reason.message : "Sign in to view favorites.")).finally(() => setBusy(false)); }, []);
  return <div className="page-shell page-content"><div className="page-heading"><p className="eyebrow">Saved products</p><h1>Your favorites</h1><p>Keep products that you want to check again later.</p></div>{busy ? <Loading /> : error ? <div className="empty-state"><Heart /><h2>Favorites require sign in</h2><p>{error}</p><Link className="button" href="/login/">Sign in</Link></div> : products.length ? <div className="product-grid">{products.map((product) => <ProductCard product={product} key={product.id} />)}</div> : <div className="empty-state"><Heart /><h2>No saved products</h2><p>Open a scan result and tap Save.</p><Link className="button" href="/search/">Search products</Link></div>}</div>;
}
