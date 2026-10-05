import { describe, expect, it } from "vitest";

import { filterEvents, serializeEventsCsv, serializeEventsJson, type TimelineEvent } from "./event-log-utils";

const events: TimelineEvent[] = [
  { step: 0, event_type: "initial_infection", node_id: 2, target_node_id: null, algorithm: null, detail: null },
  { step: 3, event_type: "recovered", node_id: 2, target_node_id: null, algorithm: null, detail: "ok" },
  { step: 4, event_type: "infected", node_id: 5, target_node_id: null, algorithm: null, detail: null },
];

describe("event log utilities", () => {
  it("filters by event type and node", () => {
    expect(filterEvents(events, "recovered", "2")).toEqual([events[1]]);
    expect(filterEvents(events, "all", "5")).toEqual([events[2]]);
  });

  it("exports stable CSV and JSON", () => {
    expect(serializeEventsCsv(events)).toContain('"3","recovered","2"');
    expect(JSON.parse(serializeEventsJson(events))).toEqual(events);
  });
});
