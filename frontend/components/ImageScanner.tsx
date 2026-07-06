"use client";

import { Camera, ImageUp, X } from "lucide-react";
import { ChangeEvent, useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { AnalysisResult } from "@/lib/types";

export default function ImageScanner({ onResult }: { onResult: (result: AnalysisResult) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function choose(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0];
    setError("");
    if (!selected) return;
    if (!selected.type.startsWith("image/")) {
      setError("Choose an image file.");
      return;
    }
    if (selected.size > 8 * 1024 * 1024) {
      setError("The image must be smaller than 8 MB.");
      return;
    }
    setFile(selected);
  }

  async function scan() {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      onResult(await api.scanImage(file));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The image could not be analyzed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="scanner-panel">
      <label className={preview ? "image-drop has-image" : "image-drop"}>
        {preview ? (
          <>
            <img src={preview} alt="Selected label" />
            <button type="button" className="remove-image" onClick={(event) => { event.preventDefault(); setFile(null); setPreview(""); }}><X /></button>
          </>
        ) : (
          <><ImageUp size={42} /><strong>Photograph the ingredient label</strong><span>Use a clear, straight image with readable text.</span></>
        )}
        <input type="file" accept="image/*" capture="environment" onChange={choose} />
      </label>
      <button className="button full" onClick={scan} disabled={!file || busy}><Camera size={18} /> {busy ? "Reading label…" : "Scan label"}</button>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
