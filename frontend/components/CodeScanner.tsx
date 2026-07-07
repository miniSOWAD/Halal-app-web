"use client";

import { BrowserMultiFormatReader } from "@zxing/browser";
import { BarcodeFormat } from "@zxing/library";
import { Camera, Keyboard, ScanSearch, StopCircle } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";

import { api } from "@/lib/api";
import type { AnalysisResult } from "@/lib/types";

type NativeBarcode = { rawValue: string; format?: string };
type NativeBarcodeDetector = { detect: (source: CanvasImageSource) => Promise<NativeBarcode[]> };
type NativeBarcodeDetectorConstructor = {
  new (options?: { formats?: string[] }): NativeBarcodeDetector;
  getSupportedFormats?: () => Promise<string[]>;
};

declare global {
  interface Window {
    BarcodeDetector?: NativeBarcodeDetectorConstructor;
  }
}

const nativeFormats = [
  "qr_code",
  "ean_13",
  "ean_8",
  "upc_a",
  "upc_e",
  "code_128",
  "code_39",
  "code_93",
  "codabar",
  "itf",
  "data_matrix",
  "pdf417",
];

const videoConstraints: MediaTrackConstraints = {
  facingMode: { ideal: "environment" },
  width: { ideal: 1920 },
  height: { ideal: 1080 },
  aspectRatio: { ideal: 1.777777778 },
  advanced: [{ focusMode: "continuous" } as MediaTrackConstraintSet],
};

function normalizeFormat(format?: string) {
  return (format || "UNKNOWN").toUpperCase().replaceAll("-", "_");
}

function zxingFormatName(format: BarcodeFormat) {
  return BarcodeFormat[format] ?? "UNKNOWN";
}

export default function CodeScanner({ onResult }: { onResult: (result: AnalysisResult) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const controlsRef = useRef<{ stop: () => void } | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number | null>(null);
  const scanLockedRef = useRef(false);
  const busyRef = useRef(false);
  const [running, setRunning] = useState(false);
  const [manualCode, setManualCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Ready for barcode, QR code, product URL or certificate number.");

  useEffect(() => {
    busyRef.current = busy;
  }, [busy]);

  useEffect(() => () => stopCamera(), []);

  function cleanupCamera() {
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    controlsRef.current?.stop();
    controlsRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
  }

  function stopCamera() {
    cleanupCamera();
    setRunning(false);
    scanLockedRef.current = false;
    if (!busyRef.current) setStatus("Scanner stopped. Start the camera again when you are ready.");
  }

  async function submitCode(code: string, format = "UNKNOWN", fromCamera = false) {
    const cleaned = code.trim();
    if (!cleaned || busyRef.current || scanLockedRef.current) return;
    scanLockedRef.current = true;
    setBusy(true);
    setError("");
    setStatus(fromCamera ? "Code detected. Loading product details…" : "Checking product details…");
    if (fromCamera) cleanupCamera();
    setRunning(false);

    try {
      const result = await api.scanCode(cleaned, normalizeFormat(format));
      onResult(result);
    } catch (reason) {
      scanLockedRef.current = false;
      setStatus("Scan failed. Try again, move closer, or type the code manually.");
      setError(reason instanceof Error ? reason.message : "The code could not be checked.");
    } finally {
      setBusy(false);
    }
  }

  async function startNativeScanner() {
    const video = videoRef.current;
    if (!video || !window.BarcodeDetector || !navigator.mediaDevices?.getUserMedia) return false;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: false, video: videoConstraints });
    streamRef.current = stream;
    video.srcObject = stream;
    video.setAttribute("playsinline", "true");
    video.muted = true;
    await video.play();

    let formats = nativeFormats;
    if (window.BarcodeDetector.getSupportedFormats) {
      const supported = await window.BarcodeDetector.getSupportedFormats();
      formats = nativeFormats.filter((format) => supported.includes(format));
      if (!formats.length) {
        cleanupCamera();
        return false;
      }
    }

    let detector: NativeBarcodeDetector;
    try {
      detector = new window.BarcodeDetector({ formats });
    } catch {
      cleanupCamera();
      return false;
    }

    let lastScan = 0;

    const scan = async (time: number) => {
      if (!streamRef.current || scanLockedRef.current) return;
      if (time - lastScan > 90 && video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
        lastScan = time;
        try {
          const hits = await detector.detect(video);
          const first = hits.find((hit) => hit.rawValue?.trim());
          if (first) {
            void submitCode(first.rawValue, first.format, true);
            return;
          }
        } catch {
          // Native detector can fail on a frame while the camera is settling. Keep scanning.
        }
      }
      rafRef.current = requestAnimationFrame(scan);
    };

    rafRef.current = requestAnimationFrame(scan);
    controlsRef.current = { stop: cleanupCamera };
    return true;
  }

  async function startZxingScanner() {
    const reader = new BrowserMultiFormatReader();
    const controls = await (reader as unknown as {
      decodeFromConstraints: (
        constraints: MediaStreamConstraints,
        previewElem: HTMLVideoElement,
        callbackFn: (result?: { getText: () => string; getBarcodeFormat: () => BarcodeFormat } | null) => void
      ) => Promise<{ stop: () => void }>;
    }).decodeFromConstraints({ audio: false, video: videoConstraints }, videoRef.current!, (result) => {
      if (result) void submitCode(result.getText(), zxingFormatName(result.getBarcodeFormat()), true);
    });
    controlsRef.current = controls;
  }

  async function startCamera() {
    setError("");
    setStatus("Starting rear camera…");
    setRunning(true);
    scanLockedRef.current = false;
    try {
      let nativeStarted = false;
      try {
        nativeStarted = await startNativeScanner();
      } catch {
        cleanupCamera();
      }
      if (nativeStarted) {
        setStatus("Fast scanner active. Fill the guide box with the QR or barcode.");
        return;
      }
      await startZxingScanner();
      setStatus("Scanner active. Fill the guide box with the QR or barcode.");
    } catch (reason) {
      cleanupCamera();
      setRunning(false);
      setStatus("Camera is not running.");
      setError(reason instanceof Error ? reason.message : "Camera access failed.");
    }
  }

  function manualSubmit(event: FormEvent) {
    event.preventDefault();
    void submitCode(manualCode, "MANUAL");
  }

  return (
    <div className="scanner-panel">
      <div className={running ? "camera-frame active" : "camera-frame"}>
        <video ref={videoRef} muted playsInline />
        {!running && !busy && (
          <div className="camera-placeholder">
            <Camera size={42} />
            <p>Point the rear camera at a barcode or QR code.</p>
            <span>Small code? Move closer slowly and keep the package flat.</span>
          </div>
        )}
        {running && (
          <>
            <div className="scan-target" />
            <div className="scan-line" />
          </>
        )}
        {busy && (
          <div className="scanner-busy">
            <ScanSearch size={28} />
            <span>Loading result…</span>
          </div>
        )}
      </div>
      <p className="scanner-status">{status}</p>
      <div className="scanner-tips" aria-label="Scanning tips">
        <span>Rear camera</span>
        <span>Fast native detection</span>
        <span>Barcode + QR</span>
      </div>
      <div className="button-row">
        {!running ? (
          <button className="button" onClick={startCamera} disabled={busy}><Camera size={18} /> Start fast scan</button>
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
