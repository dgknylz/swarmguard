"""Headline findings of the project, computed once and shipped as a small JSON file.

``python -m swarmguard.findings`` regenerates ``dashboard/assets/findings.json`` from
the presets with fixed seeds; the Genel Bakış page and the README only display it.
"""

from __future__ import annotations

import json
from dataclasses import replace
from functools import lru_cache
from importlib import resources
from pathlib import Path

import numpy as np

from .config import DefenseStrategy, SimulationConfig
from .engine import SimulationEngine
from .experiments import SOFTWARE_VERSION, calculate_statistics, paired_tests, run_monte_carlo
from .presets import DEMO_CONFIG, PRESET_BY_SLUG, SHOWCASE_CONFIG
from .spectral import spectral_radius
from .theory import adjacency_sequence, extinction_threshold, initial_vector, simulate_replicates

SEEDS = tuple(range(1, 31))
ENDEMIC_LEVEL = 0.05
SWEEP_MULTIPLIERS = tuple(float(value) for value in np.round(np.geomspace(0.5, 8.0, 33), 4))
SWEEP_REPLICATES = 200
# The sweep runs every swarm for the same long horizon, so that the initial infection has
# decayed and the level measured at the end is the endemic one, not a transient.
SWEEP_HORIZON = 400
THRESHOLD_SLUGS = (
    "spectral-demo",
    "below-threshold",
    "rapid-outbreak",
    "fragile-network",
    "dense-swarm",
    "quarantine-defense",
    "mobility-stress",
)
ORDERING_SETTINGS = (
    ("Bol bütçe · kusursuz tespit", DEMO_CONFIG),
    (
        "Kusurlu tespit (q = 0.5)",
        replace(DEMO_CONFIG, detection_probability=0.5, defense_memory=3, initial_infected_count=4),
    ),
    ("Kısıtlı bütçe (B = 1)", replace(DEMO_CONFIG, defense_budget=1, initial_infected_count=6)),
    ("Kısıtlı bütçe + kusurlu tespit", SHOWCASE_CONFIG),
)
TABLE_SETTINGS = (
    ("perfect", "Kusursuz tespit · B = 2 · I₀ = 2", DEMO_CONFIG),
    ("constrained", "Kısıtlı bütçe · B = 1 · q = 0.5 · I₀ = 6", SHOWCASE_CONFIG),
)


def sweep_key(config: SimulationConfig) -> tuple[object, ...]:
    """The fields of a scenario that decide its threshold sweep (β and T do not)."""
    return (
        config.node_count,
        config.area_width,
        config.area_height,
        config.communication_range,
        config.speed,
        config.gamma,
        config.seed,
        config.initial_infected_count,
        config.attack_strategy.value,
    )


