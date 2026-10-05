import { describe, expect, it } from "vitest";

import type { SimulationFrame } from "@/lib/api/schemas";

import { frameToGraph } from "./swarm-graph";

const frame: SimulationFrame = {
  step: 4,
  positions: [[10, 20], [30, 40], [50, 60]],
  edges: [[0, 1], [1, 2]],
  infected: [1],
  metrics: { node_count: 3, edge_count: 2, infected_count: 1, infected_ratio: 1 / 3, largest_component_ratio: 1, global_efficiency: 1, algebraic_connectivity: 1 },
  events: [{ event_type: "infected", node_id: 1 }],
};

describe("frameToGraph", () => {
  it("maps simulation positions, states and degrees to React Flow", () => {
    const graph = frameToGraph(frame);
    expect(graph.nodes).toHaveLength(3);
    expect(graph.edges).toHaveLength(2);
    expect(graph.nodes[1].data).toMatchObject({ status: "infected", newlyInfected: true, neighborCount: 2 });
    expect(graph.nodes[0].position).toEqual({ x: 10, y: 20 });
  });

  it("maps GTAD risk metadata to nodes", () => {
    const riskyFrame: SimulationFrame = { ...frame, defense_report: { algorithm: "gtad_risk", step: 4, applied_actions: [], rejected_actions: [], intervention_cost: 0, metadata: { risk_scores: { "1": 0.92 }, max_risk: 0.92 } } };
    expect(frameToGraph(riskyFrame).nodes[1].data.riskScore).toBe(0.92);
  });

  it("marks added, removed and quarantined topology actions for animation", () => {
    const animatedFrame: SimulationFrame = { ...frame, defense_report: { algorithm: "gtad_risk", step: 4, applied_actions: [{ action_type: "add_edge", source: 0, target: 2, reason: "add" }, { action_type: "remove_edge", source: 0, target: 1, reason: "cut" }, { action_type: "quarantine_node", source: 1, target: null, reason: "quarantine" }], rejected_actions: [], intervention_cost: 3, metadata: {} }, edges: [[0, 2], [1, 2]] };
    const graph = frameToGraph(animatedFrame);

    expect(graph.edges.find((edge) => edge.id === "0-2")).toMatchObject({ animated: true, className: "swarm-edge-added" });
    expect(graph.edges.find((edge) => edge.id.startsWith("removed-"))?.className).toBe("swarm-edge-removed");
    expect(graph.nodes[1].data.quarantined).toBe(true);
  });

  it("uses compact labels and hides scientific badges in presentation mode", () => {
    const graph = frameToGraph(frame, null, "presentation");
    expect(graph.nodes[0].data).toMatchObject({ label: "0", presentation: true });
  });
});
