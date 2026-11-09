import itertools
from dataclasses import replace

import networkx as nx
import pytest

from swarmguard.algorithms.defense import (
    DefenseContext,
    RandomAdditionAlgorithm,
    SpectralShieldAlgorithm,
    build_defense,
)
from swarmguard.config import DefenseStrategy, SimulationConfig
from swarmguard.engine import SimulationEngine
from swarmguard.experiments import holm_adjust, paired_tests, run_monte_carlo
from swarmguard.presets import DEMO_CONFIG


def context(graph: nx.Graph, infected: set[int], positions, **kwargs) -> DefenseContext:
    return DefenseContext(
        graph=graph,
        infected=frozenset(infected),
        step=1,
        communication_range=10.0,
        positions=positions,
        **kwargs,
    )


def test_spectral_shield_isolates_the_largest_perron_weight_first() -> None:
    graph = nx.star_graph(6)
    graph.add_edge(6, 7)
    positions = tuple((float(node), 0.0) for node in range(8))
    report = SpectralShieldAlgorithm(budget=1).execute(context(graph, {0, 7}, positions))

    assert [action.source for action in report.applied_actions] == [0]
    assert report.applied_actions[0].action_type == "quarantine_node"
    assert graph.degree(0) == 0
    assert report.metadata["quarantine_targets"] == [0]


def test_spectral_shield_spends_spare_budget_on_joining_components() -> None:
    graph = nx.Graph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (3, 4), (4, 5)])
    positions = ((0.0, 0.0), (3.0, 0.0), (6.0, 0.0), (9.0, 0.0), (12.0, 0.0), (15.0, 0.0))
    report = SpectralShieldAlgorithm(budget=2, range_multiplier=1.0).execute(
        context(graph, {5}, positions)
    )

    kinds = [action.action_type for action in report.applied_actions]
    assert kinds == ["quarantine_node", "add_edge"]
    link = report.applied_actions[1]
    assert {link.source, link.target} == {2, 3}
    assert nx.number_connected_components(graph.subgraph(range(5))) == 1


def test_link_defenses_never_touch_infected_or_quarantined_uavs() -> None:
    graph = nx.path_graph(6)
    positions = tuple((float(node), 0.0) for node in range(6))
    for algorithm in (SpectralShieldAlgorithm(budget=4), RandomAdditionAlgorithm(3, 4)):
        trial = graph.copy()
        report = algorithm.execute(context(trial, {2}, positions, quarantined=frozenset({4})))
        for action in report.applied_actions:
            if action.action_type == "add_edge":
                assert {action.source, action.target}.isdisjoint({2, 4})


def test_random_addition_respects_budget_range_and_degree() -> None:
    graph = nx.empty_graph(8)
    positions = tuple((float(node), 0.0) for node in range(8))
    report = RandomAdditionAlgorithm(
        seed=1, budget=3, range_multiplier=0.25, maximum_degree=1
    ).execute(context(graph, set(), positions))

    assert len(report.applied_actions) == 3
    assert all(abs(action.source - action.target) <= 2 for action in report.applied_actions)
    assert max(dict(graph.degree).values()) == 1


def test_registry_builds_every_strategy() -> None:
    for strategy in DefenseStrategy:
        assert build_defense(strategy, seed=1).name == strategy.value


def test_imperfect_detection_only_reveals_a_subset_and_keeps_sis_stream() -> None:
    base = SimulationConfig(node_count=20, steps=30, seed=12, beta=0.3, gamma=0.05)
    oracle = SimulationEngine(base).run()
    blurred = SimulationEngine(replace(base, detection_probability=0.3)).run()
    defended = SimulationEngine(
        replace(base, detection_probability=0.3, defense_strategy=DefenseStrategy.SPECTRAL_SHIELD)
    ).run()

    assert [frame.infected for frame in oracle] == [frame.infected for frame in blurred]
    for previous, frame in itertools.pairwise(oracle):
        assert set(frame.detected) == set(previous.infected)
    hidden = 0
    for previous, frame in itertools.pairwise(defended):
        assert set(frame.detected) <= set(previous.infected)
        hidden += len(set(previous.infected) - set(frame.detected))
    assert hidden > 0


