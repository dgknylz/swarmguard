from __future__ import annotations

from math import dist

import numpy as np

from ...spectral import adjacency_from_edges, connected_components, fiedler_pair, perron_pair
from .base import (
    DefenseAction,
    DefenseAlgorithm,
    DefenseContext,
    DefenseDecision,
    DefenseObservation,
)
from .observation import build_observation


class SpectralShieldAlgorithm(DefenseAlgorithm):
    """Security first by Perron weight, then repair by Fiedler gain (Teori, Lemma 4).

    1. Known infected UAVs are isolated in decreasing order of their Perron weight uᵢ.
       Isolating i lowers λ₁ by at most 2λ₁uᵢ², so large weights promise the largest
       drop of the spread factor σ = 1 − γ + βλ₁ that controls Teorem 2.
    2. The remaining budget adds healthy links. Joining separate components comes
       first; inside the giant component a link gains at most (vᵢ − vⱼ)² in λ₂ and
       costs at least 2uᵢuⱼ in λ₁, so a link is kept only when its normalised gain
       exceeds the penalised, normalised spread cost.
    """

    name = "spectral_shield"

    def __init__(
        self,
        budget: int,
        range_multiplier: float = 1.5,
        maximum_degree: int = 8,
        link_penalty: float = 1.0,
    ) -> None:
        self.budget = budget
        self.range_multiplier = range_multiplier
        self.maximum_degree = maximum_degree
        self.link_penalty = link_penalty

    def observe(self, context: DefenseContext) -> DefenseObservation:
        return build_observation(context, include_betweenness=False)

    def decide(self, observation: DefenseObservation) -> DefenseDecision:
        adjacency = adjacency_from_edges(observation.node_count, observation.edges)
        radius, perron = perron_pair(adjacency)
        degrees = dict(observation.degrees)
        targets = sorted(
            (node for node in observation.infected if degrees.get(node, 0) > 0),
            key=lambda node: (-perron[node], node),
        )[: self.budget]
        actions = [
            DefenseAction(
                "quarantine_node",
                node,
                reason=(
                    f"Perron ağırlığı u²={perron[node] ** 2:.4f}; "
                    f"λ₁ azalması ≤ {2 * radius * perron[node] ** 2:.3f}"
                ),
            )
            for node in targets
        ]

        links: list[dict[str, object]] = []
        remaining = self.budget - len(actions)
        if remaining > 0:
            for node in targets:
                adjacency[node, :] = 0.0
                adjacency[:, node] = 0.0
            excluded = set(observation.infected) | set(observation.quarantined)
            links = self._repair_links(observation, adjacency, remaining, excluded)
            actions.extend(
                DefenseAction(
                    "add_edge", int(link["source"]), int(link["target"]), str(link["reason"])
                )
                for link in links
            )

        return DefenseDecision(
            algorithm=self.name,
            step=observation.step,
            actions=tuple(actions),
            metadata={
                "spectral_radius": round(radius, 6),
                "quarantine_targets": targets,
                "perron_weights": {str(node): round(float(perron[node]), 6) for node in targets},
                "repair_links": links,
                "link_penalty": self.link_penalty,
            },
        )

    def _repair_links(
        self,
        observation: DefenseObservation,
        adjacency: np.ndarray,
        budget: int,
        excluded: set[int],
    ) -> list[dict[str, object]]:
        if len(observation.positions) < observation.node_count:
            return []

        node_count = observation.node_count
        components = connected_components(adjacency)
        component_of = {node: index for index, members in enumerate(components) for node in members}
        giant = components[0]
        fiedler = np.zeros(node_count)
        fiedler[giant] = fiedler_pair(adjacency[np.ix_(giant, giant)])[1]
        perron = perron_pair(adjacency)[1]
        limit = observation.communication_range * self.range_multiplier
        candidates = [node for node in observation.nodes if node not in excluded]

        scored: list[tuple[int, int, float, float, bool]] = []
        length: dict[tuple[int, int], float] = {}
        for index, source in enumerate(candidates):
            for target in candidates[index + 1 :]:
                distance = dist(observation.positions[source], observation.positions[target])
                if adjacency[source, target] or distance > limit:
                    continue
                length[(source, target)] = distance
                first, second = component_of[source], component_of[target]
                if first != second:
                    smaller = min(len(components[first]), len(components[second]))
                    gain = (2.0 if 0 in (first, second) else 1.0) + smaller / node_count
                    merge = True
                elif first == 0:
                    gain = float((fiedler[source] - fiedler[target]) ** 2)
                    merge = False
                else:
                    continue
                scored.append((source, target, gain, 2 * perron[source] * perron[target], merge))

        if not scored:
            return []
        fiedler_scale = max((gain for *_, gain, _, merge in scored if not merge), default=0.0)
        cost_scale = max(cost for *_, cost, _ in scored) or 1.0

        def normalised(item: tuple[int, int, float, float, bool]) -> float:
            _, _, gain, cost, merge = item
            relative_gain = gain if merge else (gain / fiedler_scale if fiedler_scale else 0.0)
            return relative_gain - self.link_penalty * cost / cost_scale

        # Equal scores prefer the shorter link, which needs less transmit power.
        ranked = sorted(
            scored,
            key=lambda item: (-round(normalised(item), 9), length[item[:2]], item[0], item[1]),
        )
        degrees = adjacency.sum(axis=1)
        selected: list[dict[str, object]] = []
        for item in ranked:
            source, target, gain, cost, merge = item
            score = normalised(item)
            if len(selected) >= budget or score <= 0:
                break
            if degrees[source] >= self.maximum_degree or degrees[target] >= self.maximum_degree:
                continue
            degrees[source] += 1
            degrees[target] += 1
            reason = (
                "bileşenleri birleştirir" if merge else f"λ₂ kazancı ≤ {gain:.4f}"
            ) + f"; λ₁ maliyeti ≥ {cost:.4f}"
            selected.append(
                {
                    "source": source,
                    "target": target,
                    "score": round(score, 6),
                    "merges_components": merge,
                    "reason": reason,
                }
            )
        return selected
