from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, replace
from hashlib import sha256
from json import dumps
from math import sqrt
from statistics import fmean, pvariance, stdev

from scipy.stats import binomtest
from scipy.stats import t as student_t

from .algorithms.defense.gtad_candidates import ScoreWeights
from .algorithms.defense.gtad_risk import GtadRiskAlgorithm
from .config import DefenseStrategy, SimulationConfig
from .engine import SimulationEngine, SimulationFrame

SOFTWARE_VERSION = "2.0.0"

RESULT_METRICS = (
    "final_infected_ratio",
    "peak_infected_ratio",
    "mean_infected_ratio",
    "mean_largest_component_ratio",
    "mean_global_efficiency",
    "mean_algebraic_connectivity",
    "mean_spectral_radius",
    "total_intervention_cost",
)

LOWER_IS_BETTER = frozenset(
    {
        "final_infected_ratio",
        "peak_infected_ratio",
        "mean_infected_ratio",
        "mean_spectral_radius",
        "total_intervention_cost",
    }
)

# Paired differences closer to zero than this count as ties in the sign test.
TIE_TOLERANCE = 1e-12

GTAD_ABLATIONS = {
    "full": ScoreWeights(0.50, 0.30, 0.20),
    "without_connectivity": ScoreWeights(0.00, 0.60, 0.40),
    "without_safety": ScoreWeights(0.714286, 0.00, 0.285714),
    "without_distance": ScoreWeights(0.625, 0.375, 0.00),
}


def _scenario_dict(config: SimulationConfig) -> dict[str, object]:
    return {
        key: value.value if hasattr(value, "value") else value
        for key, value in asdict(config).items()
    }


def calculate_statistics(values: Iterable[float]) -> dict[str, float | int]:
    sample = tuple(float(value) for value in values)
    if not sample:
        raise ValueError("İstatistik için en az bir değer gereklidir")

    mean = fmean(sample)
    sample_std = stdev(sample) if len(sample) > 1 else 0.0
    margin = (
        float(student_t.ppf(0.975, len(sample) - 1)) * sample_std / sqrt(len(sample))
        if len(sample) > 1
        else 0.0
    )
    return {
        "n": len(sample),
        "mean": mean,
        "std": sample_std,
        "ci95_low": mean - margin,
        "ci95_high": mean + margin,
    }


def paired_tests(
    deltas: Sequence[float], *, lower_is_better: bool
) -> dict[str, float | int | None]:
    """Two-sided paired t-test, Cohen's d_z and an exact sign test on method − baseline.

    ``wins`` counts seeds where the method beat the baseline in the metric's preferred
    direction; ties are excluded from the sign test.
    """
    sample = tuple(float(delta) for delta in deltas)
    count = len(sample)
    mean = fmean(sample) if sample else 0.0
    deviation = stdev(sample) if count > 1 else 0.0
    if count < 2:
        p_value = effect_size = None
    elif deviation == 0:
        p_value = 1.0 if abs(mean) <= TIE_TOLERANCE else 0.0
        effect_size = None
    else:
        statistic = mean / (deviation / sqrt(count))
        p_value = float(2 * student_t.sf(abs(statistic), count - 1))
        effect_size = mean / deviation

    better = [
        delta < -TIE_TOLERANCE if lower_is_better else delta > TIE_TOLERANCE for delta in sample
    ]
    worse = [
        delta > TIE_TOLERANCE if lower_is_better else delta < -TIE_TOLERANCE for delta in sample
    ]
    wins, losses = sum(better), sum(worse)
    sign_p_value = float(binomtest(wins, wins + losses, 0.5).pvalue) if wins + losses else 1.0
    return {
        "p_value": p_value,
        "effect_size": effect_size,
        "wins": wins,
        "losses": losses,
        "ties": count - wins - losses,
        "sign_p_value": sign_p_value,
    }


def holm_adjust(p_values: Sequence[float | None]) -> list[float | None]:
    """Holm–Bonferroni step-down adjustment; ``None`` entries are left untouched."""
    ranked = sorted((value, index) for index, value in enumerate(p_values) if value is not None)
    adjusted: list[float | None] = [None] * len(p_values)
    running = 0.0
    for rank, (value, index) in enumerate(ranked):
        running = max(running, min(1.0, (len(ranked) - rank) * value))
        adjusted[index] = running
    return adjusted


