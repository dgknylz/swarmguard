from __future__ import annotations

import networkx as nx

from .base import DefenseContext, DefenseObservation


def build_observation(context: DefenseContext, *, include_risk: bool = False) -> DefenseObservation:
    graph = context.graph
    nodes = tuple(sorted(graph.nodes))
    infected = tuple(sorted(context.infected))
    healthy = tuple(node for node in nodes if node not in context.infected)
    degrees = dict(graph.degree)
    betweenness = (
        nx.betweenness_centrality(graph, normalized=True)
        if graph.number_of_edges()
        else dict.fromkeys(nodes, 0.0)
    )

    risk_scores: tuple[tuple[int, float], ...] = ()
    if include_risk:
        max_degree = max(degrees.values(), default=1) or 1
        max_betweenness = max(betweenness.values(), default=1.0) or 1.0
        scores: list[tuple[int, float]] = []
        for node in nodes:
            neighbors = tuple(graph.neighbors(node))
            exposure = (
                sum(neighbor in context.infected for neighbor in neighbors) / len(neighbors)
                if neighbors
                else 0.0
            )
            score = (
                0.45 * float(node in context.infected)
                + 0.30 * exposure
                + 0.15 * degrees[node] / max_degree
                + 0.10 * betweenness[node] / max_betweenness
            )
            scores.append((node, round(min(1.0, max(0.0, score)), 6)))
        risk_scores = tuple(scores)

    return DefenseObservation(
        step=context.step,
        infected=infected,
        node_count=graph.number_of_nodes(),
        edge_count=graph.number_of_edges(),
        nodes=nodes,
        healthy=healthy,
        edges=tuple(sorted((min(a, b), max(a, b)) for a, b in graph.edges)),
        positions=context.positions,
        communication_range=context.communication_range,
        degrees=tuple(sorted(degrees.items())),
        betweenness=tuple(sorted(betweenness.items())),
        risk_scores=risk_scores,
    )
