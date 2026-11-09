import json
from dataclasses import replace
from itertools import pairwise

import numpy as np

from swarmguard import SimulationEngine
from swarmguard.dashboard.player import (
    MAX_PLAYER_FRAMES,
    build_player_payload,
    player_html,
    spectral_vectors,
)
from swarmguard.presets import DEMO_CONFIG


def test_payload_carries_frames_metrics_and_math_layers() -> None:
    config = replace(DEMO_CONFIG, steps=12)
    frames = SimulationEngine(config).run()
    payload = build_player_payload(frames, config, view="3d")

    assert payload["meta"]["view"] == "3d"
    assert len(payload["frames"]) == len(frames)
    first = payload["frames"][0]
    assert len(first["p"]) == 2 * config.node_count
    assert len(first["m"]) == 5
    assert len(first["u"]) == len(first["v"]) == config.node_count
    assert min(first["u"]) >= 0


def test_fiedler_signs_are_aligned_between_frames() -> None:
    frames = SimulationEngine(replace(DEMO_CONFIG, steps=30)).run()
    vectors = spectral_vectors(frames, DEMO_CONFIG.node_count)

    assert vectors is not None
    for (_, previous), (_, current) in pairwise(vectors):
        assert float(np.dot(previous, current)) >= 0


def test_long_runs_are_strided_and_html_cannot_be_broken_out_of() -> None:
    config = replace(
        DEMO_CONFIG, node_count=6, initial_infected_count=1, steps=2 * MAX_PLAYER_FRAMES
    )
    frames = SimulationEngine(config).run()
    payload = build_player_payload(frames, config)
    payload["meta"]["defense"] = "</script><script>alert(1)</script>"
    html = player_html(payload)

    assert len(payload["frames"]) <= MAX_PLAYER_FRAMES + 1
    assert payload["frames"][-1]["t"] == config.steps
    assert "</script><script>alert(1)" not in html
    data = html.split('type="application/json">', 1)[1].split("</script>", 1)[0]
    assert json.loads(data)["meta"]["defense"].startswith("</script>")
