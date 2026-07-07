import type { AnalysisResult } from "@/lib/types";

const PREFIX = "halalfit:scan-result:";
const MAX_CACHE_ITEMS = 8;

function cacheKey(id: string) {
  return `${PREFIX}${id}`;
}

export function rememberScanResult(result: AnalysisResult) {
  if (typeof window === "undefined" || !result.scan_id) return;
  try {
    sessionStorage.setItem(cacheKey(result.scan_id), JSON.stringify(result));
    const keys = Object.keys(sessionStorage).filter((key) => key.startsWith(PREFIX));
    keys
      .sort((a, b) => {
        const left = JSON.parse(sessionStorage.getItem(a) || "{}").created_at || "";
        const right = JSON.parse(sessionStorage.getItem(b) || "{}").created_at || "";
        return right.localeCompare(left);
      })
      .slice(MAX_CACHE_ITEMS)
      .forEach((key) => sessionStorage.removeItem(key));
  } catch {
    // Session storage may be unavailable in private or restricted browser modes.
  }
}

export function readCachedScanResult(id: string): AnalysisResult | null {
  if (typeof window === "undefined" || !id) return null;
  try {
    const raw = sessionStorage.getItem(cacheKey(id));
    return raw ? (JSON.parse(raw) as AnalysisResult) : null;
  } catch {
    return null;
  }
}
