import { api } from "@/lib/api";
import { clearAccessToken, setAccessToken } from "@/lib/storage";
import type { User } from "@/lib/types";

export async function login(email: string, password: string): Promise<User> {
  const result = await api.login({ email, password });
  await setAccessToken(result.access_token);
  return result.user;
}

export async function verifyRegistration(email: string, otp: string): Promise<User> {
  const result = await api.registerVerifyOtp(email, otp);
  await setAccessToken(result.access_token);
  return result.user;
}

export async function verifyEmailChange(email: string, otp: string): Promise<User> {
  const result = await api.emailChangeVerifyOtp(email, otp);
  await setAccessToken(result.access_token);
  return result.user;
}

export async function logout(): Promise<void> {
  await clearAccessToken();
}
