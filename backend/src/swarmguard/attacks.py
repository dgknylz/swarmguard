from __future__ import annotations

import networkx as nx
import numpy as np

from .config import AttackStrategy


def choose_initial_infected(
    graph: nx.Graph,
    strategy: AttackStrategy,
    count: int,
    rng: np.random.Generator,
) -> set[int]:
    nodes = list(graph.nodes)
    if count > len(nodes):
        raise ValueError("Enfekte düğüm sayısı ağ boyutunu aşamaz")

    if strategy is AttackStrategy.RANDOM:
        selected = rng.choice(nodes, size=count, replace=False)
        return {int(node) for node in selected}

    if strategy is AttackStrategy.HIGHEST_DEGREE:
        scores = dict(graph.degree())
    elif strategy is AttackStrategy.HIGHEST_BETWEENNESS:
        scores = nx.betweenness_centrality(graph)
    else:
        raise ValueError(f"Bilinmeyen saldırı stratejisi: {strategy}")

    ranked = sorted(nodes, key=lambda node: (-scores[node], node))
    return set(ranked[:count])
