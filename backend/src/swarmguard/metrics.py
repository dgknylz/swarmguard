from __future__ import annotations

import networkx as nx


def calculate_metrics(graph: nx.Graph, infected: set[int]) -> dict[str, float | int]:
    node_count = graph.number_of_nodes()
    if node_count == 0:
        raise ValueError("Metrikler boş graf için hesaplanamaz")

    largest_component = max(
        (len(component) for component in nx.connected_components(graph)), default=0
    )
    connected = nx.is_connected(graph)
    lambda_2 = float(nx.algebraic_connectivity(graph)) if connected and node_count > 1 else 0.0

    return {
        "node_count": node_count,
        "edge_count": graph.number_of_edges(),
        "infected_count": len(infected),
        "infected_ratio": len(infected) / node_count,
        "largest_component_ratio": largest_component / node_count,
        "global_efficiency": float(nx.global_efficiency(graph)),
        "algebraic_connectivity": lambda_2,
    }