def test_defense_memory_keeps_quarantine_in_force() -> None:
    config = SimulationConfig(
        node_count=20,
        steps=6,
        seed=5,
        defense_strategy=DefenseStrategy.CENTRALITY_QUARANTINE,
        defense_budget=1,
        defense_memory=3,
    )
    frames = SimulationEngine(config).run()
    first = frames[1].defense_report["applied_actions"][0]["source"]

    for frame in frames[1:4]:
        assert first in frame.quarantined
        assert all(first not in edge for edge in frame.edges)
    assert frames[1].removed_edges


def test_frames_record_defense_link_changes() -> None:
    config = replace(DEMO_CONFIG, steps=5)
    frames = SimulationEngine(config).run()

    for frame in frames[1:]:
        added = {
            tuple(action[key] for key in ("source", "target"))
            for action in frame.defense_report["applied_actions"]
        }
        assert {tuple(sorted(edge)) for edge in added} == set(frame.added_edges)
        assert set(frame.added_edges) <= set(frame.edges)


def test_original_report_numbers_are_reproduced() -> None:
    """Tables 6–7 of the TÜBİTAK report: DEMO_CONFIG, seeds 1–30, default memory and detection."""
    strategies = [
        DefenseStrategy.NONE,
        DefenseStrategy.RANDOM_REWIRING,
        DefenseStrategy.CENTRALITY_QUARANTINE,
        DefenseStrategy.GTAD_RISK,
    ]
    result = run_monte_carlo(DEMO_CONFIG, strategies, range(1, 31))
    means = {
        summary["method"]: {name: values["mean"] for name, values in summary["metrics"].items()}
        for summary in result["summaries"]
    }
    expected = {
        "none": (0.7875, 0.9431, 0.7203, 0.900, 0.429, 0.088, 0.0),
        "random_rewiring": (0.7806, 0.9417, 0.7070, 0.913, 0.436, 0.108, 98.6),
        "centrality_quarantine": (0.0, 0.0736, 0.0164, 0.860, 0.403, 0.067, 25.6),
        "gtad_risk": (0.7875, 0.9431, 0.7203, 0.933, 0.450, 0.153, 76.1),
    }
    names = (
        "final_infected_ratio",
        "peak_infected_ratio",
        "mean_infected_ratio",
        "mean_largest_component_ratio",
        "mean_global_efficiency",
        "mean_algebraic_connectivity",
        "total_intervention_cost",
    )
    for method, values in expected.items():
        for name, value in zip(names, values, strict=True):
            assert means[method][name] == pytest.approx(
                value, abs=0.051 if name.startswith("total") else 6e-4
            )


def test_paired_tests_and_holm_adjustment() -> None:
    better = paired_tests([-0.2, -0.1, -0.3, -0.25, 0.0], lower_is_better=True)
    identical = paired_tests([0.0, 0.0, 0.0], lower_is_better=True)

    assert better["wins"] == 4 and better["losses"] == 0 and better["ties"] == 1
    assert better["p_value"] < 0.05
    assert better["sign_p_value"] == pytest.approx(0.125)
    assert identical["p_value"] == 1.0 and identical["effect_size"] is None
    assert holm_adjust([0.01, 0.04, None, 0.03]) == [0.03, 0.06, None, 0.06]


def test_monte_carlo_reports_significance_and_variance_reduction() -> None:
    config = replace(DEMO_CONFIG, steps=20)
    result = run_monte_carlo(
        config,
        [DefenseStrategy.NONE, DefenseStrategy.SPECTRAL_SHIELD, DefenseStrategy.GTAD_RISK],
        range(1, 9),
    )
    by_method = {item["method"]: item["delta_statistics"] for item in result["paired_comparisons"]}

    shield = by_method["spectral_shield"]["mean_infected_ratio"]
    gtad = by_method["gtad_risk"]["mean_infected_ratio"]
    assert shield["wins"] == 8 and shield["p_value_holm"] < 0.01
    assert gtad["ties"] == 8 and gtad["p_value"] == 1.0
    assert by_method["gtad_risk"]["mean_largest_component_ratio"]["variance_reduction"] > 0.5
