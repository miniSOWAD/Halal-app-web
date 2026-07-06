import { Preferences } from "@capacitor/preferences";

const TOKEN_KEY = "halalfit_access_token";

export async function getAccessToken(): Promise<string | null> {
  const { value } = await Preferences.get({ key: TOKEN_KEY });
  return value;
}

export async function setAccessToken(token: string): Promise<void> {
  await Preferences.set({ key: TOKEN_KEY, value: token });
  if (typeof window !== "undefined") window.dispatchEvent(new Event("auth-changed"));
}

export async function clearAccessToken(): Promise<void> {
  await Preferences.remove({ key: TOKEN_KEY });
  if (typeof window !== "undefined") window.dispatchEvent(new Event("auth-changed"));
}
