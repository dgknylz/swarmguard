from dataclasses import replace
from math import pi

import networkx as nx
import numpy as np
import pytest

from swarmguard.config import SimulationConfig
from swarmguard.engine import SimulationEngine
from swarmguard.network import move_with_reflection
from swarmguard.spectral import adjacency_from_edges, fiedler_pair, perron_pair, spectral_radius
from swarmguard.theory import (
    adjacency_sequence,
    expected_degree,
    extinction_threshold,
    initial_vector,
    linear_bound,
    link_statistics,
    mean_field,
    naive_expected_degree,
    perturbation_check,
    phase_diagram,
    rectangle_distance_cdf,
    simulate_replicates,
    spectral_bound,
    spectral_profile,
)


@pytest.mark.parametrize("distance", [50.0, 400.0, 650.0, 900.0, 1150.0, 1300.0])
def test_rectangle_distance_cdf_matches_monte_carlo(distance: float) -> None:
    rng = np.random.default_rng(1)
    first = rng.uniform((0, 0), (1000, 700), size=(400_000, 2))
    second = rng.uniform((0, 0), (1000, 700), size=(400_000, 2))
    empirical = np.mean(np.linalg.norm(first - second, axis=1) <= distance)

    assert rectangle_distance_cdf(distance, 1000, 700) == pytest.approx(empirical, abs=0.003)


def test_rectangle_distance_cdf_closed_form_and_limits() -> None:
    width, height, radius = 1000.0, 700.0, 250.0
    closed_form = (
        pi * width * height * radius**2 - 4 / 3 * (width + height) * radius**3 + radius**4 / 2
    ) / (width**2 * height**2)

    assert rectangle_distance_cdf(radius, width, height) == pytest.approx(closed_form, rel=1e-12)
    assert rectangle_distance_cdf(radius, height, width) == pytest.approx(closed_form, rel=1e-12)
    assert rectangle_distance_cdf(0, width, height) == 0
    assert rectangle_distance_cdf(1300, width, height) == 1
    assert expected_degree(24, width, height, radius) < naive_expected_degree(
        24, width, height, radius
    )


def test_reflective_motion_keeps_uniform_positions_and_handles_fast_uavs() -> None:
    rng = np.random.default_rng(3)
    positions = rng.uniform((0, 0), (100, 50), size=(20_000, 2))
    angles = rng.uniform(0, 2 * np.pi, 20_000)
    velocities = 37.0 * np.column_stack((np.cos(angles), np.sin(angles)))
    for _ in range(25):
        positions, velocities = move_with_reflection(positions, velocities, 100, 50)

    assert positions.min() >= 0
    assert positions[:, 0].max() <= 100 and positions[:, 1].max() <= 50
    histogram, _ = np.histogram(positions[:, 0], bins=10, range=(0, 100))
    assert histogram.min() > 0.9 * histogram.mean()

    fast, _ = move_with_reflection(np.array([[5.0, 5.0]]), np.array([[-430.0, 260.0]]), 100, 50)
    assert 0 <= fast[0, 0] <= 100 and 0 <= fast[0, 1] <= 50


def test_simulated_degrees_agree_with_teorem_1() -> None:
    config = SimulationConfig(node_count=40, steps=120, seed=9, speed=12)
    frames = SimulationEngine(config).run()
    distances, mean_degrees = link_statistics(frames, config.communication_range)
    theory = expected_degree(40, config.area_width, config.area_height, config.communication_range)

    assert len(distances) == len(frames) * 40 * 39 // 2
    assert mean_degrees.mean() == pytest.approx(theory, rel=0.15)


def test_vectorised_replicate_reproduces_the_engine_exactly() -> None:
    config = SimulationConfig(node_count=18, steps=25, seed=4, beta=0.3, gamma=0.1)
    engine = SimulationEngine(config)
    generator = np.random.default_rng()
    generator.bit_generator.state = engine.rng.bit_generator.state
    frames = engine.run()

    replicate = simulate_replicates(
        adjacency_sequence(frames), initial_vector(frames), config.beta, config.gamma, 1, generator
    )

    assert replicate.infected[0].tolist() == [len(frame.infected) for frame in frames]


