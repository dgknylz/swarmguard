from swarmguard.config import DefenseStrategy, SimulationConfig
from swarmguard.dashboard.components.comparison_panel import (
    baseline_method,
    build_comparison_rows,
    build_normalized_scorecard,
)
from swarmguard.experiments import RESULT_METRICS, run_gtad_ablation, run_monte_carlo


def test_comparison_ranking_respects_metric_direction() -> None:
    result = run_monte_carlo(
        SimulationConfig(node_count=8, steps=3, speed=0),
        (DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK),
        (3, 5),
    )
    infection_rows = build_comparison_rows(result, "mean_infected_ratio")
    connectivity_rows = build_comparison_rows(result, "mean_largest_component_ratio")

    assert [row.mean for row in infection_rows] == sorted(row.mean for row in infection_rows)
    assert [row.mean for row in connectivity_rows] == sorted(
        (row.mean for row in connectivity_rows), reverse=True
    )
    assert {row.rank for row in infection_rows} == {1, 2}


def test_comparison_uses_kind_specific_baseline_and_paired_deltas() -> None:
    config = SimulationConfig(node_count=8, steps=2, speed=0)
    monte_carlo = run_monte_carlo(
        config,
        (DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK),
        (3, 5),
    )
    ablation = run_gtad_ablation(config, (3, 5))

    assert baseline_method(monte_carlo) == "none"
    assert baseline_method(ablation) == "full"
    rows = build_comparison_rows(monte_carlo, "mean_infected_ratio")
    assert next(row for row in rows if row.is_baseline).paired_delta == 0
    assert all(row.paired_delta is not None for row in rows)


def test_normalized_scorecard_is_bounded_and_ranked() -> None:
    result = run_gtad_ablation(
        SimulationConfig(node_count=8, steps=2, speed=0),
        (3, 5),
    )
    scorecard = build_normalized_scorecard(result)

    assert len(scorecard) == 4
    assert [row["overall"] for row in scorecard] == sorted(
        (row["overall"] for row in scorecard), reverse=True
    )
    assert all(set(row["scores"]) == set(RESULT_METRICS) for row in scorecard)
    assert all(0 <= score <= 1 for row in scorecard for score in row["scores"].values())
