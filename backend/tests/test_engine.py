from swarmguard import SimulationConfig, SimulationEngine


def test_same_seed_produces_identical_run() -> None:
    config = SimulationConfig(node_count=12, steps=8, seed=7)

    first = [frame.to_dict() for frame in SimulationEngine(config).run()]
    second = [frame.to_dict() for frame in SimulationEngine(config).run()]

    assert first == second


def test_run_contains_initial_frame_and_requested_steps() -> None:
    config = SimulationConfig(node_count=10, steps=5, seed=11)
    frames = SimulationEngine(config).run()

    assert len(frames) == 6
    assert [frame.step for frame in frames] == list(range(6))


def test_metrics_stay_in_valid_ranges() -> None:
    config = SimulationConfig(node_count=15, steps=4, seed=3)

    for frame in SimulationEngine(config).run():
        metrics = frame.metrics
        assert 0 <= metrics["infected_ratio"] <= 1
        assert 0 < metrics["largest_component_ratio"] <= 1
        assert 0 <= metrics["global_efficiency"] <= 1
        assert metrics["algebraic_connectivity"] >= 0


def test_each_simulation_step_contains_defense_report() -> None:
    frames = SimulationEngine(SimulationConfig(node_count=8, steps=2, seed=5)).run()

    assert frames[0].defense_report is None
    assert frames[1].defense_report == {
        "algorithm": "none",
        "step": 1,
        "applied_actions": [],
        "rejected_actions": [],
        "intervention_cost": 0.0,
        "metadata": {},
    }
