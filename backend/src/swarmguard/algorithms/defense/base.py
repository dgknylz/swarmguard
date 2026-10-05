from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Literal

import networkx as nx

ActionType = Literal["add_edge", "remove_edge", "quarantine_node"]


@dataclass(slots=True)
class DefenseContext:
    graph: nx.Graph
    infected: frozenset[int]
    step: int
    communication_range: float
    positions: tuple[tuple[float, float], ...] = ()


@dataclass(frozen=True, slots=True)
class DefenseObservation:
    step: int
    infected: tuple[int, ...]
    node_count: int
    edge_count: int
    nodes: tuple[int, ...] = ()
    healthy: tuple[int, ...] = ()
    edges: tuple[tuple[int, int], ...] = ()
    positions: tuple[tuple[float, float], ...] = ()
    communication_range: float = 0.0
    degrees: tuple[tuple[int, int], ...] = ()
    betweenness: tuple[tuple[int, float], ...] = ()
    risk_scores: tuple[tuple[int, float], ...] = ()


@dataclass(frozen=True, slots=True)
class DefenseAction:
    action_type: ActionType
    source: int
    target: int | None = None
    reason: str = ""


@dataclass(frozen=True, slots=True)
class DefenseDecision:
    algorithm: str
    step: int
    actions: tuple[DefenseAction, ...] = ()
    metadata: dict[str, object] | None = None


@dataclass(frozen=True, slots=True)
class DefenseReport:
    algorithm: str
    step: int
    applied_actions: tuple[DefenseAction, ...] = ()
    rejected_actions: tuple[DefenseAction, ...] = ()
    intervention_cost: float = 0.0
    metadata: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "algorithm": self.algorithm,
            "step": self.step,
            "applied_actions": [asdict(action) for action in self.applied_actions],
            "rejected_actions": [asdict(action) for action in self.rejected_actions],
            "intervention_cost": self.intervention_cost,
            "metadata": self.metadata or {},
        }


class DefenseAlgorithm(ABC):
    """Common observe -> decide -> apply -> report lifecycle."""

    name: str

    @abstractmethod
    def observe(self, context: DefenseContext) -> DefenseObservation:
        raise NotImplementedError

    @abstractmethod
    def decide(self, observation: DefenseObservation) -> DefenseDecision:
        raise NotImplementedError

    def apply(
        self, context: DefenseContext, decision: DefenseDecision
    ) -> tuple[tuple[DefenseAction, ...], tuple[DefenseAction, ...]]:
        applied: list[DefenseAction] = []
        rejected: list[DefenseAction] = []

        for action in decision.actions:
            if action.action_type == "add_edge" and action.target is not None:
                if (
                    action.source != action.target
                    and action.source in context.graph
                    and action.target in context.graph
                    and not context.graph.has_edge(action.source, action.target)
                ):
                    context.graph.add_edge(action.source, action.target)
                    applied.append(action)
                else:
                    rejected.append(action)
            elif action.action_type == "remove_edge" and action.target is not None:
                if context.graph.has_edge(action.source, action.target):
                    context.graph.remove_edge(action.source, action.target)
                    applied.append(action)
                else:
                    rejected.append(action)
            elif action.action_type == "quarantine_node" and action.source in context.graph:
                context.graph.remove_edges_from(list(context.graph.edges(action.source)))
                applied.append(action)
            else:
                rejected.append(action)

        return tuple(applied), tuple(rejected)

    def report(
        self,
        context: DefenseContext,
        decision: DefenseDecision,
        applied: tuple[DefenseAction, ...],
        rejected: tuple[DefenseAction, ...],
    ) -> DefenseReport:
        return DefenseReport(
            algorithm=self.name,
            step=context.step,
            applied_actions=applied,
            rejected_actions=rejected,
            intervention_cost=float(len(applied)),
            metadata=decision.metadata,
        )

    def execute(self, context: DefenseContext) -> DefenseReport:
        observation = self.observe(context)
        decision = self.decide(observation)
        applied, rejected = self.apply(context, decision)
        return self.report(context, decision, applied, rejected)
