from __future__ import annotations

import networkx as nx
import numpy as np


def infection_probability(beta: float, infected_neighbor_count: int) -> float:
    return 1.0 - (1.0 - beta) ** infected_neighbor_count


def advance_sis(
    graph: nx.Graph,
    infected: set[int],
    beta: float,
    gamma: float,
    rng: np.random.Generator,
) -> tuple[set[int], set[int], set[int]]:
    """Advance one synchronous SIS step.

    Returns the new infected set, newly infected nodes and recovered nodes.
    All decisions use the infection state at the beginning of the step.
    """
    newly_infected: set[int] = set()
    recovered: set[int] = set()

    for node in graph.nodes:
        if node in infected:
            if rng.random() < gamma:
                recovered.add(node)
            continue

        infected_neighbors = sum(neighbor in infected for neighbor in graph.neighbors(node))
        probability = infection_probability(beta, infected_neighbors)
        if rng.random() < probability:
            newly_infected.add(node)

    next_infected = (infected - recovered) | newly_infected
    return next_infected, newly_infected, recovered
