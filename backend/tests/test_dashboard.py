from swarmguard import SimulationEngine
from swarmguard.presets import DEMO_CONFIG
from swarmguard.streamlit_dashboard import frames_to_records, topology_figure


def test_demo_scenario_is_repeatable_and_dashboard_ready() -> None:
    first = SimulationEngine(DEMO_CONFIG).run()
    second = SimulationEngine(DEMO_CONFIG).run()

    assert [frame.positions for frame in first] == [frame.positions for frame in second]
    assert [frame.edges for frame in first] == [frame.edges for frame in second]
    assert [frame.infected for frame in first] == [frame.infected for frame in second]
    assert len(first) == DEMO_CONFIG.steps + 1
    assert len(frames_to_records(first)) == len(first)
    assert len(topology_figure(first[-1]).data) == 2
