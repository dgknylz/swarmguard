from __future__ import annotations

import networkx as nx
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def initialize_motion(
    node_count: int,
    width: float,
    height: float,
    speed: float,
    rng: np.random.Generator,
) -> tuple[FloatArray, FloatArray]:
    positions = np.column_stack(
        (rng.uniform(0, width, node_count), rng.uniform(0, height, node_count))
    )
    angles = rng.uniform(0, 2 * np.pi, node_count)
    velocities = speed * np.column_stack((np.cos(angles), np.sin(angles)))
    return positions, velocities


def move_with_reflection(
    positions: FloatArray,
    velocities: FloatArray,
    width: float,
    height: float,
) -> tuple[FloatArray, FloatArray]:
    next_positions = positions + velocities
    next_velocities = velocities.copy()

    for axis, upper_bound in ((0, width), (1, height)):
        below = next_positions[:, axis] < 0
        next_positions[below, axis] *= -1
        next_velocities[below, axis] *= -1

        above = next_positions[:, axis] > upper_bound
        next_positions[above, axis] = 2 * upper_bound - next_positions[above, axis]
        next_velocities[above, axis] *= -1

    return next_positions, next_velocities


def build_graph(positions: FloatArray, communication_range: float) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(len(positions)))

    for node_id, (x, y) in enumerate(positions):
        graph.nodes[node_id]["x"] = float(x)
        graph.nodes[node_id]["y"] = float(y)

    deltas = positions[:, None, :] - positions[None, :, :]
    distances = np.linalg.norm(deltas, axis=2)
    source_ids, target_ids = np.where(
        np.triu((distances <= communication_range) & (distances > 0), k=1)
    )
    graph.add_edges_from(
        (int(source), int(target), {"distance": float(distances[source, target])})
        for source, target in zip(source_ids, target_ids, strict=True)
    )
    return graph
