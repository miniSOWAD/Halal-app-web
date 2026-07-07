"use client";

import { useEffect, useState } from "react";

import Loading from "@/components/Loading";
import ScanResult from "@/components/ScanResult";
import { api } from "@/lib/api";
import { readCachedScanResult, rememberScanResult } from "@/lib/scan-cache";
import type { AnalysisResult } from "@/lib/types";

export default function ResultPage() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("id");
    if (!id) {
      setError("Scan ID is missing.");
      return;
    }

    const cached = readCachedScanResult(id);
    if (cached) setResult(cached);

    api.getScan(id)
      .then((fresh) => {
        rememberScanResult(fresh);
        setResult(fresh);
        setError("");
      })
      .catch((reason) => {
        if (!cached) setError(reason instanceof Error ? reason.message : "Could not load the result.");
      });
  }, []);

  return <div className="page-shell page-content result-page">{error ? <p className="form-error">{error}</p> : result ? <ScanResult result={result} /> : <Loading label="Loading analysis…" />}</div>;
}
