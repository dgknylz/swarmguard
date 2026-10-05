from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..config import AttackStrategy, DefenseStrategy, SimulationConfig


class SimulationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_count: int = Field(default=30, ge=2, le=500)
    area_width: float = Field(default=1_000.0, gt=0, le=100_000)
    area_height: float = Field(default=700.0, gt=0, le=100_000)
    communication_range: float = Field(default=230.0, gt=0, le=100_000)
    speed: float = Field(default=8.0, ge=0, le=1_000)
    beta: float = Field(default=0.18, ge=0, le=1)
    gamma: float = Field(default=0.06, ge=0, le=1)
    steps: int = Field(default=100, ge=1, le=10_000)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    initial_infected_count: int = Field(default=1, ge=1)
    attack_strategy: AttackStrategy = AttackStrategy.HIGHEST_DEGREE
    defense_strategy: DefenseStrategy = DefenseStrategy.NONE
    defense_budget: int = Field(default=2, ge=0, le=100)
    defense_range_multiplier: float = Field(default=1.5, ge=1, le=5)
    defense_max_degree: int = Field(default=8, ge=1, le=499)
    step_interval_ms: int = Field(default=50, ge=0, le=2_000)

    @model_validator(mode="after")
    def infected_count_fits_network(self) -> SimulationCreateRequest:
        if self.initial_infected_count > self.node_count:
            raise ValueError("initial_infected_count node_count değerini aşamaz")
        return self

    def to_core_config(self) -> SimulationConfig:
        return SimulationConfig(
            node_count=self.node_count,
            area_width=self.area_width,
            area_height=self.area_height,
            communication_range=self.communication_range,
            speed=self.speed,
            beta=self.beta,
            gamma=self.gamma,
            steps=self.steps,
            seed=self.seed,
            initial_infected_count=self.initial_infected_count,
            attack_strategy=self.attack_strategy,
            defense_strategy=self.defense_strategy,
            defense_budget=self.defense_budget,
            defense_range_multiplier=self.defense_range_multiplier,
            defense_max_degree=self.defense_max_degree,
        )


class SimulationCreateResponse(BaseModel):
    id: str
    status: str
    stream_url: str
    config: dict[str, Any]


class SimulationStatusResponse(BaseModel):
    id: str
    status: str
    latest_step: int
    frame_count: int
    error: str | None = None


class ControlResponse(BaseModel):
    id: str
    status: str


class ExperimentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: SimulationCreateRequest = Field(default_factory=SimulationCreateRequest)
    seeds: list[int] = Field(default_factory=lambda: [42, 43, 44], min_length=1, max_length=30)

    @model_validator(mode="after")
    def seeds_are_unique_and_valid(self) -> ExperimentRequest:
        if any(seed < 0 or seed > 2**32 - 1 for seed in self.seeds):
            raise ValueError("seed değerleri geçerli aralıkta olmalıdır")
        if len(set(self.seeds)) != len(self.seeds):
            raise ValueError("seed değerleri benzersiz olmalıdır")
        return self


class MonteCarloRequest(ExperimentRequest):
    strategies: list[DefenseStrategy] = Field(
        default_factory=lambda: list(DefenseStrategy), min_length=1
    )

    @model_validator(mode="after")
    def strategies_are_unique(self) -> MonteCarloRequest:
        if len(set(self.strategies)) != len(self.strategies):
            raise ValueError("stratejiler benzersiz olmalıdır")
        return self
