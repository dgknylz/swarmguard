import numpy as np

from swarmguard.network import build_graph, move_with_reflection


def test_graph_contains_only_links_within_range() -> None:
    positions = np.array([[0.0, 0.0], [3.0, 4.0], [20.0, 0.0]])
    graph = build_graph(positions, communication_range=5.0)

    assert set(graph.edges) == {(0, 1)}
    assert graph.edges[0, 1]["distance"] == 5.0


def test_motion_reflects_at_boundary() -> None:
    positions = np.array([[9.0, 5.0]])
    velocities = np.array([[3.0, 0.0]])

    moved, reflected_velocity = move_with_reflection(positions, velocities, 10.0, 10.0)

    np.testing.assert_allclose(moved, [[8.0, 5.0]])
    np.testing.assert_allclose(reflected_velocity, [[-3.0, 0.0]])
