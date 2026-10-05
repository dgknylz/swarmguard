import networkx as nx

from swarmguard.algorithms.defense import DefenseAction, DefenseContext, DefenseDecision
from swarmguard.algorithms.defense.centrality_quarantine import CentralityQuarantineAlgorithm
from swarmguard.algorithms.defense.gtad_candidates import (
    generate_link_candidates,
    score_link_candidates,
)
from swarmguard.algorithms.defense.gtad_risk import GtadRiskAlgorithm
from swarmguard.algorithms.defense.none import NoDefenseAlgorithm
from swarmguard.algorithms.defense.observation import build_observation
from swarmguard.algorithms.defense.random_rewiring import RandomRewiringAlgorithm


def test_no_defense_runs_full_lifecycle_without_mutating_graph() -> None:
    graph = nx.path_graph(4)
    original_edges = set(graph.edges)
    algorithm = NoDefenseAlgorithm()

    report = algorithm.execute(
        DefenseContext(
            graph=graph,
            infected=frozenset({1}),
            step=3,
            communication_range=100.0,
        )
    )

    assert set(graph.edges) == original_edges
    assert report.algorithm == "none"
    assert report.step == 3
    assert report.applied_actions == ()
    assert report.intervention_cost == 0


def test_common_apply_contract_validates_and_applies_actions() -> None:
    graph = nx.path_graph(3)
    algorithm = NoDefenseAlgorithm()
    context = DefenseContext(graph, frozenset(), 1, 100.0)
    decision = DefenseDecision(
        algorithm="test",
        step=1,
        actions=(
            DefenseAction("remove_edge", 0, 1, "riskli bağlantı"),
            DefenseAction("add_edge", 0, 99, "geçersiz hedef"),
        ),
    )

    applied, rejected = algorithm.apply(context, decision)

    assert len(applied) == 1
    assert len(rejected) == 1
    assert not graph.has_edge(0, 1)


def test_random_rewiring_is_seeded_budgeted_and_avoids_infected_contact() -> None:
    def execute() -> tuple[set[tuple[int, int]], object]:
        graph = nx.Graph([(0, 1), (0, 3)])
        graph.add_nodes_from(range(4))
        report = RandomRewiringAlgorithm(seed=12, budget=2, range_multiplier=2).execute(
            DefenseContext(
                graph=graph,
                infected=frozenset({0}),
                step=1,
                communication_range=10,
                positions=((0, 0), (4, 0), (7, 0), (8, 0)),
            )
        )
        return set(graph.edges), report

    first_edges, first_report = execute()
    second_edges, second_report = execute()

    assert first_edges == second_edges
    assert first_report == second_report
    assert len(first_report.applied_actions) == 2
    assert first_report.intervention_cost == 2
    assert all(action.source != action.target for action in first_report.applied_actions)


def test_centrality_quarantine_selects_infected_hub() -> None:
    graph = nx.star_graph(4)
    report = CentralityQuarantineAlgorithm(budget=1).execute(
        DefenseContext(graph, frozenset({0, 4}), 2, 10)
    )

    assert report.applied_actions[0].source == 0
    assert graph.degree(0) == 0
    assert report.metadata == {"quarantined_nodes": [0]}


def test_gtad_risk_scores_are_bounded_and_reported_without_intervention() -> None:
    graph = nx.path_graph(4)
    report = GtadRiskAlgorithm().execute(DefenseContext(graph, frozenset({1}), 3, 10))
    scores = report.metadata["risk_scores"]

    assert report.applied_actions == ()
    assert report.intervention_cost == 0
    assert all(0 <= score <= 1 for score in scores.values())
    assert scores["1"] == max(scores.values())


def test_gtad_generates_only_missing_healthy_links() -> None:
    graph = nx.Graph([(0, 1), (1, 2)])
    graph.add_nodes_from(range(4))
    observation = build_observation(
        DefenseContext(
            graph,
            frozenset({1}),
            1,
            10,
            ((0, 0), (2, 0), (5, 0), (9, 0)),
        ),
        include_risk=True,
    )

    candidates = generate_link_candidates(observation)

    assert [(item.source, item.target) for item in candidates] == [(0, 2), (0, 3), (2, 3)]


def test_gtad_multi_objective_score_is_deterministic_and_bounded() -> None:
    graph = nx.Graph([(0, 1), (2, 3)])
    observation = build_observation(
        DefenseContext(
            graph,
            frozenset({1}),
            1,
            10,
            ((0, 0), (2, 0), (6, 0), (8, 0)),
        ),
        include_risk=True,
    )
    candidates = generate_link_candidates(observation)

    scored = score_link_candidates(observation, candidates, maximum_range=15)

    assert scored == score_link_candidates(observation, candidates, maximum_range=15)
    assert all(0 <= candidate.total_score <= 1 for candidate in scored)
    assert scored == tuple(
        sorted(scored, key=lambda item: (-item.total_score, item.source, item.target))
    )


def test_gtad_enforces_range_degree_and_budget_constraints() -> None:
    graph = nx.Graph([(0, 1), (2, 3)])
    graph.add_nodes_from(range(5))
    report = GtadRiskAlgorithm(budget=1, range_multiplier=1.0, maximum_degree=2).execute(
        DefenseContext(
            graph,
            frozenset({1}),
            4,
            5,
            ((0, 0), (1, 0), (4, 0), (5, 0), (20, 0)),
        )
    )

    assert len(report.applied_actions) == 1
    action = report.applied_actions[0]
    assert action.target is not None
    assert report.metadata["selected_candidate_count"] == 1
    assert report.metadata["range_rejected_count"] > 0
    assert report.metadata["degree_rejected_count"] > 0
    assert graph.degree(action.source) <= 2
    assert graph.degree(action.target) <= 2


def test_gtad_budget_caps_otherwise_feasible_links() -> None:
    graph = nx.empty_graph(4)
    report = GtadRiskAlgorithm(budget=1, range_multiplier=1.0, maximum_degree=3).execute(
        DefenseContext(
            graph,
            frozenset(),
            5,
            10,
            ((0, 0), (1, 0), (2, 0), (3, 0)),
        )
    )

    assert len(report.applied_actions) == 1
    assert report.metadata["budget_rejected_count"] == 5
