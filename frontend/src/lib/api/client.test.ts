import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiClient } from "./client";

afterEach(() => vi.unstubAllGlobals());

describe("apiClient", () => {
  it("validates a health response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "ok", service: "swarmguard-api" }), { status: 200 })));
    await expect(apiClient.health()).resolves.toEqual({ status: "ok", service: "swarmguard-api" });
  });

  it("turns API failures into ApiError", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Geçersiz parametre" }), { status: 422 })));
    await expect(apiClient.health()).rejects.toMatchObject({
      name: "ApiError",
      status: 422,
      message: "Geçersiz parametre",
    } satisfies Partial<ApiError>);
  });
});
