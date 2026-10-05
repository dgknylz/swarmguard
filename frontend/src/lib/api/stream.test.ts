import { describe, expect, it } from "vitest";

import { parseStreamMessage } from "./stream";

const id = "123e4567-e89b-42d3-a456-426614174000";

describe("parseStreamMessage", () => {
  it("accepts a valid simulation frame", () => {
    const message = parseStreamMessage(JSON.stringify({ type: "frame", simulation_id: id, frame: { step: 0, positions: [[1, 2]], edges: [], infected: [0], metrics: { node_count: 1, edge_count: 0, infected_count: 1, infected_ratio: 1, largest_component_ratio: 1, global_efficiency: 0, algebraic_connectivity: 0 }, events: [], defense_report: null } }));
    expect(message.type).toBe("frame");
  });

  it("rejects malformed messages", () => {
    expect(() => parseStreamMessage('{"type":"frame"}')).toThrow(/sözleşmeyle/);
  });
});
