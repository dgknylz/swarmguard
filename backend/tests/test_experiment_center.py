import pytest

from swarmguard.config import DefenseStrategy, SimulationConfig
from swarmguard.dashboard.components.experiment_center import (
    build_experiment_plan,
    parse_seeds,
    summary_rows,
)
from swarmguard.experiments import run_monte_carlo


def test_seed_parser_accepts_delimiters_and_rejects_invalid_sets() -> None:
    assert parse_seeds("11, 23; 37") == (11, 23, 37)

    with pytest.raises(ValueError, match="benzersiz"):
        parse_seeds("11, 11")
    with pytest.raises(ValueError, match="negatif"):
        parse_seeds("-1, 2")
    with pytest.raises(ValueError, match="tam sayılar"):
        parse_seeds("alpha, 2")


def test_experiment_plan_calculates_run_and_step_budget() -> None:
    monte_carlo = build_experiment_plan(
        "monte_carlo",
        (DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK),
        (3, 5, 7),
        20,
    )
    ablation = build_experiment_plan("gtad_ablation", (), (3, 5), 20)

    assert monte_carlo.run_count == 6
    assert monte_carlo.simulated_steps == 120
    assert ablation.run_count == 8
    assert ablation.simulated_steps == 160


def test_summary_rows_expose_mean_and_confidence_interval() -> None:
    result = run_monte_carlo(
        SimulationConfig(node_count=8, steps=2, speed=0),
        (DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK),
        (3, 5),
    )
    rows = summary_rows(result, "mean_infected_ratio")

    assert len(rows) == 2
    assert {row["method"] for row in rows} == {"none", "gtad_risk"}
    assert all(row["ci95_low"] <= row["mean"] <= row["ci95_high"] for row in rows)
