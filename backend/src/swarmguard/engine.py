from __future__ import annotations

from dataclasses import asdict, dataclass
from math import dist

import networkx as nx
import numpy as np
from numpy.typing import NDArray

from .algorithms.defense import (
    DefenseAction,
    DefenseAlgorithm,
    DefenseContext,
    DefenseReport,
    build_defense,
)
from .attacks import choose_initial_infected
from .config import SimulationConfig
from .metrics import calculate_metrics
from .network import build_graph, initialize_motion, move_with_reflection
from .sis import advance_sis

# Separate stream for detection draws, so imperfect detection never shifts the SIS
# random numbers that pair runs of different defenses on the same seed.
DETECTION_STREAM = 0xD37EC7


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
    # Infected UAVs the defender knew about when it acted in this step.
    detected: tuple[int, ...] = ()
    # Links the defense added to, or removed from, the range graph in this step.
    added_edges: tuple[tuple[int, int], ...] = ()
    removed_edges: tuple[tuple[int, int], ...] = ()
    quarantined: tuple[int, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "step": self.step,
            "positions": self.positions,
            "edges": self.edges,
            "infected": self.infected,
            "metrics": self.metrics,
            "events": [asdict(event) for event in self.events],
            "defense_report": self.defense_report,
            "detected": self.detected,
            "added_edges": self.added_edges,
            "removed_edges": self.removed_edges,
            "quarantined": self.quarantined,
        }


def _edge_set(graph: nx.Graph) -> set[tuple[int, int]]:
    return {(min(a, b), max(a, b)) for a, b in graph.edges}


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
        self.detection_rng = np.random.default_rng([config.seed, DETECTION_STREAM])
        self.detected: set[int] = set()
        self._active_actions: list[tuple[DefenseAction, int]] = []

    def _frame(
        self,
        events: tuple[SimulationEvent, ...] = (),
        defense_report: DefenseReport | None = None,
        *,
        detected: set[int] | None = None,
        added_edges: tuple[tuple[int, int], ...] = (),
        removed_edges: tuple[tuple[int, int], ...] = (),
        quarantined: set[int] | None = None,
    ) -> SimulationFrame:
        return SimulationFrame(
            step=self.step_number,
            positions=tuple((float(x), float(y)) for x, y in self.positions),
            edges=tuple(sorted((min(a, b), max(a, b)) for a, b in self.graph.edges)),
            infected=tuple(sorted(self.infected)),
            metrics=calculate_metrics(self.graph, self.infected),
            events=events,
            defense_report=defense_report.to_dict() if defense_report else None,
            detected=tuple(sorted(detected or ())),
            added_edges=added_edges,
            removed_edges=removed_edges,
            quarantined=tuple(sorted(quarantined or ())),
        )

    def initial_frame(self) -> SimulationFrame:
        return self._frame(
            tuple(SimulationEvent("initial_infection", node) for node in sorted(self.infected))
        )

    def _observe_infections(self) -> set[int]:
        """Update the defender's knowledge of the infected UAVs.

        A detected UAV stays known until it recovers; every undetected infected UAV is
        found with probability ``detection_probability`` per step.
        """
        self.detected &= self.infected
        if self.config.detection_probability >= 1:
            self.detected = set(self.infected)
        else:
            for node in sorted(self.infected - self.detected):
                if self.detection_rng.random() < self.config.detection_probability:
                    self.detected.add(node)
        return set(self.detected)

    def _apply_remembered_actions(self) -> set[int]:
        """Re-apply defense actions that are still in force; returns isolated UAVs."""
        self._active_actions = [
            (action, expires)
            for action, expires in self._active_actions
            if expires > self.step_number
        ]
        quarantined = {
            action.source
            for action, _ in self._active_actions
            if action.action_type == "quarantine_node"
        }
        link_limit = self.config.communication_range * self.config.defense_range_multiplier
        for action, _ in self._active_actions:
            source, target = action.source, action.target
            if action.action_type == "remove_edge" and self.graph.has_edge(source, target):
                self.graph.remove_edge(source, target)
            elif (
                action.action_type == "add_edge"
                and target is not None
                and source not in quarantined
                and target not in quarantined
                and dist(self.positions[source], self.positions[target]) <= link_limit
            ):
                self.graph.add_edge(source, target)
        for node in quarantined:
            self.graph.remove_edges_from(list(self.graph.edges(node)))
        return quarantined

    def step(self) -> SimulationFrame:
        self.positions, self.velocities = move_with_reflection(
            self.positions,
            self.velocities,
            self.config.area_width,
            self.config.area_height,
        )
        self.graph = build_graph(self.positions, self.config.communication_range)
        self.step_number += 1
        range_edges = _edge_set(self.graph)
        quarantined = self._apply_remembered_actions()
        known_infected = self._observe_infections()
        defense_report = self.defense.execute(
            DefenseContext(
                graph=self.graph,
                infected=frozenset(known_infected),
                step=self.step_number,
                communication_range=self.config.communication_range,
                positions=tuple((float(x), float(y)) for x, y in self.positions),
                quarantined=frozenset(quarantined),
            )
        )
        expires = self.step_number + self.config.defense_memory
        self._active_actions.extend((action, expires) for action in defense_report.applied_actions)
        quarantined |= {
            action.source
            for action in defense_report.applied_actions
            if action.action_type == "quarantine_node"
        }
        defended_edges = _edge_set(self.graph)

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
        return self._frame(
            health_events + defense_events,
            defense_report,
            detected=known_infected,
            added_edges=tuple(sorted(defended_edges - range_edges)),
            removed_edges=tuple(sorted(range_edges - defended_edges)),
            quarantined=quarantined,
        )

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
