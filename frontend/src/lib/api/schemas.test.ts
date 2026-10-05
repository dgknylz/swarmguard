import { describe, expect, it } from "vitest";

import { experimentResultSchema, simulationConfigSchema, simulationFrameSchema } from "./schemas";

describe("GTAD API schemas", () => {
  it("validates the maximum degree configuration", () => {
    const result = simulationConfigSchema.safeParse({
      node_count: 10,
      area_width: 100,
      area_height: 100,
      communication_range: 20,
      speed: 1,
      beta: 0.1,
      gamma: 0.1,
      steps: 5,
      seed: 1,
      initial_infected_count: 1,
      attack_strategy: "random",
      defense_strategy: "gtad_risk",
      defense_budget: 2,
      defense_range_multiplier: 1.5,
      defense_max_degree: 4,
      step_interval_ms: 0,
    });

    expect(result.success).toBe(true);
  });

  it("validates candidate scores and applied GTAD constraints", () => {
    const result = simulationFrameSchema.safeParse({
      step: 1,
      positions: [[0, 0], [1, 0]],
      edges: [[0, 1]],
      infected: [],
      metrics: {
        node_count: 2,
        edge_count: 1,
        infected_count: 0,
        infected_ratio: 0,
        largest_component_ratio: 1,
        global_efficiency: 1,
        algebraic_connectivity: 2,
      },
      events: [],
      defense_report: {
        algorithm: "gtad_risk",
        step: 1,
        applied_actions: [{ action_type: "add_edge", source: 0, target: 1, reason: "GTAD" }],
        rejected_actions: [],
        intervention_cost: 1,
        metadata: {
          candidate_count: 1,
          feasible_candidate_count: 1,
          selected_candidate_count: 1,
          selected_links: [{ source: 0, target: 1, score: 0.8, connectivity_gain: 1, safety_score: 1, distance_score: 0.5, distance: 10 }],
          constraints: { maximum_range: 20, maximum_degree: 4, budget: 1 },
        },
      },
    });

    expect(result.success).toBe(true);
  });
});

describe("experiment result schema", () => {
  it("validates paired Monte Carlo output", () => {
    const run = { method: "none", seed: 42, final_infected_ratio: 0.2, peak_infected_ratio: 0.3, mean_infected_ratio: 0.25, mean_largest_component_ratio: 1, mean_global_efficiency: 0.5, mean_algebraic_connectivity: 0.1, total_intervention_cost: 0 };
    const metric = { n: 1, mean: 0.25, std: 0, ci95_low: 0.25, ci95_high: 0.25 };
    const result = experimentResultSchema.safeParse({
      experiment_id: "0123456789abcdef",
      kind: "monte_carlo",
      strategies: ["none"],
      seeds: [42],
      run_count: 1,
      runs: [run],
      summaries: [{ method: "none", run_count: 1, metrics: { mean_infected_ratio: metric } }],
      paired_comparisons: [],
      manifest: { schema_version: "1.0", software: { name: "swarmguard", version: "0.1.0" }, experiment: {}, fingerprint: `sha256:${"a".repeat(64)}` },
    });

    expect(result.success).toBe(true);
  });

  it("rejects an invalid reproducibility fingerprint", () => {
    expect(experimentResultSchema.safeParse({ experiment_id: "not-valid" }).success).toBe(false);
  });
});
