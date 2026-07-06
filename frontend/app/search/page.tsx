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
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  async function runSearch(value: string) {
    const cleaned = value.trim();
    setQuery(cleaned);
    setBusy(true);
    setError("");
    setSearched(true);
    if (typeof window !== "undefined") {
      window.history.replaceState({}, "", cleaned ? `/search/?q=${encodeURIComponent(cleaned)}` : "/search/");
    }
    try {
      setProducts(await api.searchProducts(cleaned));
    } catch (reason) {
      setProducts([]);
      setError(reason instanceof Error ? reason.message : "Search failed.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    const initial = new URLSearchParams(window.location.search).get("q") ?? "";
    setQuery(initial);
    if (initial) void runSearch(initial);
  }, []);

  return (
    <div className="page-shell page-content">
      <div className="page-heading search-heading">
        <p className="eyebrow">International product database</p>
        <h1>Search food</h1>
        <p>Search by product name, brand, ingredient keyword, E-number or complete barcode.</p>
      </div>
      <SearchBox initialValue={query} large onSearch={runSearch} />
      <div className="search-tips">
        <span>Try “gelatin candy”</span><span>Try “E471”</span><span>Try a barcode</span>
      </div>
      {busy ? (
        <Loading label="Searching Neon and food databases…" />
      ) : error ? (
        <p className="form-error">{error}</p>
      ) : products.length ? (
        <>
          <div className="result-summary"><strong>{products.length}</strong> product{products.length === 1 ? "" : "s"} found</div>
          <div className="product-grid">{products.map((product) => <ProductCard product={product} key={product.id} />)}</div>
        </>
      ) : searched ? (
        <div className="empty-state"><h2>No product found</h2><p>Try another spelling, scan the barcode, or paste the ingredient list.</p></div>
      ) : (
        <div className="search-empty-guide">
          <div><strong>Product name</strong><span>Search common or branded food names.</span></div>
          <div><strong>Ingredient</strong><span>Find products containing a specific ingredient.</span></div>
          <div><strong>Barcode</strong><span>Enter the full EAN, UPC or GTIN number.</span></div>
        </div>
      )}
    </div>
  );
}
