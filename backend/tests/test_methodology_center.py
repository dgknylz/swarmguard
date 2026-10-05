import pytest

from swarmguard.config import AttackStrategy, DefenseStrategy
from swarmguard.dashboard.components.methodology_center import (
    GTAD_LINK_WEIGHTS,
    GTAD_RISK_WEIGHTS,
    methodology_manifest,
)
from swarmguard.experiments import GTAD_ABLATIONS, RESULT_METRICS


def test_methodology_catalog_matches_runtime_strategies_and_metrics() -> None:
    manifest = methodology_manifest()

    assert {method["key"] for method in manifest["attack_methods"]} == {
        strategy.value for strategy in AttackStrategy
    }
    assert {method["key"] for method in manifest["defense_methods"]} == {
        strategy.value for strategy in DefenseStrategy
    }
    assert {metric["key"] for metric in manifest["metrics"]} == set(RESULT_METRICS)


def test_documented_gtad_weights_are_normalized() -> None:
    assert sum(GTAD_RISK_WEIGHTS.values()) == pytest.approx(1.0)
    assert sum(GTAD_LINK_WEIGHTS.values()) == pytest.approx(1.0)
    assert GTAD_RISK_WEIGHTS == {
        "infection": 0.45,
        "exposure": 0.30,
        "degree": 0.15,
        "betweenness": 0.10,
    }
    assert GTAD_LINK_WEIGHTS == {
        "connectivity": 0.50,
        "safety": 0.30,
        "distance": 0.20,
    }


def test_methodology_exposes_every_ablation_variant_with_normalized_weights() -> None:
    variants = methodology_manifest()["ablation_variants"]

    assert set(variants) == set(GTAD_ABLATIONS)
    assert all(sum(weights.values()) == pytest.approx(1.0) for weights in variants.values())
