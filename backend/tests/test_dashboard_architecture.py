from dataclasses import replace
from types import SimpleNamespace

import pytest

from swarmguard.config import DefenseStrategy
from swarmguard.dashboard.components.scenario_builder import summarize_scenario
from swarmguard.dashboard.components.shell import PAGE_DESCRIPTIONS, get_shell_context
from swarmguard.dashboard.navigation import PAGE_SPECS, build_navigation
from swarmguard.dashboard.pages.overview import get_home_snapshot
from swarmguard.dashboard.state import get_or_create
from swarmguard.presets import DEMO_CONFIG, SCENARIO_PRESETS, get_scenario_preset


def test_page_registry_has_unique_routes_and_one_default() -> None:
    assert len(PAGE_SPECS) == 6
    assert len({spec.path for spec in PAGE_SPECS}) == len(PAGE_SPECS)
    assert sum(spec.default for spec in PAGE_SPECS) == 1
    assert {spec.section for spec in PAGE_SPECS} == {"Platform", "Araştırma"}


def test_navigation_uses_flat_top_menu() -> None:
    class FakeStreamlit:
        def __init__(self) -> None:
            self.position = ""
            self.pages: list[object] = []

        def Page(self, renderer, **kwargs):
            return {"renderer": renderer, **kwargs}

        def navigation(self, pages, *, position):
            self.pages = pages
            self.position = position
            return SimpleNamespace(run=lambda: None)

    st = FakeStreamlit()
    build_navigation(st)

    assert st.position == "top"
    assert isinstance(st.pages, list)
    assert len(st.pages) == len(PAGE_SPECS)


def test_session_state_factory_runs_only_once() -> None:
    state: dict[str, object] = {}
    calls = 0

    def factory() -> list[int]:
        nonlocal calls
        calls += 1
        return [2025]

    first = get_or_create(state, "seed", factory)
    second = get_or_create(state, "seed", factory)

    assert first is second
    assert first == [2025]
    assert calls == 1


def test_shell_context_has_safe_empty_state() -> None:
    context = get_shell_context({})

    assert context.scenario_status == "Beklemede"
    assert context.node_count == "—"
    assert context.current_step == "—"
    assert set(PAGE_DESCRIPTIONS) == {spec.title for spec in PAGE_SPECS}


def test_shell_context_summarizes_active_scenario() -> None:
    frame = SimpleNamespace(step=60, metrics={"infected_count": 3})
    context = get_shell_context({"config": DEMO_CONFIG, "frames": [frame]})

    assert context.scenario_status == "Aktif"
    assert context.node_count == "24"
    assert context.defense == "gtad_risk"
    assert context.seed == "2025"
    assert context.current_step == "60"
    assert context.infected_count == "3"


def test_command_center_snapshot_handles_idle_and_completed_runs() -> None:
    idle = get_home_snapshot({})
    frame = SimpleNamespace(
        step=60,
        metrics={"infected_count": 3, "largest_component_ratio": 0.875},
    )
    completed = get_home_snapshot({"config": DEMO_CONFIG, "frames": [frame]})

    assert idle.status == "PLATFORM HAZIR"
    assert idle.step == "—"
    assert completed.status == "SON KOŞU HAZIR"
    assert completed.step == "60"
    assert completed.infected == "3"
    assert completed.connectivity == "%87.5"
    assert completed.defense == "GTAD_RISK"


def test_scenario_summary_estimates_load_and_flags_risky_inputs() -> None:
    demo = summarize_scenario(DEMO_CONFIG)
    risky = summarize_scenario(
        replace(
            DEMO_CONFIG,
            communication_range=10,
            initial_infected_count=8,
            defense_strategy=DefenseStrategy.NONE,
            defense_max_degree=24,
        )
    )

    assert demo.area == "1000 × 700 m"
    assert demo.expected_degree > 2
    assert demo.attack_pressure == "Orta"
    assert len(risky.warnings) == 4


def test_scenario_library_has_seven_valid_unique_profiles() -> None:
    assert len(SCENARIO_PRESETS) == 7
    assert len({preset.slug for preset in SCENARIO_PRESETS}) == len(SCENARIO_PRESETS)
    assert all(
        preset.title and preset.description and preset.category for preset in SCENARIO_PRESETS
    )
    assert get_scenario_preset("gtad-demo").config == DEMO_CONFIG

    with pytest.raises(ValueError, match="Bilinmeyen senaryo profili"):
        get_scenario_preset("missing")


def test_baseline_preset_is_paired_with_gtad_demo() -> None:
    baseline = get_scenario_preset("unprotected-baseline").config
    normalized = replace(
        baseline,
        defense_strategy=DefenseStrategy.GTAD_RISK,
        defense_budget=DEMO_CONFIG.defense_budget,
    )

    assert normalized == DEMO_CONFIG
