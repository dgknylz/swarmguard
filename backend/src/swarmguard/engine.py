from __future__ import annotations

from dataclasses import asdict, dataclass

import networkx as nx
import numpy as np
from numpy.typing import NDArray

from .algorithms.defense import DefenseAlgorithm, DefenseContext, DefenseReport, build_defense
from .attacks import choose_initial_infected
from .config import SimulationConfig
from .metrics import calculate_metrics
from .network import build_graph, initialize_motion, move_with_reflection
from .sis import advance_sis


@dataclass(frozen=True, slots=True)
class SimulationEvent:
    event_type: str
    node_id: int
    target_node_id: int | None = None
    algorithm: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class SimulationFrame:
    step: int
    positions: tuple[tuple[float, float], ...]
    edges: tuple[tuple[int, int], ...]
    infected: tuple[int, ...]
    metrics: dict[str, float | int]
    events: tuple[SimulationEvent, ...]
    defense_report: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "step": self.step,
            "positions": self.positions,
            "edges": self.edges,
            "infected": self.infected,
            "metrics": self.metrics,
            "events": [asdict(event) for event in self.events],
            "defense_report": self.defense_report,
        }


class SimulationEngine:
    def __init__(self, config: SimulationConfig, defense: DefenseAlgorithm | None = None):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.positions, self.velocities = initialize_motion(
            config.node_count,
            config.area_width,
            config.area_height,
            config.speed,
            self.rng,
        )
        self.graph = build_graph(self.positions, config.communication_range)
        self.infected = choose_initial_infected(
            self.graph,
            config.attack_strategy,
            config.initial_infected_count,
            self.rng,
        )
        self.step_number = 0
        self.defense = defense or build_defense(
            config.defense_strategy,
            seed=config.seed,
            budget=config.defense_budget,
            range_multiplier=config.defense_range_multiplier,
            maximum_degree=config.defense_max_degree,
        )

    def _frame(
        self,
        events: tuple[SimulationEvent, ...] = (),
        defense_report: DefenseReport | None = None,
    ) -> SimulationFrame:
        return SimulationFrame(
            step=self.step_number,
            positions=tuple((float(x), float(y)) for x, y in self.positions),
            edges=tuple(sorted((min(a, b), max(a, b)) for a, b in self.graph.edges)),
            infected=tuple(sorted(self.infected)),
            metrics=calculate_metrics(self.graph, self.infected),
            events=events,
            defense_report=defense_report.to_dict() if defense_report else None,
        )

    def initial_frame(self) -> SimulationFrame:
        return self._frame(
            tuple(SimulationEvent("initial_infection", node) for node in sorted(self.infected))
        )

    def step(self) -> SimulationFrame:
        self.positions, self.velocities = move_with_reflection(
            self.positions,
            self.velocities,
            self.config.area_width,
            self.config.area_height,
        )
        self.graph = build_graph(self.positions, self.config.communication_range)
        self.step_number += 1
        defense_report = self.defense.execute(
            DefenseContext(
                graph=self.graph,
                infected=frozenset(self.infected),
                step=self.step_number,
                communication_range=self.config.communication_range,
                positions=tuple((float(x), float(y)) for x, y in self.positions),
            )
        )
        self.infected, newly_infected, recovered = advance_sis(
            self.graph,
            self.infected,
            self.config.beta,
            self.config.gamma,
            self.rng,
        )
        health_events = tuple(
            [SimulationEvent("infected", node) for node in sorted(newly_infected)]
            + [SimulationEvent("recovered", node) for node in sorted(recovered)]
        )
        defense_events = tuple(
            SimulationEvent(
                event_type=action.action_type,
                node_id=action.source,
                target_node_id=action.target,
                algorithm=defense_report.algorithm,
                detail=action.reason or None,
            )
            for action in defense_report.applied_actions
        )
        return self._frame(health_events + defense_events, defense_report)

    def run(self) -> list[SimulationFrame]:
        frames = [self.initial_frame()]
        frames.extend(self.step() for _ in range(self.config.steps))
        return frames

    @property
    def position_array(self) -> NDArray[np.float64]:
        return self.positions.copy()

    @property
    def current_graph(self) -> nx.Graph:
        return self.graph.copy()
