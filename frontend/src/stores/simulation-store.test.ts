import { beforeEach, describe, expect, it } from "vitest";

import { useSimulationStore } from "./simulation-store";

const id = "123e4567-e89b-42d3-a456-426614174000";

describe("simulation store", () => {
  beforeEach(() => useSimulationStore.getState().reset());

  it("stores incoming frames as replay history", () => {
    const frame = { step: 0, positions: [[1, 2]] as [number, number][], edges: [] as [number, number][], infected: [0], metrics: { node_count: 1, edge_count: 0, infected_count: 1, infected_ratio: 1, largest_component_ratio: 1, global_efficiency: 0, algebraic_connectivity: 0 }, events: [] };
    useSimulationStore.getState().receiveMessage({ type: "frame", simulation_id: id, frame });
    expect(useSimulationStore.getState().latestFrame).toEqual(frame);
    expect(useSimulationStore.getState().frames).toHaveLength(1);

    useSimulationStore.getState().receiveMessage({ type: "frame", simulation_id: id, frame });
    expect(useSimulationStore.getState().frames).toHaveLength(1);
  });

  it("moves a newly created session to running on its first frame", () => {
    useSimulationStore.setState({ status: "created" });
    const frame = { step: 0, positions: [[1, 2]] as [number, number][], edges: [] as [number, number][], infected: [], metrics: { node_count: 1, edge_count: 0, infected_count: 0, infected_ratio: 0, largest_component_ratio: 1, global_efficiency: 0, algebraic_connectivity: 0 }, events: [] };

    useSimulationStore.getState().receiveMessage({ type: "frame", simulation_id: id, frame });

    expect(useSimulationStore.getState().status).toBe("running");
  });
});
