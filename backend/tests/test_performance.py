from swarmguard.config import DefenseStrategy, SimulationConfig
from swarmguard.dashboard.performance import (
    cached_gtad_ablation,
    cached_monte_carlo,
    cached_simulation,
    clear_performance_caches,
    performance_cache_info,
)


def setup_function() -> None:
    clear_performance_caches()


def test_simulation_cache_reuses_identical_configurations() -> None:
    config = SimulationConfig(node_count=8, steps=2, speed=0, seed=9)

    first = cached_simulation(config)
    second = cached_simulation(config)
    info = performance_cache_info()["simulation"]

    assert first == second
    assert first is not second
    assert info.misses == 1
    assert info.hits == 1


def test_monte_carlo_cache_returns_isolated_mutable_results() -> None:
    config = SimulationConfig(node_count=8, steps=2, speed=0)
    strategies = (DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK)
    seeds = (3, 5)

    first = cached_monte_carlo(config, strategies, seeds)
    first["run_count"] = -1
    second = cached_monte_carlo(config, strategies, seeds)
    info = performance_cache_info()["monte_carlo"]

    assert second["run_count"] == 4
    assert info.misses == 1
    assert info.hits == 1


def test_ablation_cache_is_keyed_by_scenario_and_seed_tuple() -> None:
    config = SimulationConfig(node_count=8, steps=2, speed=0)

    first = cached_gtad_ablation(config, (3,))
    second = cached_gtad_ablation(config, (5,))
    repeated = cached_gtad_ablation(config, (3,))
    info = performance_cache_info()["gtad_ablation"]

    assert first["experiment_id"] == repeated["experiment_id"]
    assert first["experiment_id"] != second["experiment_id"]
    assert info.misses == 2
    assert info.hits == 1


def test_clear_performance_caches_resets_all_cache_statistics() -> None:
    config = SimulationConfig(node_count=8, steps=1, speed=0)
    cached_simulation(config)
    clear_performance_caches()

    assert all(
        info.hits == 0 and info.misses == 0 and info.currsize == 0
        for info in performance_cache_info().values()
    )
