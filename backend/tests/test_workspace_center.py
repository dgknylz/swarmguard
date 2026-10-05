import json

import pytest

from swarmguard import SimulationEngine
from swarmguard.config import SimulationConfig
from swarmguard.dashboard.components.workspace_center import (
    MAX_BUNDLE_BYTES,
    WORKSPACE_SCHEMA,
    apply_workspace,
    decode_workspace,
    encode_workspace,
)
from swarmguard.dashboard.simulation_session import PlaybackStatus


def sample_state() -> dict[str, object]:
    config = SimulationConfig(node_count=8, steps=3, speed=0, seed=17)
    return {
        "config": config,
        "frames": SimulationEngine(config).run(),
        "experiment_history": [{"experiment_id": "demo-experiment", "kind": "test"}],
        "selected_uav": 4,
        "analysis_step": 2,
    }


def test_workspace_bundle_round_trip_preserves_research_state() -> None:
    state = sample_state()
    bundle = encode_workspace(state)
    snapshot = decode_workspace(bundle)

    assert snapshot.config == state["config"]
    assert list(snapshot.frames) == state["frames"]
    assert snapshot.experiments[0]["experiment_id"] == "demo-experiment"
    assert snapshot.selected_node == 4
    assert snapshot.analysis_step == 2
    assert snapshot.checksum.startswith("sha256:")


def test_workspace_bundle_rejects_tampering_and_unknown_schema() -> None:
    envelope = json.loads(encode_workspace(sample_state()))
    envelope["payload"]["config"]["seed"] = 99
    tampered = json.dumps(envelope).encode("utf-8")

    with pytest.raises(ValueError, match="bütünlük"):
        decode_workspace(tampered)

    envelope["schema_version"] = "99.0"
    with pytest.raises(ValueError, match="şema sürümü"):
        decode_workspace(json.dumps(envelope).encode("utf-8"))


def test_workspace_bundle_enforces_size_and_active_simulation_requirements() -> None:
    with pytest.raises(ValueError, match="aktif bir simülasyon"):
        encode_workspace({})
    with pytest.raises(ValueError, match="25 MB"):
        decode_workspace(b"x" * (MAX_BUNDLE_BYTES + 1))


def test_apply_workspace_restores_context_and_paused_playback() -> None:
    snapshot = decode_workspace(encode_workspace(sample_state()))
    target: dict[str, object] = {"unrelated": "preserve"}
    apply_workspace(target, snapshot)

    assert target["unrelated"] == "preserve"
    assert target["config"] == snapshot.config
    assert target["selected_uav"] == 4
    assert target["node_picker"] == 4
    assert target["replay_cursor"] == 2
    assert target["active_experiment_id"] == "demo-experiment"
    assert target["playback"].status is PlaybackStatus.PAUSED
    assert target["playback"].index == 2


def test_workspace_schema_constant_is_stable() -> None:
    assert WORKSPACE_SCHEMA == "1.0"
