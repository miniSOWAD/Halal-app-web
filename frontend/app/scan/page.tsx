"use client";

import { Camera, ScanBarcode } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import CodeScanner from "@/components/CodeScanner";
import ImageScanner from "@/components/ImageScanner";
import type { AnalysisResult } from "@/lib/types";

export default function ScanPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"code" | "image">("code");
  function done(result: AnalysisResult) { router.push(`/result/?id=${result.scan_id}`); }
  return <div className="page-shell page-content narrow"><div className="page-heading centered"><p className="eyebrow">Camera scanner</p><h1>Scan a product</h1><p>Use a barcode or QR code, or photograph the ingredient and nutrition label.</p></div><div className="segmented"><button className={mode === "code" ? "active" : ""} onClick={() => setMode("code")}><ScanBarcode /> Barcode or QR</button><button className={mode === "image" ? "active" : ""} onClick={() => setMode("image")}><Camera /> Label image</button></div>{mode === "code" ? <CodeScanner onResult={done} /> : <ImageScanner onResult={done} />}</div>;
}
