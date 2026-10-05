import type { ZodType } from "zod";

import { API_BASE_URL } from "./config";
import {
  controlResponseSchema,
  experimentResultSchema,
  healthResponseSchema,
  simulationCreateResponseSchema,
  simulationStatusResponseSchema,
  type ControlResponse,
  type ExperimentRequest,
  type ExperimentResult,
  type HealthResponse,
  type SimulationCreateRequest,
  type SimulationCreateResponse,
  type SimulationStatusResponse,
  type MonteCarloRequest,
} from "./schemas";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export type ExperimentArtifact = "export.csv" | "export.parquet" | "manifest.json";

export const experimentArtifactUrl = (
  experimentId: string,
  artifact: ExperimentArtifact,
) => `${API_BASE_URL}/api/v1/experiments/${experimentId}/${artifact}`;

async function request<T>(
  path: string,
  schema: ZodType<T>,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });

  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const message =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? String(payload.detail)
        : `API isteği başarısız oldu (${response.status})`;
    throw new ApiError(message, response.status, payload);
  }

  const parsed = schema.safeParse(payload);
  if (!parsed.success) {
    throw new ApiError("API yanıtı beklenen sözleşmeyle eşleşmiyor", 502, parsed.error.flatten());
  }
  return parsed.data;
}

export const apiClient = {
  health: (): Promise<HealthResponse> => request("/health", healthResponseSchema),

  createSimulation: (config: SimulationCreateRequest): Promise<SimulationCreateResponse> =>
    request("/api/v1/simulations", simulationCreateResponseSchema, {
      method: "POST",
      body: JSON.stringify(config),
    }),

  getSimulation: (id: string): Promise<SimulationStatusResponse> =>
    request(`/api/v1/simulations/${id}`, simulationStatusResponseSchema),

  pauseSimulation: (id: string): Promise<ControlResponse> =>
    request(`/api/v1/simulations/${id}/pause`, controlResponseSchema, { method: "POST" }),

  resumeSimulation: (id: string): Promise<ControlResponse> =>
    request(`/api/v1/simulations/${id}/resume`, controlResponseSchema, { method: "POST" }),

  stopSimulation: (id: string): Promise<ControlResponse> =>
    request(`/api/v1/simulations/${id}/stop`, controlResponseSchema, { method: "POST" }),

  runMonteCarlo: (experiment: MonteCarloRequest): Promise<ExperimentResult> =>
    request("/api/v1/experiments/monte-carlo", experimentResultSchema, {
      method: "POST",
      body: JSON.stringify(experiment),
    }),

  runGtadAblation: (experiment: ExperimentRequest): Promise<ExperimentResult> =>
    request("/api/v1/experiments/gtad-ablation", experimentResultSchema, {
      method: "POST",
      body: JSON.stringify(experiment),
    }),
};