def test_bounds_dominate_the_monte_carlo_mean_and_new_infections() -> None:
    config = SimulationConfig(node_count=24, steps=40, seed=2025, beta=0.08, gamma=0.2)
    frames = SimulationEngine(config).run()
    adjacencies = adjacency_sequence(frames)
    initial = initial_vector(frames)
    run = simulate_replicates(adjacencies, initial, config.beta, config.gamma, 4000, 7)
    mean_infected = run.infected.mean(axis=0)
    profile = spectral_profile(adjacencies, config.beta, config.gamma)

    linear = linear_bound(adjacencies, initial, config.beta, config.gamma)
    spectral = spectral_bound(24, int(initial.sum()), profile.spread_factor)
    tolerance = 4 * run.infected.std(axis=0) / np.sqrt(4000) + 1e-9
    assert np.all(mean_infected <= linear + tolerance)
    assert np.all(linear <= spectral + 1e-9)
    assert np.all(run.expected_new <= config.beta * run.boundary + 1e-9)
    lower = config.beta * run.boundary - config.beta**2 * run.pair_term
    assert np.all(run.expected_new >= lower - 1e-9)
    assert mean_field(adjacencies, initial, config.beta, config.gamma)[0] == initial.sum()


def test_extinction_threshold_separates_decay_from_growth() -> None:
    radii = np.array([2.0, 4.0, 3.0, 5.0])
    gamma = 0.2
    threshold = extinction_threshold(radii, gamma)
    below = spectral_profile([np.zeros((1, 1))], 0, gamma)

    geometric = np.exp(np.mean(np.log(1 - gamma + threshold * radii)))
    assert geometric == pytest.approx(1.0, abs=1e-9)
    assert below.geometric_mean == pytest.approx(1 - gamma)
    assert extinction_threshold(np.zeros(3), gamma) == float("inf")
    assert extinction_threshold(radii, 0.0) == 0.0


def test_static_graph_threshold_is_gamma_over_lambda() -> None:
    graph = nx.random_regular_graph(4, 30, seed=5)
    adjacency = adjacency_from_edges(30, graph.edges)

    assert spectral_radius(adjacency) == pytest.approx(4.0)
    assert extinction_threshold(np.full(10, 4.0), 0.2) == pytest.approx(0.05)


def test_phase_diagram_has_one_cell_per_parameter_pair() -> None:
    frames = SimulationEngine(replace(SimulationConfig(), node_count=16, steps=30, seed=8)).run()
    diagram = phase_diagram(
        adjacency_sequence(frames), initial_vector(frames), [0.05, 0.4], [0.1, 0.3], replicates=8
    )

    assert diagram.endemic_level.shape == (2, 2)
    assert diagram.endemic_level[0, 1] >= diagram.endemic_level[0, 0]
    assert np.all(np.diff(diagram.threshold_betas) > 0)


@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_lemma_4_rayleigh_bounds_hold_for_every_perturbation(seed: int) -> None:
    graph = nx.random_geometric_graph(26, 0.32, seed=seed)
    check = perturbation_check(adjacency_from_edges(26, graph.edges))

    assert len(check.nodes) >= 2
    assert np.all(check.edge_removal.exact >= check.edge_removal.bound - 1e-9)
    assert np.all(check.node_isolation.exact >= check.node_isolation.bound - 1e-9)
    assert np.all(check.link_cost.exact >= check.link_cost.bound - 1e-9)
    assert np.all(check.link_gain.exact <= check.link_gain.bound + 1e-9)
    assert np.all(check.link_gain.exact >= -1e-9)


def test_spectral_helpers_return_unit_vectors() -> None:
    adjacency = adjacency_from_edges(5, [(0, 1), (1, 2), (3, 4)])
    radius, perron = perron_pair(adjacency)
    connectivity, fiedler = fiedler_pair(adjacency)

    assert radius == pytest.approx(np.sqrt(2))
    assert np.linalg.norm(perron) == pytest.approx(1.0)
    assert np.all(perron >= 0)
    assert connectivity == 0.0
    assert np.linalg.norm(fiedler) == pytest.approx(1.0)
    assert fiedler.sum() == pytest.approx(0.0, abs=1e-12)
