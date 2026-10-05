import { z } from "zod";

export const attackStrategySchema = z.enum([
  "random",
  "highest_degree",
  "highest_betweenness",
]);

export const defenseStrategySchema = z.enum([
  "none",
  "random_rewiring",
  "centrality_quarantine",
  "gtad_risk",
]);

export const sessionStatusSchema = z.enum([
  "created",
  "running",
  "paused",
  "completed",
  "stopped",
  "failed",
]);

export const simulationConfigSchema = z.object({
  node_count: z.number().int().min(2).max(500),
  area_width: z.number().positive(),
  area_height: z.number().positive(),
  communication_range: z.number().positive(),
  speed: z.number().nonnegative(),
  beta: z.number().min(0).max(1),
  gamma: z.number().min(0).max(1),
  steps: z.number().int().positive(),
  seed: z.number().int().nonnegative(),
  initial_infected_count: z.number().int().positive(),
  attack_strategy: attackStrategySchema,
  defense_strategy: defenseStrategySchema,
  defense_budget: z.number().int().min(0).max(100),
  defense_range_multiplier: z.number().min(1).max(5),
  defense_max_degree: z.number().int().min(1).max(499),
  step_interval_ms: z.number().int().nonnegative(),
});

export const simulationCreateResponseSchema = z.object({
  id: z.string().uuid(),
  status: sessionStatusSchema,
  stream_url: z.string().startsWith("/"),
  config: simulationConfigSchema,
});

export const simulationStatusResponseSchema = z.object({
  id: z.string().uuid(),
  status: sessionStatusSchema,
  latest_step: z.number().int(),
  frame_count: z.number().int().nonnegative(),
  error: z.string().nullable(),
});

export const controlResponseSchema = z.object({
  id: z.string().uuid(),
  status: sessionStatusSchema,
});

export const healthResponseSchema = z.object({
  status: z.literal("ok"),
  service: z.literal("swarmguard-api"),
});

const eventSchema = z.object({
  event_type: z.string(),
  node_id: z.number().int(),
  target_node_id: z.number().int().nullable().optional(),
  algorithm: z.string().nullable().optional(),
  detail: z.string().nullable().optional(),
});

const defenseActionSchema = z.object({
  action_type: z.enum(["add_edge", "remove_edge", "quarantine_node"]),
  source: z.number().int(),
  target: z.number().int().nullable(),
  reason: z.string(),
});

const defenseReportSchema = z.object({
  algorithm: z.string(),
  step: z.number().int().nonnegative(),
  applied_actions: z.array(defenseActionSchema),
  rejected_actions: z.array(defenseActionSchema),
  intervention_cost: z.number().nonnegative(),
  metadata: z.object({
    candidate_count: z.number().int().nonnegative().optional(),
    feasible_candidate_count: z.number().int().nonnegative().optional(),
    selected_candidate_count: z.number().int().nonnegative().optional(),
    range_rejected_count: z.number().int().nonnegative().optional(),
    degree_rejected_count: z.number().int().nonnegative().optional(),
    budget_rejected_count: z.number().int().nonnegative().optional(),
    rewiring_count: z.number().int().nonnegative().optional(),
    quarantined_nodes: z.array(z.number().int()).optional(),
    risk_scores: z.record(z.string(), z.number().min(0).max(1)).optional(),
    highest_risk_nodes: z.array(z.number().int()).optional(),
    max_risk: z.number().min(0).max(1).optional(),
    selected_links: z.array(z.object({
      source: z.number().int(),
      target: z.number().int(),
      score: z.number().min(0).max(1),
      connectivity_gain: z.number().min(0).max(1),
      safety_score: z.number().min(0).max(1),
      distance_score: z.number().min(0).max(1),
      distance: z.number().nonnegative(),
    })).optional(),
    score_weights: z.object({
      connectivity: z.number(),
      safety: z.number(),
      distance: z.number(),
    }).optional(),
    constraints: z.object({
      maximum_range: z.number().positive(),
      maximum_degree: z.number().int().positive(),
      budget: z.number().int().nonnegative(),
    }).optional(),
  }).passthrough(),
});

