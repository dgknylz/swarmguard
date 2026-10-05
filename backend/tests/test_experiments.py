import pytest

from swarmguard.algorithms.defense.gtad_candidates import ScoreWeights
from swarmguard.config import DefenseStrategy, SimulationConfig
from swarmguard.experiments import (
    calculate_statistics,
    run_gtad_ablation,
    run_monte_carlo,
)


def test_score_weights_are_normalized_for_ablation() -> None:
    weights = ScoreWeights(2, 1, 1)

    assert weights.to_dict() == {
        "connectivity": 0.5,
        "safety": 0.25,
        "distance": 0.25,
    }


def test_student_t_confidence_interval_contains_sample_mean() -> None:
    statistics = calculate_statistics([0.2, 0.4, 0.6])

    assert statistics["n"] == 3
    assert statistics["mean"] == pytest.approx(0.4)
    assert statistics["ci95_low"] < statistics["mean"] < statistics["ci95_high"]


def test_gtad_ablation_runs_every_variant_with_paired_seeds() -> None:
    result = run_gtad_ablation(
        SimulationConfig(node_count=8, steps=2, speed=0, defense_budget=1),
        [4, 9],
    )

    assert result["run_count"] == 8
    assert len(result["summaries"]) == 4
    assert {comparison["pair_count"] for comparison in result["paired_comparisons"]} == {2}


def test_monte_carlo_is_reproducible_and_pairs_each_seed() -> None:
    config = SimulationConfig(node_count=8, steps=2, speed=0)
    strategies = [DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK]

    first = run_monte_carlo(config, strategies, [3, 5])
    second = run_monte_carlo(config, strategies, [3, 5])

    assert first == second
    assert first["experiment_id"] == second["experiment_id"]
    assert first["manifest"]["fingerprint"].startswith("sha256:")
    assert first["run_count"] == 4
    assert first["summaries"][0]["metrics"]["mean_infected_ratio"]["n"] == 2
    assert first["paired_comparisons"][0]["pair_count"] == 2
    assert "ci95_low" in first["paired_comparisons"][0]["delta_statistics"]["mean_infected_ratio"]
    assert [pair["seed"] for pair in first["paired_comparisons"][0]["pairs"]] == [3, 5]