def threshold_sweep(
    config: SimulationConfig, *, replicates: int = SWEEP_REPLICATES
) -> dict[str, object]:
    """β* of Teorem 2 next to the β at which the undefended epidemic becomes endemic."""
    base = replace(
        config, defense_strategy=DefenseStrategy.NONE, defense_budget=0, steps=SWEEP_HORIZON
    )
    frames = SimulationEngine(base).run()
    adjacencies, initial = adjacency_sequence(frames), initial_vector(frames)
    radii = np.array([spectral_radius(adjacency) for adjacency in adjacencies])
    threshold = extinction_threshold(radii, base.gamma)
    tail = max(1, len(adjacencies) // 3)
    levels = []
    for multiplier in SWEEP_MULTIPLIERS:
        run = simulate_replicates(
            adjacencies, initial, multiplier * threshold, base.gamma, replicates, base.seed
        )
        levels.append(float(run.infected[:, -tail:].mean() / base.node_count))
    endemic = next(
        (m for m, level in zip(SWEEP_MULTIPLIERS, levels, strict=True) if level >= ENDEMIC_LEVEL),
        None,
    )
    return {
        "node_count": base.node_count,
        "gamma": base.gamma,
        "mean_spectral_radius": round(float(radii.mean()), 4),
        "threshold_beta": round(threshold, 5),
        "empirical_beta": None if endemic is None else round(endemic * threshold, 5),
        "tightness": endemic,
        "level_below_threshold": round(
            max(
                level
                for multiplier, level in zip(SWEEP_MULTIPLIERS, levels, strict=True)
                if multiplier < 1
            ),
            4,
        ),
        "replicates": replicates,
        "key": list(sweep_key(config)),
        "levels": [round(level, 4) for level in levels],
    }


def _means(result: dict[str, object], method: str, metric: str) -> list[float]:
    return [float(run[metric]) for run in result["runs"] if run["method"] == method]


def ordering_control(config: SimulationConfig) -> dict[str, object]:
    """Spektral Kalkan against the same defense with a random isolation order."""
    pair = (DefenseStrategy.SPECTRAL_SHIELD, DefenseStrategy.RANDOM_QUARANTINE)
    result = run_monte_carlo(config, pair, SEEDS)
    shield, control = (_means(result, item.value, "mean_infected_ratio") for item in pair)
    deltas = [first - second for first, second in zip(shield, control, strict=True)]
    tests = paired_tests(deltas, lower_is_better=True)
    return {
        "shield": calculate_statistics(shield),
        "control": calculate_statistics(control),
        "delta": calculate_statistics(deltas),
        **{key: tests[key] for key in ("p_value", "effect_size", "wins", "losses", "ties")},
    }


def _against_shield(
    result: dict[str, object], method: str, metric: str, *, lower_is_better: bool
) -> dict[str, object]:
    """Paired Spektral Kalkan − method differences over the seeds."""
    shield = _means(result, DefenseStrategy.SPECTRAL_SHIELD.value, metric)
    deltas = [first - second for first, second in zip(shield, _means(result, method, metric))]
    tests = paired_tests(deltas, lower_is_better=lower_is_better)
    return {
        "delta": calculate_statistics(deltas)["mean"],
        **{key: tests[key] for key in ("p_value", "wins", "losses", "ties")},
    }


def strategy_table(config: SimulationConfig) -> list[dict[str, object]]:
    result = run_monte_carlo(config, tuple(DefenseStrategy), SEEDS)
    return [
        {
            "method": summary["method"],
            "infection": summary["metrics"]["mean_infected_ratio"],
            "connectivity": summary["metrics"]["mean_largest_component_ratio"],
            "cost": summary["metrics"]["total_intervention_cost"]["mean"],
            "shield_infection": _against_shield(
                result, summary["method"], "mean_infected_ratio", lower_is_better=True
            ),
            "shield_connectivity": _against_shield(
                result, summary["method"], "mean_largest_component_ratio", lower_is_better=False
            ),
        }
        for summary in result["summaries"]
    ]


def compute_findings() -> dict[str, object]:
    return {
        "software_version": SOFTWARE_VERSION,
        "seeds": [SEEDS[0], SEEDS[-1]],
        "endemic_level": ENDEMIC_LEVEL,
        "sweep_multipliers": list(SWEEP_MULTIPLIERS),
        "sweep_replicates": SWEEP_REPLICATES,
        "sweep_horizon": SWEEP_HORIZON,
        "thresholds": [
            {
                "slug": slug,
                "title": PRESET_BY_SLUG[slug].title,
                **threshold_sweep(PRESET_BY_SLUG[slug].config),
            }
            for slug in THRESHOLD_SLUGS
        ],
        "ordering": [
            {"label": label, **ordering_control(config)} for label, config in ORDERING_SETTINGS
        ],
        "tables": [
            {"key": key, "label": label, "rows": strategy_table(config)}
            for key, label, config in TABLE_SETTINGS
        ],
    }


@lru_cache(maxsize=1)
def load_findings() -> dict[str, object]:
    asset = resources.files("swarmguard.dashboard").joinpath("assets", "findings.json")
    return json.loads(asset.read_text(encoding="utf-8"))


def main() -> None:
    target = Path(__file__).parent / "dashboard" / "assets" / "findings.json"
    findings = compute_findings()
    target.write_text(
        json.dumps(findings, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"{target} yazıldı")


if __name__ == "__main__":
    main()
