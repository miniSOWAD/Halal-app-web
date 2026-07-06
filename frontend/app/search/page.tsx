"use client";

import { useEffect, useState } from "react";

import Loading from "@/components/Loading";
import ProductCard from "@/components/ProductCard";
import SearchBox from "@/components/SearchBox";
import { api } from "@/lib/api";
import type { Product } from "@/lib/types";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const value = new URLSearchParams(window.location.search).get("q") ?? "";
    setQuery(value);
    setBusy(true);
    api.searchProducts(value).then(setProducts).catch((reason) => setError(reason instanceof Error ? reason.message : "Search failed.")).finally(() => setBusy(false));
  }, []);

  return <div className="page-shell page-content"><div className="page-heading"><p className="eyebrow">Product database</p><h1>Search food</h1><p>Search products, brands, ingredients or enter a complete barcode.</p></div><SearchBox initialValue={query} large />{busy ? <Loading label="Searching products…" /> : error ? <p className="form-error">{error}</p> : products.length ? <div className="product-grid">{products.map((product) => <ProductCard product={product} key={product.id} />)}</div> : <div className="empty-state"><h2>No product found</h2><p>Try a barcode scan or paste the ingredient list.</p></div>}</div>;
}
