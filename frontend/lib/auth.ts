import { api } from "@/lib/api";
import { clearAccessToken, setAccessToken } from "@/lib/storage";
import type { User } from "@/lib/types";

export async function login(email: string, password: string): Promise<User> {
  const result = await api.login({ email, password });
  await setAccessToken(result.access_token);
  return result.user;
}

export async function register(name: string, email: string, password: string, country?: string): Promise<User> {
  const result = await api.register({ name, email, password, country });
  await setAccessToken(result.access_token);
  return result.user;
}

export async function logout(): Promise<void> {
  await clearAccessToken();
}
