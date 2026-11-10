from __future__ import annotations

import numpy as np

from .spectral_shield import SpectralShieldAlgorithm


class RandomQuarantineAlgorithm(SpectralShieldAlgorithm):
    """Control group for the Perron ordering of Spektral Kalkan.

    Everything is inherited from Spektral Kalkan (budget, the same known infected UAVs,
    the same link repair) except the order of isolation, which is uniformly random. Any
    gap between the two methods is therefore the value of the Perron ordering alone.
    """

    name = "random_quarantine"

    def __init__(
        self,
        seed: int,
        budget: int,
        range_multiplier: float = 1.5,
        maximum_degree: int = 8,
        link_penalty: float = 1.0,
    ) -> None:
        super().__init__(budget, range_multiplier, maximum_degree, link_penalty)
        self.rng = np.random.default_rng(seed ^ 0xC0DE)

    def _rank_targets(self, nodes: list[int], perron: np.ndarray) -> list[int]:
        return [int(node) for node in self.rng.permutation(sorted(nodes))]

    def _quarantine_reason(self, node: int, radius: float, perron: np.ndarray) -> str:
        return f"rastgele kontrol karantinası (u²={perron[node] ** 2:.4f})"
