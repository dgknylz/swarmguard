"use client";

import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import { cn } from "@/lib/utils";

export type SwarmNodeData = {
  label: string;
  status: "healthy" | "infected";
  newlyInfected: boolean;
  quarantined: boolean;
  neighborCount: number;
  riskScore: number;
  presentation: boolean;
};

export type SwarmFlowNode = Node<SwarmNodeData, "uav">;

export function SwarmNode({ data, selected }: NodeProps<SwarmFlowNode>) {
  const infected = data.status === "infected";
  return <div className={cn("swarm-node", infected ? "swarm-node-infected" : "swarm-node-healthy", data.riskScore >= 0.65 && "swarm-node-risk", data.newlyInfected && "swarm-node-pulse", data.quarantined && "swarm-node-quarantined", data.presentation && "swarm-node-presentation", selected && "swarm-node-selected")}>
    <Handle className="!border-0 !bg-transparent" position={Position.Left} type="target" />
    <span>{data.label}</span>
    {!data.presentation && <span className="swarm-node-degree">{data.neighborCount}</span>}
    <Handle className="!border-0 !bg-transparent" position={Position.Right} type="source" />
  </div>;
}
