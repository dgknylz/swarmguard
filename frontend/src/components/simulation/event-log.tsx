"use client";

import { Activity, Download, Network, ShieldCheck, ShieldX } from "lucide-react";
import { useMemo, useState } from "react";

import type { SimulationFrame } from "@/lib/api/schemas";

import { collectEvents, filterEvents, serializeEventsCsv, serializeEventsJson, type TimelineEvent } from "./event-log-utils";

function download(name: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(url);
}

const eventLabel: Record<string, string> = {
  initial_infection: "saldırı başlangıcı",
  infected: "enfekte oldu",
  recovered: "iyileşti",
  add_edge: "bağlantı eklendi",
  remove_edge: "bağlantı kesildi",
  quarantine_node: "karantinaya alındı",
};

export function EventLog({ frames, onSelectEvent }: { frames: SimulationFrame[]; onSelectEvent?: (event: TimelineEvent) => void; }) {
  const allEvents = useMemo(() => collectEvents(frames), [frames]);
  const [eventType, setEventType] = useState("all");
  const [nodeId, setNodeId] = useState("all");
  const eventTypes = [...new Set(allEvents.map((event) => event.event_type))].sort();
  const nodeIds = [...new Set(allEvents.map((event) => event.node_id))].sort((a, b) => a - b);
  const events = filterEvents(allEvents, eventType, nodeId).reverse();

  return <div className="space-y-3">
    <div className="grid grid-cols-2 gap-2">
      <select aria-label="Olay türü filtresi" className="form-input !py-2 text-[10px]" onChange={(event) => setEventType(event.target.value)} value={eventType}><option value="all">Tüm olaylar</option>{eventTypes.map((type) => <option key={type} value={type}>{eventLabel[type] ?? type}</option>)}</select>
      <select aria-label="İHA filtresi" className="form-input !py-2 text-[10px]" onChange={(event) => setNodeId(event.target.value)} value={nodeId}><option value="all">Tüm İHA&apos;lar</option>{nodeIds.map((id) => <option key={id} value={id}>UAV-{String(id).padStart(2, "0")}</option>)}</select>
    </div>
    <div className="flex gap-2">
      <button className="flex flex-1 items-center justify-center gap-1 rounded-lg border border-white/10 px-2 py-2 text-[10px] text-slate-400 transition hover:border-cyan-300/30 hover:text-cyan-200" disabled={!events.length} onClick={() => download("swarmguard-events.csv", serializeEventsCsv(events.slice().reverse()), "text/csv;charset=utf-8")} type="button"><Download size={11} /> CSV</button>
      <button className="flex flex-1 items-center justify-center gap-1 rounded-lg border border-white/10 px-2 py-2 text-[10px] text-slate-400 transition hover:border-cyan-300/30 hover:text-cyan-200" disabled={!events.length} onClick={() => download("swarmguard-events.json", serializeEventsJson(events.slice().reverse()), "application/json")} type="button"><Download size={11} /> JSON</button>
    </div>
    {!events.length ? <div className="flex min-h-[280px] items-center justify-center rounded-xl border border-dashed border-white/[0.08] bg-black/10 p-6 text-center"><div><Activity className="mx-auto text-slate-700" size={25} /><p className="mt-4 text-xs font-semibold text-slate-400">Eşleşen olay yok</p><p className="mt-2 text-[11px] leading-5 text-slate-600">Filtreleri değiştir veya simülasyonu başlat.</p></div></div> : <div className="max-h-[350px] space-y-2 overflow-y-auto pr-1">{events.map((event, index) => {
      const infected = event.event_type === "infected" || event.event_type === "initial_infection";
      const defense = ["add_edge", "remove_edge", "quarantine_node"].includes(event.event_type);
      const Icon = defense ? Network : infected ? ShieldX : ShieldCheck;
      const tone = infected ? "bg-rose-300/10 text-rose-300" : defense ? "bg-cyan-300/10 text-cyan-300" : "bg-emerald-300/10 text-emerald-300";
      return <button className="flex w-full gap-3 rounded-xl border border-white/[0.055] bg-white/[0.025] p-3 text-left transition hover:border-cyan-300/20 hover:bg-cyan-300/[0.04]" key={`${event.step}-${event.node_id}-${event.event_type}-${index}`} onClick={() => onSelectEvent?.(event)} type="button"><div className={`mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg ${tone}`}><Icon size={13} /></div><div className="min-w-0"><p className="text-[11px] text-slate-300">UAV-{String(event.node_id).padStart(2, "0")} <span className="text-slate-500">{eventLabel[event.event_type] ?? event.event_type}</span></p><p className="mt-1 font-mono text-[9px] uppercase tracking-wider text-slate-700">t = {event.step}{event.algorithm ? ` · ${event.algorithm}` : ""}</p></div></button>;
    })}</div>}
  </div>;
}