def _variance_reduction(baseline: Sequence[float], method: Sequence[float]) -> float | None:
    """Share of Var(method) + Var(baseline) removed by pairing runs on the same seed.

    Var(X − Y) = Var X + Var Y − 2·Cov(X, Y): common random numbers make the covariance
    positive, which is why paired differences need far fewer seeds.
    """
    if len(baseline) < 2:
        return None
    independent = pvariance(baseline) + pvariance(method)
    if independent <= 0:
        return None
    paired = pvariance([b - a for a, b in zip(baseline, method, strict=True)])
    return 1 - paired / independent


def _finalize_result(
    result: dict[str, object],
    base_config: SimulationConfig,
    methods: list[str],
    *,
    variants: dict[str, dict[str, float]] | None = None,
) -> dict[str, object]:
    manifest_core: dict[str, object] = {
        "schema_version": "1.0",
        "software": {"name": "swarmguard", "version": SOFTWARE_VERSION},
        "experiment": {
            "kind": result["kind"],
            "scenario": _scenario_dict(base_config),
            "seeds": result["seeds"],
            "methods": methods,
            "variants": variants or {},
            "pairing_key": "seed",
            "metrics": list(RESULT_METRICS),
            "confidence_level": 0.95,
            "confidence_method": "two-sided Student-t interval",
        },
    }
    canonical = dumps(
        manifest_core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    fingerprint = sha256(canonical).hexdigest()
    manifest = {
        **manifest_core,
        "fingerprint": f"sha256:{fingerprint}",
    }
    result.update(
        {
            "experiment_id": fingerprint[:16],
            "scenario": _scenario_dict(base_config),
            "manifest": manifest,
        }
    )
    return result


def _summarize_run(
    method: str, seed: int, frames: list[SimulationFrame]
) -> dict[str, str | int | float]:
    measured = frames[1:] or frames
    infected = [float(frame.metrics["infected_ratio"]) for frame in measured]
    intervention_cost = sum(
        float(frame.defense_report["intervention_cost"])
        for frame in measured
        if frame.defense_report is not None
    )
    return {
        "method": method,
        "seed": seed,
        "final_infected_ratio": infected[-1],
        "peak_infected_ratio": max(infected),
        "mean_infected_ratio": fmean(infected),
        "mean_largest_component_ratio": fmean(
            float(frame.metrics["largest_component_ratio"]) for frame in measured
        ),
        "mean_global_efficiency": fmean(
            float(frame.metrics["global_efficiency"]) for frame in measured
        ),
        "mean_algebraic_connectivity": fmean(
            float(frame.metrics["algebraic_connectivity"]) for frame in measured
        ),
        "mean_spectral_radius": fmean(
            float(frame.metrics["spectral_radius"]) for frame in measured
        ),
        "total_intervention_cost": intervention_cost,
    }


def _aggregate(runs: list[dict[str, str | int | float]]) -> list[dict[str, object]]:
    by_method: dict[str, list[dict[str, str | int | float]]] = defaultdict(list)
    for run in runs:
        by_method[str(run["method"])].append(run)

    summaries: list[dict[str, object]] = []
    for method, method_runs in by_method.items():
        metrics = {}
        for metric in RESULT_METRICS:
            values = [float(run[metric]) for run in method_runs]
            metrics[metric] = calculate_statistics(values)
        summaries.append({"method": method, "run_count": len(method_runs), "metrics": metrics})
    return summaries


def _paired_comparisons(
    runs: list[dict[str, str | int | float]], baseline: str
) -> list[dict[str, object]]:
    by_key = {(str(run["method"]), int(run["seed"])): run for run in runs}
    methods = sorted({str(run["method"]) for run in runs if run["method"] != baseline})
    seeds = sorted({int(run["seed"]) for run in runs if run["method"] == baseline})
    comparisons: list[dict[str, object]] = []

    for method in methods:
        pairs = []
        for seed in seeds:
            baseline_run = by_key.get((baseline, seed))
            method_run = by_key.get((method, seed))
            if baseline_run is None or method_run is None:
                continue
            deltas = {
                metric: float(method_run[metric]) - float(baseline_run[metric])
                for metric in RESULT_METRICS
            }
            pairs.append({"seed": seed, "deltas": deltas})

        delta_statistics: dict[str, dict[str, object]] = {}
        for metric in RESULT_METRICS if pairs else ():
            deltas = [float(pair["deltas"][metric]) for pair in pairs]
            baseline_values = [float(by_key[(baseline, pair["seed"])][metric]) for pair in pairs]
            method_values = [float(by_key[(method, pair["seed"])][metric]) for pair in pairs]
            delta_statistics[metric] = {
                **calculate_statistics(deltas),
                **paired_tests(deltas, lower_is_better=metric in LOWER_IS_BETTER),
                "variance_reduction": _variance_reduction(baseline_values, method_values),
            }
        mean_deltas = {
            metric: float(statistics["mean"]) for metric, statistics in delta_statistics.items()
        }
        comparisons.append(
            {
                "baseline": baseline,
                "method": method,
                "pair_count": len(pairs),
                "pairs": pairs,
                "mean_deltas": mean_deltas,
                "delta_statistics": delta_statistics,
            }
        )

    # Every method is tested against the same baseline, so each metric forms one
    # family of hypotheses for the Holm correction.
    for metric in RESULT_METRICS:
        family = [comparison["delta_statistics"].get(metric) for comparison in comparisons]
        adjusted = holm_adjust([item["p_value"] if item else None for item in family])
        for item, value in zip(family, adjusted, strict=True):
            if item is not None:
                item["p_value_holm"] = value
    return comparisons


def run_monte_carlo(
    base_config: SimulationConfig,
    strategies: Iterable[DefenseStrategy],
    seeds: Iterable[int],
) -> dict[str, object]:
    strategy_list = tuple(dict.fromkeys(strategies))
    seed_list = tuple(dict.fromkeys(seeds))
    if not strategy_list or not seed_list:
        raise ValueError("En az bir strateji ve seed gereklidir")

    runs = []
    for strategy in strategy_list:
        for seed in seed_list:
            config = replace(base_config, seed=seed, defense_strategy=strategy)
            runs.append(_summarize_run(strategy.value, seed, SimulationEngine(config).run()))

    baseline = DefenseStrategy.NONE.value
    result = {
        "kind": "monte_carlo",
        "strategies": [strategy.value for strategy in strategy_list],
        "seeds": list(seed_list),
        "run_count": len(runs),
        "runs": runs,
        "summaries": _aggregate(runs),
        "paired_comparisons": (
            _paired_comparisons(runs, baseline) if DefenseStrategy.NONE in strategy_list else []
        ),
    }
    return _finalize_result(
        result,
        base_config,
        [strategy.value for strategy in strategy_list],
    )


def run_gtad_ablation(base_config: SimulationConfig, seeds: Iterable[int]) -> dict[str, object]:
    seed_list = tuple(dict.fromkeys(seeds))
    if not seed_list:
        raise ValueError("En az bir seed gereklidir")

    runs = []
    for variant, weights in GTAD_ABLATIONS.items():
        for seed in seed_list:
            config = replace(base_config, seed=seed, defense_strategy=DefenseStrategy.GTAD_RISK)
            defense = GtadRiskAlgorithm(
                config.defense_budget,
                config.defense_range_multiplier,
                config.defense_max_degree,
                weights,
            )
            runs.append(_summarize_run(variant, seed, SimulationEngine(config, defense).run()))

    variant_manifest = {name: weights.to_dict() for name, weights in GTAD_ABLATIONS.items()}
    result = {
        "kind": "gtad_ablation",
        "variants": variant_manifest,
        "seeds": list(seed_list),
        "run_count": len(runs),
        "runs": runs,
        "summaries": _aggregate(runs),
        "paired_comparisons": _paired_comparisons(runs, "full"),
    }
    return _finalize_result(
        result,
        base_config,
        list(GTAD_ABLATIONS),
        variants=variant_manifest,
    )
