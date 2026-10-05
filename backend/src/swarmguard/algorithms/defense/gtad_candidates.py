from __future__ import annotations

from dataclasses import dataclass, replace
from math import dist

import networkx as nx

from .base import DefenseObservation


@dataclass(frozen=True, slots=True)
class LinkCandidate:
    source: int
    target: int
    distance: float
    connectivity_gain: float = 0.0
    safety_score: float = 0.0
    distance_score: float = 0.0
    total_score: float = 0.0


@dataclass(frozen=True, slots=True)
class CandidateSelection:
    selected: tuple[LinkCandidate, ...]
    range_rejected: int
    degree_rejected: int
    budget_rejected: int


@dataclass(frozen=True, slots=True)
class ScoreWeights:
    connectivity: float = 0.50
    safety: float = 0.30
    distance: float = 0.20

    def __post_init__(self) -> None:
        values = (self.connectivity, self.safety, self.distance)
        if any(value < 0 for value in values) or sum(values) <= 0:
            raise ValueError("GTAD ağırlıkları negatif olamaz ve toplamları pozitif olmalıdır")

    def normalized(self) -> ScoreWeights:
        total = self.connectivity + self.safety + self.distance
        return ScoreWeights(
            connectivity=self.connectivity / total,
            safety=self.safety / total,
            distance=self.distance / total,
        )

    def to_dict(self) -> dict[str, float]:
        normalized = self.normalized()
        return {
            "connectivity": round(normalized.connectivity, 6),
            "safety": round(normalized.safety, 6),
            "distance": round(normalized.distance, 6),
        }


def generate_link_candidates(observation: DefenseObservation) -> tuple[LinkCandidate, ...]:
    """Generate every missing healthy-to-healthy link in deterministic order."""
    if len(observation.positions) < observation.node_count:
        return ()

    existing = {tuple(sorted(edge)) for edge in observation.edges}
    candidates: list[LinkCandidate] = []
    for index, source in enumerate(observation.healthy):
        for target in observation.healthy[index + 1 :]:
            if (source, target) in existing:
                continue
            candidates.append(
                LinkCandidate(
                    source=source,
                    target=target,
                    distance=dist(observation.positions[source], observation.positions[target]),
                )
            )
    return tuple(candidates)


def score_link_candidates(
    observation: DefenseObservation,
    candidates: tuple[LinkCandidate, ...],
    *,
    maximum_range: float,
    weights: ScoreWeights | None = None,
) -> tuple[LinkCandidate, ...]:
    """Score topology gain, endpoint safety and radio distance on [0, 1]."""
    graph = nx.Graph()
    graph.add_nodes_from(observation.nodes)
    graph.add_edges_from(observation.edges)
    risk = dict(observation.risk_scores)
    component_by_node = {
        node: component_index
        for component_index, component in enumerate(nx.connected_components(graph))
        for node in component
    }
    path_normalizer = max(1, observation.node_count - 2)
    scored: list[LinkCandidate] = []
    normalized_weights = (weights or ScoreWeights()).normalized()

    for candidate in candidates:
        if component_by_node[candidate.source] != component_by_node[candidate.target]:
            connectivity_gain = 1.0
        else:
            path_length = nx.shortest_path_length(graph, candidate.source, candidate.target)
            connectivity_gain = min(1.0, max(0.0, (path_length - 1) / path_normalizer))

        safety_score = 1.0 - (risk.get(candidate.source, 0.0) + risk.get(candidate.target, 0.0)) / 2
        distance_score = max(0.0, 1.0 - candidate.distance / maximum_range)
        total_score = (
            normalized_weights.connectivity * connectivity_gain
            + normalized_weights.safety * safety_score
            + normalized_weights.distance * distance_score
        )
        scored.append(
            replace(
                candidate,
                connectivity_gain=round(connectivity_gain, 6),
                safety_score=round(safety_score, 6),
                distance_score=round(distance_score, 6),
                total_score=round(total_score, 6),
            )
        )

    return tuple(sorted(scored, key=lambda item: (-item.total_score, item.source, item.target)))


def select_feasible_candidates(
    observation: DefenseObservation,
    candidates: tuple[LinkCandidate, ...],
    *,
    maximum_range: float,
    maximum_degree: int,
    budget: int,
) -> CandidateSelection:
    """Greedily enforce physical range, dynamic degree caps and action budget."""
    degrees = dict(observation.degrees)
    selected: list[LinkCandidate] = []
    range_rejected = 0
    degree_rejected = 0
    budget_rejected = 0

    for candidate in candidates:
        if candidate.distance > maximum_range:
            range_rejected += 1
            continue
        if (
            degrees.get(candidate.source, 0) >= maximum_degree
            or degrees.get(candidate.target, 0) >= maximum_degree
        ):
            degree_rejected += 1
            continue
        if len(selected) >= budget:
            budget_rejected += 1
            continue

        selected.append(candidate)
        degrees[candidate.source] = degrees.get(candidate.source, 0) + 1
        degrees[candidate.target] = degrees.get(candidate.target, 0) + 1

    return CandidateSelection(
        selected=tuple(selected),
        range_rejected=range_rejected,
        degree_rejected=degree_rejected,
        budget_rejected=budget_rejected,
    )
