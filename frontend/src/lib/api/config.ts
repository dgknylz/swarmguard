const trimTrailingSlash = (value: string) => value.replace(/\/$/, "");

export const API_BASE_URL = trimTrailingSlash(
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000",
);

export const WS_BASE_URL = trimTrailingSlash(
  process.env.NEXT_PUBLIC_WS_URL ?? API_BASE_URL.replace(/^http/, "ws"),
);
