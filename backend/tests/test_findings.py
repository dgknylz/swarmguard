import pytest

from swarmguard.config import DefenseStrategy
from swarmguard.dashboard.components import findings_charts
from swarmguard.dashboard.components.theory_lab import compute_threshold_sweep
from swarmguard.dashboard.pages.overview import build_findings
from swarmguard.findings import (
    ENDEMIC_LEVEL,
    SWEEP_MULTIPLIERS,
    THRESHOLD_SLUGS,
    load_findings,
    sweep_key,
    threshold_sweep,
)
from swarmguard.presets import PRESET_BY_SLUG, SHOWCASE_CONFIG


def test_shipped_findings_cover_every_scenario_and_method() -> None:
    findings = load_findings()

    assert [item["slug"] for item in findings["thresholds"]] == list(THRESHOLD_SLUGS)
    assert findings["sweep_multipliers"] == list(SWEEP_MULTIPLIERS)
    assert len(findings["ordering"]) == 4
    for table in findings["tables"]:
        assert {row["method"] for row in table["rows"]} == {item.value for item in DefenseStrategy}


def test_shipped_thresholds_respect_the_guarantee_of_theorem_2() -> None:
    for item in load_findings()["thresholds"]:
        config = PRESET_BY_SLUG[item["slug"]].config
        assert item["key"] == list(sweep_key(config))
        assert len(item["levels"]) == len(SWEEP_MULTIPLIERS)
        assert item["level_below_threshold"] < ENDEMIC_LEVEL
        assert item["tightness"] is None or item["tightness"] > 1


def test_shipped_threshold_matches_a_fresh_computation() -> None:
    shipped = load_findings()["thresholds"][0]
    fresh = threshold_sweep(SHOWCASE_CONFIG, replicates=8)

    assert fresh["threshold_beta"] == shipped["threshold_beta"]
    assert fresh["mean_spectral_radius"] == shipped["mean_spectral_radius"]
    assert compute_threshold_sweep(SHOWCASE_CONFIG) == shipped


def test_shipped_tables_agree_with_the_reproduced_report_numbers() -> None:
    tables = {
        table["key"]: {row["method"]: row for row in table["rows"]}
        for table in load_findings()["tables"]
    }
    perfect = tables["perfect"]

    assert perfect["none"]["infection"]["mean"] == pytest.approx(0.7203, abs=6e-4)
    assert perfect["gtad_risk"]["connectivity"]["mean"] == pytest.approx(0.933, abs=6e-4)
    assert perfect["centrality_quarantine"]["infection"]["mean"] == pytest.approx(0.0164, abs=6e-4)
    # The ordering experiment and the table share the constrained setting and seeds.
    control = load_findings()["ordering"][-1]
    assert control["shield"]["mean"] == pytest.approx(
        tables["constrained"]["spectral_shield"]["infection"]["mean"]
    )
    assert control["control"]["mean"] == pytest.approx(
        tables["constrained"]["random_quarantine"]["infection"]["mean"]
    )


def test_findings_render_as_sentences_and_figures() -> None:
    findings = load_findings()
    sentences = build_findings(findings)

    assert [item.figure for item in sentences] == ["collapse", "ordering", "tradeoff"]
    assert all(item.headline and item.body for item in sentences)
    sweep = findings["thresholds"][0]
    figures = (
        findings_charts.threshold_collapse_figure(findings),
        findings_charts.ordering_figure(findings),
        findings_charts.tradeoff_figure(findings),
        findings_charts.tightness_figure(findings),
        findings_charts.scenario_threshold_figure(sweep, SWEEP_MULTIPLIERS, 0.16, ENDEMIC_LEVEL),
        findings_charts.scenario_threshold_figure(sweep, SWEEP_MULTIPLIERS, 0.02, ENDEMIC_LEVEL),
    )
    assert all(len(figure.data) >= 1 for figure in figures)
    assert len(figures[2].data) == 2 * len(DefenseStrategy)
