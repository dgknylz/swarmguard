from dataclasses import replace

import pytest

from swarmguard import SimulationEngine
from swarmguard.config import DefenseStrategy
from swarmguard.dashboard.components.node_inspector import build_node_snapshot
from swarmguard.presets import DEMO_CONFIG


@pytest.fixture(scope="module")
def demo_frames():
    return SimulationEngine(DEMO_CONFIG).run()


def test_node_snapshot_calculates_network_and_risk_attributes(demo_frames) -> None:
    frame_index = 10
    node_id = 6
    snapshot = build_node_snapshot(demo_frames, frame_index, node_id)
    frame = demo_frames[frame_index]
    expected_neighbors = {
        target if source == node_id else source
        for source, target in frame.edges
        if source == node_id or target == node_id
    }

    assert snapshot.node_id == node_id
    assert snapshot.degree == len(expected_neighbors)
    assert snapshot.neighbors == tuple(sorted(expected_neighbors))
    assert 0 <= snapshot.infected_neighbor_ratio <= 1
    assert 0 <= snapshot.betweenness <= 1
    assert snapshot.risk == pytest.approx(0.863266)


def test_node_snapshot_collects_historical_events_and_rejects_invalid_id(demo_frames) -> None:
    infected_event = next(
        event for frame in demo_frames for event in frame.events if event.event_type == "infected"
    )
    snapshot = build_node_snapshot(demo_frames, len(demo_frames) - 1, infected_event.node_id)

    assert any(event.event_type == "infected" for event in snapshot.events)
    assert all(event.step <= demo_frames[-1].step for event in snapshot.events)

    with pytest.raises(ValueError, match="Geçersiz İHA kimliği"):
        build_node_snapshot(demo_frames, 0, 10_000)


def test_node_snapshot_tracks_quarantine_history() -> None:
    config = replace(DEMO_CONFIG, defense_strategy=DefenseStrategy.CENTRALITY_QUARANTINE)
    frames = SimulationEngine(config).run()
    quarantine_event = next(
        event for frame in frames for event in frame.events if event.event_type == "quarantine_node"
    )
    snapshot = build_node_snapshot(frames, len(frames) - 1, quarantine_event.node_id)

    assert snapshot.quarantined is True
    assert any(event.event_type == "quarantine_node" for event in snapshot.events)
