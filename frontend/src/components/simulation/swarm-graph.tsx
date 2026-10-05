"use client";

import {
  Background,
  BackgroundVariant,
  Controls,
  ReactFlow,
  type Edge,
  type NodeMouseHandler,
} from "@xyflow/react";
import { RadioTower } from "lucide-react";
import { useMemo, useState } from "react";

import type { SimulationFrame } from "@/lib/api/schemas";
import { SwarmNode, type SwarmFlowNode } from "./swarm-node";

const nodeTypes = { uav: SwarmNode };
export type DisplayMode = "scientific" | "presentation";

export function frameToGraph(frame: SimulationFrame, focusedNodeId?: number | null, displayMode: DisplayMode = "scientific"): { nodes: SwarmFlowNode[]; edges: Edge[] } {
  const infected = new Set(frame.infected);
  const newlyInfected = new Set(
    frame.events.filter((event) => event.event_type === "infected").map((event) => event.node_id),
  );
  const degree = new Map<number, number>();
  const actions = frame.defense_report?.applied_actions ?? [];
  const addedEdges = new Set(actions.filter((action) => action.action_type === "add_edge" && action.target !== null).map((action) => `${Math.min(action.source, action.target ?? action.source)}-${Math.max(action.source, action.target ?? action.source)}`));
  const removedEdges = actions.filter((action) => action.action_type === "remove_edge" && action.target !== null);
  const quarantined = new Set(actions.filter((action) => action.action_type === "quarantine_node").map((action) => action.source));
  const riskScores = frame.defense_report?.metadata.risk_scores ?? {};
  frame.edges.forEach(([source, target]) => {
    degree.set(source, (degree.get(source) ?? 0) + 1);
    degree.set(target, (degree.get(target) ?? 0) + 1);
  });

  const nodes: SwarmFlowNode[] = frame.positions.map(([x, y], id) => ({
    id: String(id),
    type: "uav",
    position: { x, y },
    data: {
      label: displayMode === "presentation" ? String(id) : `UAV-${String(id).padStart(2, "0")}`,
      status: infected.has(id) ? "infected" : "healthy",
      newlyInfected: newlyInfected.has(id),
      quarantined: quarantined.has(id),
      neighborCount: degree.get(id) ?? 0,
      riskScore: riskScores[String(id)] ?? 0,
      presentation: displayMode === "presentation",
    },
    selected: id === focusedNodeId,
  }));

  const edges: Edge[] = frame.edges.map(([source, target]) => {
    const exposed = infected.has(source) || infected.has(target);
    const edgeId = `${Math.min(source, target)}-${Math.max(source, target)}`;
    const added = addedEdges.has(edgeId);
    return {
      id: edgeId,
      source: String(source),
      target: String(target),
      animated: added || infected.has(source) !== infected.has(target),
      className: added ? "swarm-edge-added" : exposed ? "swarm-edge-exposed" : undefined,
      style: {
        stroke: added ? "rgba(34,211,238,0.95)" : exposed ? "rgba(251,113,133,0.42)" : "rgba(87,231,214,0.22)",
        strokeWidth: added ? 3 : exposed ? 1.5 : 1,
      },
    };
  });
  removedEdges.forEach((action) => {
    if (action.target === null) return;
    edges.push({
      id: `removed-${action.source}-${action.target}`,
      source: String(action.source),
      target: String(action.target),
      animated: true,
      className: "swarm-edge-removed",
      style: { stroke: "rgba(251,113,133,0.9)", strokeWidth: 2.5, strokeDasharray: "7 6" },
    });
  });
  return { nodes, edges };
}

export function SwarmGraph({ frame, focusedNodeId = null, displayMode = "scientific" }: { frame: SimulationFrame | null; focusedNodeId?: number | null; displayMode?: DisplayMode }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const effectiveSelectedId = focusedNodeId === null ? selectedId : String(focusedNodeId);
  const graph = useMemo(() => (frame ? frameToGraph(frame, effectiveSelectedId === null ? null : Number(effectiveSelectedId), displayMode) : { nodes: [], edges: [] }), [displayMode, effectiveSelectedId, frame]);
  const selected = graph.nodes.find((node) => node.id === effectiveSelectedId);
  const handleNodeClick: NodeMouseHandler<SwarmFlowNode> = (_, node) => setSelectedId(node.id);

  if (!frame) {
    return <div className="flex h-full min-h-[470px] items-center justify-center text-center"><div><RadioTower className="mx-auto text-slate-700" size={34} /><p className="mt-4 text-xs font-semibold text-slate-400">Canlı ağ bekleniyor</p><p className="mt-2 text-[11px] text-slate-600">Simülasyonu başlattığında İHA topolojisi burada oluşacak.</p></div></div>;
  }

  return <div className="relative h-full min-h-[470px]">
    <ReactFlow
      colorMode="dark"
      defaultEdgeOptions={{ selectable: false }}
      edges={graph.edges}
      elementsSelectable
      fitView
      fitViewOptions={{ padding: 0.18, duration: 500 }}
      maxZoom={1.8}
      minZoom={0.35}
      nodeTypes={nodeTypes}
      nodes={graph.nodes}
      nodesConnectable={false}
      nodesDraggable={false}
      onNodeClick={handleNodeClick}
    >
      <Background color="rgba(87,231,214,0.08)" gap={28} size={1} variant={BackgroundVariant.Dots} />
      {displayMode === "scientific" && <Controls position="bottom-right" showInteractive={false} />}
    </ReactFlow>
    {selected && displayMode === "scientific" && <div className="absolute bottom-4 left-4 z-10 min-w-48 rounded-xl border border-white/10 bg-[#081419]/90 p-3 shadow-2xl backdrop-blur"><p className="text-xs font-bold text-white">{selected.data.label}</p><div className="mt-2 flex items-center justify-between gap-6 text-[10px]"><span className="text-slate-600">Durum</span><span className={selected.data.status === "infected" ? "text-rose-300" : "text-emerald-300"}>{selected.data.status === "infected" ? "Enfekte" : "Sağlıklı"}</span></div><div className="mt-1.5 flex items-center justify-between text-[10px]"><span className="text-slate-600">Komşu</span><span className="text-slate-300">{selected.data.neighborCount}</span></div><div className="mt-1.5 flex items-center justify-between text-[10px]"><span className="text-slate-600">Risk</span><span className={selected.data.riskScore >= 0.65 ? "text-amber-300" : "text-slate-300"}>{selected.data.riskScore.toFixed(3)}</span></div></div>}
  </div>;
}
