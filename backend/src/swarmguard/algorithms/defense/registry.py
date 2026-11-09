from ...config import DefenseStrategy
from .base import DefenseAlgorithm
from .centrality_quarantine import CentralityQuarantineAlgorithm
from .gtad_risk import GtadRiskAlgorithm
from .none import NoDefenseAlgorithm
from .random_addition import RandomAdditionAlgorithm
from .random_rewiring import RandomRewiringAlgorithm
from .spectral_shield import SpectralShieldAlgorithm


def build_defense(
    strategy: DefenseStrategy,
    *,
    seed: int = 0,
    budget: int = 2,
    range_multiplier: float = 1.5,
    maximum_degree: int = 8,
) -> DefenseAlgorithm:
    if strategy is DefenseStrategy.NONE:
        return NoDefenseAlgorithm()
    if strategy is DefenseStrategy.RANDOM_REWIRING:
        return RandomRewiringAlgorithm(seed, budget, range_multiplier)
    if strategy is DefenseStrategy.CENTRALITY_QUARANTINE:
        return CentralityQuarantineAlgorithm(budget)
    if strategy is DefenseStrategy.GTAD_RISK:
        return GtadRiskAlgorithm(budget, range_multiplier, maximum_degree)
    if strategy is DefenseStrategy.SPECTRAL_SHIELD:
        return SpectralShieldAlgorithm(budget, range_multiplier, maximum_degree)
    if strategy is DefenseStrategy.RANDOM_ADDITION:
        return RandomAdditionAlgorithm(seed, budget, range_multiplier, maximum_degree)
    raise ValueError(f"Desteklenmeyen savunma stratejisi: {strategy}")
