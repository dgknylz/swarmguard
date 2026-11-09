from __future__ import annotations

from math import dist

import numpy as np

from .base import (
    DefenseAction,
    DefenseAlgorithm,
    DefenseContext,
    DefenseDecision,
    DefenseObservation,
)
from .observation import build_observation


class RandomAdditionAlgorithm(DefenseAlgorithm):
    """Control group for link-adding defenses.

    Uses GTAD's budget, range and degree caps but picks healthy links uniformly at
    random, so any gain a scored method shows beyond this one comes from its scoring
    and not from the act of adding links.
    """

    name = "random_addition"

    def __init__(
        self, seed: int, budget: int, range_multiplier: float = 1.5, maximum_degree: int = 8
    ) -> None:
        self.rng = np.random.default_rng(seed ^ 0xADD)
        self.budget = budget
        self.range_multiplier = range_multiplier
        self.maximum_degree = maximum_degree

    def observe(self, context: DefenseContext) -> DefenseObservation:
        return build_observation(context, include_betweenness=False)

    def decide(self, observation: DefenseObservation) -> DefenseDecision:
        existing = set(observation.edges)
        degrees = dict(observation.degrees)
        isolated = set(observation.quarantined)
        healthy = [node for node in observation.healthy if node not in isolated]
        limit = observation.communication_range * self.range_multiplier
        candidates = [
            (source, target)
            for index, source in enumerate(healthy)
            for target in healthy[index + 1 :]
            if (source, target) not in existing
            and observation.positions
            and dist(observation.positions[source], observation.positions[target]) <= limit
        ]
        self.rng.shuffle(candidates)

        actions: list[DefenseAction] = []
        for source, target in candidates:
            if len(actions) >= self.budget:
                break
            if degrees[source] >= self.maximum_degree or degrees[target] >= self.maximum_degree:
                continue
            degrees[source] += 1
            degrees[target] += 1
            actions.append(DefenseAction("add_edge", source, target, "rastgele kontrol bağlantısı"))

        return DefenseDecision(
            algorithm=self.name,
            step=observation.step,
            actions=tuple(actions),
            metadata={"candidate_count": len(candidates)},
        )
