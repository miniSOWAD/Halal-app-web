import { getAccessToken } from "@/lib/storage";
import type {
  AdminDashboard,
  AnalysisResult,
  AuthResponse,
  Certification,
  HistoryItem,
  Ingredient,
  OTPResponse,
  PasswordResetToken,
  Product,
  Report,
  User,
} from "@/lib/types";

function normalizeApiUrl(rawUrl?: string): string {
  const value = (rawUrl || "http://localhost:8000/api").trim().replace(/\/+$/, "");
  return value.endsWith("/api") ? value : `${value}/api`;
}

export const API_URL = normalizeApiUrl(process.env.NEXT_PUBLIC_API_URL);

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join(", ");
    }
  } catch {
    // Ignore invalid error bodies.
  }
  return `Request failed (${response.status})`;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getAccessToken();
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers, mode: "cors" });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Network request failed";
    throw new Error(`Could not reach the HalalFit API at ${API_URL}. ${message}`);
  }

  if (!response.ok) throw new Error(await parseError(response));
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  registerSendOtp: (payload: { name: string; email: string; password: string; country?: string; phone?: string }) =>
    apiFetch<OTPResponse>("/auth/register/send-otp", { method: "POST", body: JSON.stringify(payload) }),
  registerResendOtp: (email: string) =>
    apiFetch<OTPResponse>("/auth/register/resend-otp", { method: "POST", body: JSON.stringify({ email }) }),
  registerVerifyOtp: (email: string, otp: string) =>
    apiFetch<AuthResponse>("/auth/register/verify-otp", { method: "POST", body: JSON.stringify({ email, otp }) }),
  login: (payload: { email: string; password: string }) =>
    apiFetch<AuthResponse>("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  forgotPasswordSendOtp: (email: string) =>
    apiFetch<OTPResponse>("/auth/forgot-password/send-otp", { method: "POST", body: JSON.stringify({ email }) }),
  forgotPasswordResendOtp: (email: string) =>
    apiFetch<OTPResponse>("/auth/forgot-password/resend-otp", { method: "POST", body: JSON.stringify({ email }) }),
  forgotPasswordVerifyOtp: (email: string, otp: string) =>
    apiFetch<PasswordResetToken>("/auth/forgot-password/verify-otp", { method: "POST", body: JSON.stringify({ email, otp }) }),
  resetPassword: (resetToken: string, newPassword: string) =>
    apiFetch<{ message: string }>("/auth/forgot-password/reset", {
      method: "POST",
      body: JSON.stringify({ reset_token: resetToken, new_password: newPassword }),
    }),
  me: () => apiFetch<User>("/auth/me"),
  updateMe: (payload: { name?: string; country?: string; phone?: string }) =>
    apiFetch<User>("/auth/me", { method: "PATCH", body: JSON.stringify(payload) }),
  changePassword: (oldPassword: string, newPassword: string) =>
    apiFetch<{ message: string }>("/auth/password/change", {
      method: "POST",
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    }),
  emailChangeSendOtp: (newEmail: string) =>
    apiFetch<OTPResponse>("/auth/email-change/send-otp", { method: "POST", body: JSON.stringify({ new_email: newEmail }) }),
  emailChangeResendOtp: (newEmail: string) =>
    apiFetch<OTPResponse>("/auth/email-change/resend-otp", { method: "POST", body: JSON.stringify({ new_email: newEmail }) }),
  emailChangeVerifyOtp: (newEmail: string, otp: string) =>
    apiFetch<AuthResponse>("/auth/email-change/verify-otp", {
      method: "POST",
      body: JSON.stringify({ new_email: newEmail, otp }),
    }),

  searchProducts: (query: string) => apiFetch<Product[]>(`/products/search?q=${encodeURIComponent(query)}`),
  getProduct: (id: string) => apiFetch<Product>(`/products/${id}`),
  createProduct: (payload: Record<string, unknown>) =>
    apiFetch<Product>("/products", { method: "POST", body: JSON.stringify(payload) }),
  updateProduct: (id: string, payload: Record<string, unknown>) =>
    apiFetch<Product>(`/products/${id}`, { method: "PUT", body: JSON.stringify(payload) }),

  analyzeIngredients: (payload: {
    ingredient_text: string;
    nutrition_data?: Record<string, number>;
    product_name?: string;
    country?: string;
  }) => apiFetch<AnalysisResult>("/analyze/ingredients", { method: "POST", body: JSON.stringify(payload) }),
  scanCode: (code: string, format: string) =>
    apiFetch<AnalysisResult>("/scan/code", { method: "POST", body: JSON.stringify({ code, format }) }),
  scanImage: async (file: File) => {
    const body = new FormData();
    body.append("image", file);
    return apiFetch<AnalysisResult>("/scan/image", { method: "POST", body });
  },
  getScan: (id: string) => apiFetch<AnalysisResult>(`/scans/${id}`),

  history: () => apiFetch<HistoryItem[]>("/history"),
  deleteHistory: (id: string) => apiFetch<void>(`/history/${id}`, { method: "DELETE" }),
  favorites: () => apiFetch<Product[]>("/favorites"),
  addFavorite: (productId: string) => apiFetch(`/favorites/${productId}`, { method: "POST" }),
  removeFavorite: (productId: string) => apiFetch<void>(`/favorites/${productId}`, { method: "DELETE" }),
  createReport: (payload: { product_id?: string; subject: string; category: string; message: string }) =>
    apiFetch<Report>("/reports", { method: "POST", body: JSON.stringify(payload) }),

  ingredients: (query = "") => apiFetch<Ingredient[]>(`/ingredients?q=${encodeURIComponent(query)}`),
  adminDashboard: () => apiFetch<AdminDashboard>("/admin/dashboard"),
  adminCreateIngredient: (payload: Record<string, unknown>) =>
    apiFetch<Ingredient>("/admin/ingredients", { method: "POST", body: JSON.stringify(payload) }),
  adminUpdateIngredient: (id: string, payload: Record<string, unknown>) =>
    apiFetch<Ingredient>(`/admin/ingredients/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  adminCertifications: () => apiFetch<Certification[]>("/admin/certifications"),
  adminCreateCertification: (payload: Record<string, unknown>) =>
    apiFetch<Certification>("/admin/certifications", { method: "POST", body: JSON.stringify(payload) }),
  adminReports: () => apiFetch<Report[]>("/admin/reports"),
  adminUpdateReport: (id: string, status: string) =>
    apiFetch<Report>(`/admin/reports/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
};
