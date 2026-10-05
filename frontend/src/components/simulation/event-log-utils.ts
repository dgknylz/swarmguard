import type { SimulationFrame } from "@/lib/api/schemas";

export type TimelineEvent = SimulationFrame["events"][number] & { step: number };

export function collectEvents(frames: SimulationFrame[]): TimelineEvent[] {
  return frames.flatMap((frame) => frame.events.map((event) => ({ ...event, step: frame.step })));
}

function csvCell(value: unknown): string {
  const text = value == null ? "" : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

export function serializeEventsCsv(events: TimelineEvent[]): string {
  const headers = ["step", "event_type", "node_id", "target_node_id", "algorithm", "detail"];
  const rows = events.map((event) => headers.map((key) => csvCell(event[key as keyof TimelineEvent])).join(","));
  return [headers.join(","), ...rows].join("\n");
}

export function serializeEventsJson(events: TimelineEvent[]): string {
  return JSON.stringify(events, null, 2);
}

export function filterEvents(events: TimelineEvent[], eventType: string, nodeId: string): TimelineEvent[] {
  return events.filter((event) => (eventType === "all" || event.event_type === eventType) && (nodeId === "all" || event.node_id === Number(nodeId)));
}