export const simulationFrameSchema = z.object({
  step: z.number().int().nonnegative(),
  positions: z.array(z.tuple([z.number(), z.number()])),
  edges: z.array(z.tuple([z.number().int(), z.number().int()])),
  infected: z.array(z.number().int()),
  metrics: z.object({
    node_count: z.number().int().positive(),
    edge_count: z.number().int().nonnegative(),
    infected_count: z.number().int().nonnegative(),
    infected_ratio: z.number().min(0).max(1),
    largest_component_ratio: z.number().min(0).max(1),
    global_efficiency: z.number().min(0).max(1),
    algebraic_connectivity: z.number().nonnegative(),
  }),
  events: z.array(eventSchema),
  defense_report: defenseReportSchema.nullable().optional(),
});

export const streamMessageSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("frame"),
    simulation_id: z.string().uuid(),
    frame: simulationFrameSchema,
  }),
  z.object({
    type: z.literal("status"),
    simulation_id: z.string().uuid(),
    status: sessionStatusSchema,
    error: z.string().nullable(),
  }),
]);

const experimentRunSchema = z.object({
  method: z.string(),
  seed: z.number().int().nonnegative(),
  final_infected_ratio: z.number().min(0).max(1),
  peak_infected_ratio: z.number().min(0).max(1),
  mean_infected_ratio: z.number().min(0).max(1),
  mean_largest_component_ratio: z.number().min(0).max(1),
  mean_global_efficiency: z.number().min(0).max(1),
  mean_algebraic_connectivity: z.number().nonnegative(),
  total_intervention_cost: z.number().nonnegative(),
});

const aggregateMetricSchema = z.object({
  n: z.number().int().positive(),
  mean: z.number(),
  std: z.number().nonnegative(),
  ci95_low: z.number(),
  ci95_high: z.number(),
});

const pairedComparisonSchema = z.object({
  baseline: z.string(),
  method: z.string(),
  pair_count: z.number().int().nonnegative(),
  pairs: z.array(z.object({
    seed: z.number().int().nonnegative(),
    deltas: z.record(z.string(), z.number()),
  })),
  mean_deltas: z.record(z.string(), z.number()),
  delta_statistics: z.record(z.string(), aggregateMetricSchema),
});

export const experimentResultSchema = z.object({
  experiment_id: z.string().regex(/^[0-9a-f]{16}$/),
  kind: z.enum(["monte_carlo", "gtad_ablation"]),
  seeds: z.array(z.number().int().nonnegative()),
  run_count: z.number().int().nonnegative(),
  runs: z.array(experimentRunSchema),
  summaries: z.array(z.object({
    method: z.string(),
    run_count: z.number().int().nonnegative(),
    metrics: z.record(z.string(), aggregateMetricSchema),
  })),
  paired_comparisons: z.array(pairedComparisonSchema),
  strategies: z.array(defenseStrategySchema).optional(),
  variants: z.record(z.string(), z.object({
    connectivity: z.number().min(0).max(1),
    safety: z.number().min(0).max(1),
    distance: z.number().min(0).max(1),
  })).optional(),
  scenario: z.record(z.string(), z.unknown()).optional(),
  manifest: z.object({
    schema_version: z.literal("1.0"),
    software: z.object({ name: z.literal("swarmguard"), version: z.string() }),
    experiment: z.record(z.string(), z.unknown()),
    fingerprint: z.string().startsWith("sha256:"),
  }),
});

export const experimentRequestSchema = z.object({
  scenario: simulationConfigSchema,
  seeds: z.array(z.number().int().nonnegative()).min(1).max(30),
});

export const monteCarloRequestSchema = experimentRequestSchema.extend({
  strategies: z.array(defenseStrategySchema).min(1),
});

export type AttackStrategy = z.infer<typeof attackStrategySchema>;
export type DefenseStrategy = z.infer<typeof defenseStrategySchema>;
export type SessionStatus = z.infer<typeof sessionStatusSchema>;
export type SimulationConfig = z.infer<typeof simulationConfigSchema>;
export type SimulationCreateResponse = z.infer<typeof simulationCreateResponseSchema>;
export type SimulationStatusResponse = z.infer<typeof simulationStatusResponseSchema>;
export type ControlResponse = z.infer<typeof controlResponseSchema>;
export type HealthResponse = z.infer<typeof healthResponseSchema>;
export type SimulationFrame = z.infer<typeof simulationFrameSchema>;
export type StreamMessage = z.infer<typeof streamMessageSchema>;
export type ExperimentResult = z.infer<typeof experimentResultSchema>;
export type ExperimentRequest = z.infer<typeof experimentRequestSchema>;
export type MonteCarloRequest = z.infer<typeof monteCarloRequestSchema>;

export type SimulationCreateRequest = SimulationConfig;
