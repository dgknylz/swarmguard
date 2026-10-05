"use client";

import dynamic from "next/dynamic";

import type { SimulationFrame } from "@/lib/api/schemas";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export function buildMetricSeries(frames: SimulationFrame[]) {
  return {
    steps: frames.map((frame) => frame.step),
    infected: frames.map((frame) => frame.metrics.infected_ratio),
    gcc: frames.map((frame) => frame.metrics.largest_component_ratio),
    efficiency: frames.map((frame) => frame.metrics.global_efficiency),
    lambda2: frames.map((frame) => frame.metrics.algebraic_connectivity),
  };
}

export function LiveMetricsChart({ frames }: { frames: SimulationFrame[] }) {
  const series = buildMetricSeries(frames);
  return <Plot
    config={{ displayModeBar: false, responsive: true }}
    data={[
      { x: series.steps, y: series.infected, type: "scatter", mode: "lines", name: "Enfeksiyon", line: { color: "#fb7185", width: 2 } },
      { x: series.steps, y: series.gcc, type: "scatter", mode: "lines", name: "GCC", line: { color: "#6ee7b7", width: 2 } },
      { x: series.steps, y: series.efficiency, type: "scatter", mode: "lines", name: "Efficiency", line: { color: "#57e7d6", width: 2 } },
      { x: series.steps, y: series.lambda2, type: "scatter", mode: "lines", name: "λ₂", yaxis: "y2", line: { color: "#fbbf24", width: 1.5, dash: "dot" } },
    ]}
    layout={{
      autosize: true,
      height: 270,
      margin: { l: 38, r: 38, t: 14, b: 36 },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      font: { color: "#64787f", size: 10 },
      legend: { orientation: "h", x: 0, y: 1.14, font: { size: 9 } },
      hovermode: "x unified",
      xaxis: { title: { text: "Zaman adımı", font: { size: 9 } }, gridcolor: "rgba(255,255,255,0.045)", zeroline: false },
      yaxis: { range: [0, 1], gridcolor: "rgba(255,255,255,0.045)", zeroline: false },
      yaxis2: { overlaying: "y", side: "right", showgrid: false, zeroline: false },
    }}
    style={{ width: "100%", height: "270px" }}
    useResizeHandler
  />;
}
