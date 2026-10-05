from __future__ import annotations

from itertools import combinations
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


class RandomRewiringAlgorithm(DefenseAlgorithm):
    name = "random_rewiring"

    def __init__(self, seed: int, budget: int, range_multiplier: float = 1.5):
        self.rng = np.random.default_rng(seed ^ 0x5A17)
        self.budget = budget
        self.range_multiplier = range_multiplier

    def observe(self, context: DefenseContext) -> DefenseObservation:
        return build_observation(context)

    def decide(self, observation: DefenseObservation) -> DefenseDecision:
        edge_set = set(observation.edges)
        infected = set(observation.infected)
        risky_edges = [
            edge for edge in observation.edges if (edge[0] in infected) != (edge[1] in infected)
        ]
        safe_candidates = [
            (a, b)
            for a, b in combinations(observation.healthy, 2)
            if (a, b) not in edge_set
            and observation.positions
            and dist(observation.positions[a], observation.positions[b])
            <= observation.communication_range * self.range_multiplier
        ]
        self.rng.shuffle(risky_edges)
        self.rng.shuffle(safe_candidates)
        pair_count = min(len(risky_edges), len(safe_candidates), self.budget // 2)
        actions: list[DefenseAction] = []
        for risky, safe in zip(risky_edges[:pair_count], safe_candidates[:pair_count]):
            actions.extend(
                (
                    DefenseAction("remove_edge", risky[0], risky[1], "enfeksiyon temasını kes"),
                    DefenseAction("add_edge", safe[0], safe[1], "sağlıklı rotayı güçlendir"),
                )
            )
        return DefenseDecision(
            algorithm=self.name,
            step=observation.step,
            actions=tuple(actions),
            metadata={"candidate_count": len(safe_candidates), "rewiring_count": pair_count},
        )
