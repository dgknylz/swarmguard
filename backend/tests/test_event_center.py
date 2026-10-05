import json

from swarmguard import SimulationEngine
from swarmguard.dashboard.components.event_center import (
    collect_events,
    export_events_csv,
    export_events_json,
    filter_events,
    summarize_events,
)
from swarmguard.presets import DEMO_CONFIG


def test_event_center_collects_and_summarizes_complete_history() -> None:
    frames = SimulationEngine(DEMO_CONFIG).run()
    events = collect_events(frames)
    summary = summarize_events(events)

    assert len(events) == sum(len(frame.events) for frame in frames)
    assert len({event.event_id for event in events}) == len(events)
    assert summary.total == len(events)
    assert summary.attacks > 0
    assert summary.defenses > 0
    assert summary.affected_nodes <= DEMO_CONFIG.node_count


def test_event_center_combines_category_node_type_and_time_filters() -> None:
    frames = SimulationEngine(DEMO_CONFIG).run()
    events = collect_events(frames)
    infected = next(event for event in events if event.event_type == "infected")
    filtered = filter_events(
        events,
        categories=("Saldırı",),
        event_types=("infected",),
        node_id=infected.node_id,
        step_range=(infected.step, infected.step),
    )

    assert filtered
    assert all(event.category == "Saldırı" for event in filtered)
    assert all(event.event_type == "infected" for event in filtered)
    assert all(event.step == infected.step for event in filtered)
    assert all(
        event.node_id == infected.node_id or event.target_node_id == infected.node_id
        for event in filtered
    )


def test_event_exports_preserve_unicode_and_filtered_rows() -> None:
    frames = SimulationEngine(DEMO_CONFIG).run()
    events = filter_events(collect_events(frames), categories=("Savunma",))
    csv_data = export_events_csv(events)
    json_data = export_events_json(events)
    decoded_json = json.loads(json_data.decode("utf-8"))

    assert csv_data.startswith(b"\xef\xbb\xbf")
    assert csv_data.count(b"\n") == len(events) + 1
    assert len(decoded_json) == len(events)
    assert all(row["category"] == "Savunma" for row in decoded_json)
