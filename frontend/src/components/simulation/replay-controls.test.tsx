import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { SimulationFrame } from "@/lib/api/schemas";

import { ReplayControls } from "./replay-controls";

const frame = (step: number): SimulationFrame => ({
  step,
  positions: [[0, 0], [1, 1]],
  edges: [[0, 1]],
  infected: [],
  metrics: { node_count: 2, edge_count: 1, infected_count: 0, infected_ratio: 0, largest_component_ratio: 1, global_efficiency: 1, algebraic_connectivity: 2 },
  events: [],
  defense_report: null,
});

describe("ReplayControls", () => {
  it("moves through frames and returns to live mode", () => {
    const onIndexChange = vi.fn();
    const onLive = vi.fn();
    render(<ReplayControls frames={[frame(0), frame(1), frame(2)]} index={1} onIndexChange={onIndexChange} onLive={onLive} />);

    fireEvent.click(screen.getByRole("button", { name: "Sonraki kare" }));
    fireEvent.click(screen.getByRole("button", { name: /Canlıya dön/i }));

    expect(onIndexChange).toHaveBeenCalledWith(2);
    expect(onLive).toHaveBeenCalledOnce();
  });
});
