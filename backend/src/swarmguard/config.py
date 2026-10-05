from dataclasses import dataclass
from enum import Enum


class AttackStrategy(str, Enum):
    RANDOM = "random"
    HIGHEST_DEGREE = "highest_degree"
    HIGHEST_BETWEENNESS = "highest_betweenness"


class DefenseStrategy(str, Enum):
    NONE = "none"
    RANDOM_REWIRING = "random_rewiring"
    CENTRALITY_QUARANTINE = "centrality_quarantine"
    GTAD_RISK = "gtad_risk"


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    node_count: int = 30
    area_width: float = 1_000.0
    area_height: float = 700.0
    communication_range: float = 230.0
    speed: float = 8.0
    beta: float = 0.18
    gamma: float = 0.06
    steps: int = 100
    seed: int = 42
    initial_infected_count: int = 1
    attack_strategy: AttackStrategy = AttackStrategy.HIGHEST_DEGREE
    defense_strategy: DefenseStrategy = DefenseStrategy.NONE
    defense_budget: int = 2
    defense_range_multiplier: float = 1.5
    defense_max_degree: int = 8

    def __post_init__(self) -> None:
        if self.node_count < 2:
            raise ValueError("node_count en az 2 olmalıdır")
        if self.area_width <= 0 or self.area_height <= 0:
            raise ValueError("Görev alanı boyutları pozitif olmalıdır")
        if self.communication_range <= 0:
            raise ValueError("communication_range pozitif olmalıdır")
        if self.speed < 0:
            raise ValueError("speed negatif olamaz")
        if not 0 <= self.beta <= 1 or not 0 <= self.gamma <= 1:
            raise ValueError("beta ve gamma [0, 1] aralığında olmalıdır")
        if self.steps < 1:
            raise ValueError("steps en az 1 olmalıdır")
        if not 1 <= self.initial_infected_count <= self.node_count:
            raise ValueError("initial_infected_count geçerli düğüm aralığında olmalıdır")
        if self.defense_budget < 0:
            raise ValueError("defense_budget negatif olamaz")
        if self.defense_range_multiplier < 1:
            raise ValueError("defense_range_multiplier en az 1 olmalıdır")
        if self.defense_max_degree < 1:
            raise ValueError("defense_max_degree en az 1 olmalıdır")
