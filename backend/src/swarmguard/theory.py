"""Closed-form results of the SwarmGuard model and the computations that check them.

Teorem 1  Exact link probability of two uniform UAVs in a W×H mission area, hence the
          exact expected degree of the communication graph (boundary effects included).
Teorem 2  Spectral upper bound E[I(t)] ≤ √(n·I₀)·Π σ(s) with σ(s) = 1 − γ + β·λ₁(A(s)),
          and the extinction condition (Π σ)^(1/t) < 1.
Önerme 3  One step of SIS creates at most β·|∂I| new infections in expectation, where
          ∂I is the set of susceptible–infected edges.
Lemma 4   Rayleigh-quotient bounds for removing an edge, isolating a node and adding a
          link, which drive the spectral defense.

Theorems 2–3 hold for any graph sequence chosen independently of the epidemic, so the
checks below always use the undefended mobility of a scenario.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import asin, pi, sqrt

import numpy as np
from numpy.typing import NDArray

from .engine import SimulationFrame
from .spectral import (
    adjacency_from_edges,
    connected_components,
    fiedler_pair,
    laplacian,
    perron_pair,
    spectral_radius,
)

FloatArray = NDArray[np.float64]


# Teorem 1 ---------------------------------------------------------------------------


def rectangle_distance_cdf(distance: float, width: float, height: float) -> float:
    """P(‖X − Y‖ ≤ d) for independent uniform points X, Y in [0, W] × [0, H].

    U = |X₁ − Y₁| has density 2(W − u)/W² and V = |X₂ − Y₂| has density 2(H − v)/H², so
    F(d) = 4/(W²H²) ∬_{u²+v²≤d²} (W − u)(H − v) du dv, which is integrated exactly here.
    For d ≤ min(W, H) this reduces to (πWHd² − ⁴⁄₃(W + H)d³ + ½d⁴) / (W²H²).
    """
    if width <= 0 or height <= 0:
        raise ValueError("Görev alanı boyutları pozitif olmalıdır")
    d = float(distance)
    if d <= 0:
        return 0.0
    if d * d >= width * width + height * height:
        return 1.0

    a, b = float(width), float(height)
    v_max = min(b, d)
    v_0 = min(sqrt(max(d * d - a * a, 0.0)), v_max)

    def root_integral(v: float) -> float:  # ∫ √(d² − v²) dv
        return 0.5 * (v * sqrt(max(d * d - v * v, 0.0)) + d * d * asin(min(v / d, 1.0)))

    def weighted_root_integral(v: float) -> float:  # ∫ v·√(d² − v²) dv
        return -(max(d * d - v * v, 0.0) ** 1.5) / 3

    def polynomial_integral(v: float) -> float:  # ∫ (b − v)(d² − v²) dv
        return b * d * d * v - b * v**3 / 3 - d * d * v * v / 2 + v**4 / 4

    integral = (
        0.5 * a * a * (b * v_0 - v_0 * v_0 / 2)
        + a
        * (
            b * (root_integral(v_max) - root_integral(v_0))
            - (weighted_root_integral(v_max) - weighted_root_integral(v_0))
        )
        - 0.5 * (polynomial_integral(v_max) - polynomial_integral(v_0))
    )
    return min(1.0, max(0.0, 4 * integral / (a * a * b * b)))


def expected_degree(
    node_count: int, width: float, height: float, communication_range: float
) -> float:
    """E[deg] = (n − 1)·F(r): exact under uniform positions (Teorem 1)."""
    return (node_count - 1) * rectangle_distance_cdf(communication_range, width, height)


def naive_expected_degree(
    node_count: int, width: float, height: float, communication_range: float
) -> float:
    """The boundary-free estimate (n − 1)·πr²/(WH) that Teorem 1 corrects."""
    return (node_count - 1) * min(1.0, pi * communication_range**2 / (width * height))


def link_statistics(
    frames: Sequence[SimulationFrame], communication_range: float, *, max_frames: int = 200
) -> tuple[FloatArray, FloatArray]:
    """Pairwise distances pooled over frames and the mean range-graph degree per frame.

    Degrees are counted from positions, so defense actions do not affect the check.
    """
    stride = max(1, -(-len(frames) // max_frames))
    distances: list[FloatArray] = []
    mean_degrees: list[float] = []
    for frame in frames[::stride]:
        points = np.asarray(frame.positions, dtype=float)
        rows, columns = np.triu_indices(len(points), k=1)
        pairwise = np.linalg.norm(points[rows] - points[columns], axis=1)
        distances.append(pairwise)
        mean_degrees.append(2 * np.count_nonzero(pairwise <= communication_range) / len(points))
    return np.concatenate(distances), np.asarray(mean_degrees)


# Teorem 2 ---------------------------------------------------------------------------


def adjacency_sequence(frames: Sequence[SimulationFrame]) -> list[FloatArray]:
    """A(1), …, A(T): the graphs used by the SIS transitions of a run."""
    node_count = len(frames[0].positions)
    return [adjacency_from_edges(node_count, frame.edges) for frame in frames[1:]]


def initial_vector(frames: Sequence[SimulationFrame]) -> FloatArray:
    vector = np.zeros(len(frames[0].positions))
    vector[list(frames[0].infected)] = 1.0
    return vector


def extinction_threshold(radii: FloatArray, gamma: float) -> float:
    """β* solving mean_t log(1 − γ + β·λ₁(t)) = 0.

    For β < β* the geometric mean of σ(t) is below one, so Teorem 2 forces the expected
    number of infected UAVs to decay exponentially. ``inf`` means no β ever breaks it.
    """
    radii = np.asarray(radii, dtype=float)
    if gamma <= 0:
        return 0.0
    if not np.any(radii > 0):
        return float("inf")

    def log_growth(beta: float) -> float:
        with np.errstate(divide="ignore"):
            return float(np.mean(np.log(np.maximum(1 - gamma + beta * radii, 0.0))))

    low, high = 0.0, 1.0
    while log_growth(high) < 0:
        high *= 2
        if high > 1e9:
            return float("inf")
    for _ in range(80):
        middle = (low + high) / 2
        if log_growth(middle) < 0:
            low = middle
        else:
            high = middle
    return high


@dataclass(frozen=True, slots=True)
class SpectralProfile:
    spectral_radius: FloatArray
    spread_factor: FloatArray
    geometric_mean: float
    threshold_beta: float


def spectral_profile(
    adjacencies: Sequence[FloatArray], beta: float, gamma: float
) -> SpectralProfile:
    radii = np.array([spectral_radius(adjacency) for adjacency in adjacencies])
    factors = 1 - gamma + beta * radii
    with np.errstate(divide="ignore"):
        geometric_mean = float(np.exp(np.mean(np.log(np.maximum(factors, 0.0)))))
    return SpectralProfile(
        spectral_radius=radii,
        spread_factor=factors,
        geometric_mean=geometric_mean,
        threshold_beta=extinction_threshold(radii, gamma),
    )


def spectral_bound(
    node_count: int, initial_infected: int, spread_factors: FloatArray
) -> FloatArray:
    """√(n·I₀)·Π_{s≤t} σ(s) for t = 0, …, T, clipped to the trivial bound n."""
    with np.errstate(divide="ignore"):
        logs = np.log(np.maximum(np.asarray(spread_factors, dtype=float), 0.0))
    log_bound = 0.5 * np.log(node_count * initial_infected) + np.concatenate(
        ([0.0], np.cumsum(logs))
    )
    return np.minimum(np.exp(np.minimum(log_bound, np.log(node_count))), node_count)


def linear_bound(
    adjacencies: Sequence[FloatArray], initial: FloatArray, beta: float, gamma: float
) -> FloatArray:
    """Σᵢ bᵢ(t) with b(t) = min(1, M(t)·b(t − 1)), M(t) = (1 − γ)I + βA(t).

    Step (i) of the proof shows p(t) ≤ M(t)p(t − 1) and M(t) preserves order, so this
    vector bound dominates the true infection probabilities at every step.
    """
    bound = np.asarray(initial, dtype=float)
    totals = [float(bound.sum())]
    for adjacency in adjacencies:
        bound = np.minimum(1.0, (1 - gamma) * bound + beta * (adjacency @ bound))
        totals.append(float(bound.sum()))
    return np.asarray(totals)


def mean_field(
    adjacencies: Sequence[FloatArray], initial: FloatArray, beta: float, gamma: float
) -> FloatArray:
    """Expected infected count under the independence (NIMFA) approximation.

    pᵢ(t) = (1 − γ)pᵢ(t − 1) + (1 − pᵢ(t − 1))·(1 − Πⱼ(1 − β·Aᵢⱼ(t)·pⱼ(t − 1))).
    """
    probability = np.asarray(initial, dtype=float)
    totals = [float(probability.sum())]
    for adjacency in adjacencies:
        log_escape = adjacency @ np.log1p(-np.minimum(beta * probability, 1 - 1e-12))
        probability = (1 - gamma) * probability + (1 - probability) * (1 - np.exp(log_escape))
        totals.append(float(probability.sum()))
    return np.asarray(totals)


@dataclass(frozen=True, slots=True)
class ReplicateRun:
    infected: NDArray[np.int64]
    new_infections: NDArray[np.int64]
    expected_new: FloatArray
    boundary: FloatArray
    pair_term: FloatArray


def simulate_replicates(
    adjacencies: Sequence[FloatArray],
    initial: FloatArray,
    beta: float,
    gamma: float,
    replicates: int,
    rng: np.random.Generator | int,
) -> ReplicateRun:
    """Vectorised copy of the engine's synchronous SIS step for many replicates.

    Each UAV consumes exactly one uniform draw per step, as in the engine, so a single
    replicate fed with the engine's generator reproduces the engine run exactly.
    """
    generator = rng if isinstance(rng, np.random.Generator) else np.random.default_rng(rng)
    state = np.repeat(np.asarray(initial, dtype=bool)[None, :], replicates, axis=0)
    infected = [state.sum(axis=1)]
    new_infections, expected_new, boundary, pair_term = [], [], [], []

    for adjacency in adjacencies:
        neighbors = state.astype(float) @ adjacency
        susceptible = ~state
        infection_probability = 1 - (1 - beta) ** neighbors
        expected_new.append((infection_probability * susceptible).sum(axis=1))
        boundary.append((neighbors * susceptible).sum(axis=1))
        pair_term.append((neighbors * (neighbors - 1) / 2 * susceptible).sum(axis=1))

        draws = generator.random(state.shape)
        recovered = state & (draws < gamma)
        newly_infected = susceptible & (draws < infection_probability)
        state = (state & ~recovered) | newly_infected
        new_infections.append(newly_infected.sum(axis=1))
        infected.append(state.sum(axis=1))

    def stack(values: list[FloatArray]) -> FloatArray:
        return np.stack(values, axis=1) if values else np.zeros((replicates, 0))

    return ReplicateRun(
        infected=np.stack(infected, axis=1),
        new_infections=stack(new_infections).astype(np.int64),
        expected_new=stack(expected_new),
        boundary=stack(boundary),
        pair_term=stack(pair_term),
    )


@dataclass(frozen=True, slots=True)
class PhaseDiagram:
    betas: FloatArray
    gammas: FloatArray
    endemic_level: FloatArray
    threshold_betas: FloatArray


def phase_diagram(
    adjacencies: Sequence[FloatArray],
    initial: FloatArray,
    betas: Sequence[float],
    gammas: Sequence[float],
    *,
    replicates: int = 24,
    seed: int = 0,
) -> PhaseDiagram:
    """Mean infected fraction over the last third of the horizon on a (γ, β) grid.

    Every cell reuses the same random stream (common random numbers), which keeps the
    surface smooth, and β*(γ) from Teorem 2 is returned alongside for the overlay.
    """
    node_count = len(initial)
    tail = max(1, len(adjacencies) // 3)
    radii = np.array([spectral_radius(adjacency) for adjacency in adjacencies])
    levels = np.zeros((len(gammas), len(betas)))
    for row, gamma in enumerate(gammas):
        for column, beta in enumerate(betas):
            run = simulate_replicates(adjacencies, initial, beta, gamma, replicates, seed)
            levels[row, column] = run.infected[:, -tail:].mean() / node_count
    return PhaseDiagram(
        betas=np.asarray(betas, dtype=float),
        gammas=np.asarray(gammas, dtype=float),
        endemic_level=levels,
        threshold_betas=np.array([extinction_threshold(radii, gamma) for gamma in gammas]),
    )


# Lemma 4 ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BoundCheck:
    bound: FloatArray
    exact: FloatArray


@dataclass(frozen=True, slots=True)
class PerturbationCheck:
    nodes: tuple[int, ...]
    spectral_radius: float
    algebraic_connectivity: float
    edge_removal: BoundCheck
    node_isolation: BoundCheck
    link_cost: BoundCheck
    link_gain: BoundCheck


def perturbation_check(adjacency: FloatArray, *, max_pairs: int = 400) -> PerturbationCheck:
    """Compare every Lemma 4 bound with the exact eigenvalue change.

    Works on the largest connected component so that λ₂ > 0 and the Fiedler vector is
    well defined. Expected signs: removal/isolation/link cost exact ≥ bound, link gain
    exact ≤ bound.
    """
    nodes = connected_components(adjacency)[0]
    sub = adjacency[np.ix_(nodes, nodes)]
    size = len(nodes)
    radius, perron = perron_pair(sub)
    connectivity, fiedler = fiedler_pair(sub)
    rows, columns = np.triu_indices(size, k=1)
    is_edge = sub[rows, columns] > 0
    edges = list(zip(rows[is_edge], columns[is_edge], strict=True))
    non_edges = list(zip(rows[~is_edge], columns[~is_edge], strict=True))
    if len(non_edges) > max_pairs:
        non_edges = non_edges[:: -(-len(non_edges) // max_pairs)]

    removal_bound, removal_exact = [], []
    for i, j in edges:
        changed = sub.copy()
        changed[i, j] = changed[j, i] = 0.0
        removal_bound.append(-2 * perron[i] * perron[j])
        removal_exact.append(spectral_radius(changed) - radius)

    isolation_bound, isolation_exact = [], []
    for i in range(size):
        changed = sub.copy()
        changed[i, :] = 0.0
        changed[:, i] = 0.0
        isolation_bound.append(-2 * radius * perron[i] ** 2)
        isolation_exact.append(spectral_radius(changed) - radius)

    cost_bound, cost_exact, gain_bound, gain_exact = [], [], [], []
    for i, j in non_edges:
        changed = sub.copy()
        changed[i, j] = changed[j, i] = 1.0
        cost_bound.append(2 * perron[i] * perron[j])
        cost_exact.append(spectral_radius(changed) - radius)
        gain_bound.append((fiedler[i] - fiedler[j]) ** 2)
        gain_exact.append(float(np.linalg.eigvalsh(laplacian(changed))[1]) - connectivity)

    def check(bound: list[float], exact: list[float]) -> BoundCheck:
        return BoundCheck(np.asarray(bound, dtype=float), np.asarray(exact, dtype=float))

    return PerturbationCheck(
        nodes=tuple(int(node) for node in nodes),
        spectral_radius=radius,
        algebraic_connectivity=connectivity,
        edge_removal=check(removal_bound, removal_exact),
        node_isolation=check(isolation_bound, isolation_exact),
        link_cost=check(cost_bound, cost_exact),
        link_gain=check(gain_bound, gain_exact),
    )
