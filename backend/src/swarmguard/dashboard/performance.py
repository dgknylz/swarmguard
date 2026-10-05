from __future__ import annotations

from copy import deepcopy
from functools import lru_cache

from ..config import DefenseStrategy, SimulationConfig
from ..engine import SimulationEngine, SimulationFrame
from ..experiments import run_gtad_ablation, run_monte_carlo


@lru_cache(maxsize=24)
def _simulation_cache(config: SimulationConfig) -> tuple[SimulationFrame, ...]:
    return tuple(SimulationEngine(config).run())


@lru_cache(maxsize=12)
def _monte_carlo_cache(
    config: SimulationConfig,
    strategies: tuple[DefenseStrategy, ...],
    seeds: tuple[int, ...],
) -> dict[str, object]:
    return run_monte_carlo(config, strategies, seeds)


@lru_cache(maxsize=12)
def _ablation_cache(config: SimulationConfig, seeds: tuple[int, ...]) -> dict[str, object]:
    return run_gtad_ablation(config, seeds)


def cached_simulation(config: SimulationConfig) -> list[SimulationFrame]:
    return list(_simulation_cache(config))


def cached_monte_carlo(
    config: SimulationConfig,
    strategies: tuple[DefenseStrategy, ...],
    seeds: tuple[int, ...],
) -> dict[str, object]:
    return deepcopy(_monte_carlo_cache(config, strategies, seeds))


def cached_gtad_ablation(config: SimulationConfig, seeds: tuple[int, ...]) -> dict[str, object]:
    return deepcopy(_ablation_cache(config, seeds))


def clear_performance_caches() -> None:
    _simulation_cache.cache_clear()
    _monte_carlo_cache.cache_clear()
    _ablation_cache.cache_clear()


def performance_cache_info() -> dict[str, object]:
    return {
        "simulation": _simulation_cache.cache_info(),
        "monte_carlo": _monte_carlo_cache.cache_info(),
        "gtad_ablation": _ablation_cache.cache_info(),
    }
