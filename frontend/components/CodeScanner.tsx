"use client";

import { BrowserMultiFormatReader } from "@zxing/browser";
import { BarcodeFormat } from "@zxing/library";
import { Camera, Keyboard, StopCircle } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";

import { api } from "@/lib/api";
import type { AnalysisResult } from "@/lib/types";

export default function CodeScanner({ onResult }: { onResult: (result: AnalysisResult) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const controlsRef = useRef<{ stop: () => void } | null>(null);
  const [running, setRunning] = useState(false);
  const [manualCode, setManualCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => () => controlsRef.current?.stop(), []);

  async function submitCode(code: string, format = "UNKNOWN") {
    if (!code.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const result = await api.scanCode(code.trim(), format);
      controlsRef.current?.stop();
      setRunning(false);
      onResult(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The code could not be checked.");
    } finally {
      setBusy(false);
    }
  }

  async function startCamera() {
    setError("");
    setRunning(true);
    try {
      const reader = new BrowserMultiFormatReader();
      const controls = await reader.decodeFromVideoDevice(undefined, videoRef.current!, (result) => {
        if (result) void submitCode(result.getText(), BarcodeFormat[result.getBarcodeFormat()] ?? "UNKNOWN");
      });
      controlsRef.current = controls;
    } catch (reason) {
      setRunning(false);
      setError(reason instanceof Error ? reason.message : "Camera access failed.");
    }
  }

  function stopCamera() {
    controlsRef.current?.stop();
    controlsRef.current = null;
    setRunning(false);
  }

  function manualSubmit(event: FormEvent) {
    event.preventDefault();
    void submitCode(manualCode, "MANUAL");
  }

  return (
    <div className="scanner-panel">
      <div className={running ? "camera-frame active" : "camera-frame"}>
        <video ref={videoRef} muted playsInline />
        {!running && <div className="camera-placeholder"><Camera size={42} /><p>Point the camera at a barcode or QR code.</p></div>}
        {running && <div className="scan-line" />}
      </div>
      <div className="button-row">
        {!running ? (
          <button className="button" onClick={startCamera} disabled={busy}><Camera size={18} /> Start camera</button>
        ) : (
          <button className="button secondary" onClick={stopCamera}><StopCircle size={18} /> Stop</button>
        )}
      </div>
      <div className="divider"><span>or type the code</span></div>
      <form className="inline-form" onSubmit={manualSubmit}>
        <Keyboard size={20} />
        <input value={manualCode} onChange={(event) => setManualCode(event.target.value)} placeholder="Barcode, certificate number or QR URL" />
        <button className="button" disabled={busy || !manualCode.trim()}>{busy ? "Checking…" : "Check"}</button>
      </form>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
