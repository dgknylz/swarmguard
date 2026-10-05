import { describe, expect, it } from "vitest";

import type { SimulationFrame } from "@/lib/api/schemas";

import { buildMetricSeries } from "./live-metrics-chart";

describe("buildMetricSeries", () => {
  it("keeps metric samples aligned by step", () => {
    const frames = [0, 1].map((step): SimulationFrame => ({
      step,
      positions: [[0, 0]],
      edges: [],
      infected: step ? [0] : [],
      metrics: { node_count: 1, edge_count: 0, infected_count: step, infected_ratio: step, largest_component_ratio: 1, global_efficiency: 0, algebraic_connectivity: 0 },
      events: [],
    }));
    expect(buildMetricSeries(frames)).toMatchObject({ steps: [0, 1], infected: [0, 1], gcc: [1, 1] });
  });
});
