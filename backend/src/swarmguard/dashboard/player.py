"""Browser-side swarm player.

The whole run is shipped to the client once and animated on a canvas there, so playback
is smooth (interpolated 60 fps motion) and never waits on a Streamlit rerun.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from math import ceil

from ..config import SimulationConfig
from ..engine import SimulationFrame
from ..spectral import adjacency_from_edges, spectral_radius
from .components.scenario_builder import DEFENSE_LABELS

MAX_PLAYER_FRAMES = 600
MAX_PLAYER_EDGES = 400_000
FRAME_METRICS = (
    "infected_ratio",
    "largest_component_ratio",
    "global_efficiency",
    "algebraic_connectivity",
)


def player_stride(frames: list[SimulationFrame]) -> int:
    """Smallest frame stride that keeps the payload within the browser budget."""
    stride = max(1, ceil(len(frames) / MAX_PLAYER_FRAMES))
    edge_total = sum(len(frame.edges) for frame in frames)
    while edge_total / stride > MAX_PLAYER_EDGES and stride < len(frames):
        stride += 1
    return stride


def _flat(pairs: tuple[tuple[int, int], ...]) -> list[int]:
    return [node for pair in pairs for node in pair]


def _frame_payload(frame: SimulationFrame, node_count: int) -> dict[str, object]:
    metrics = frame.metrics
    radius = metrics.get("spectral_radius")
    if radius is None:  # frames imported from bundles written before λ₁ was recorded
        radius = spectral_radius(adjacency_from_edges(node_count, frame.edges))
    return {
        "t": frame.step,
        "p": [round(coordinate, 1) for position in frame.positions for coordinate in position],
        "e": _flat(frame.edges),
        "i": list(frame.infected),
        "d": list(frame.detected),
        "a": _flat(frame.added_edges),
        "x": _flat(frame.removed_edges),
        "q": list(frame.quarantined),
        "m": [round(float(metrics.get(key, 0.0)), 5) for key in FRAME_METRICS]
        + [round(float(radius), 5)],
        "ev": [[event.event_type, event.node_id, event.target_node_id] for event in frame.events],
    }


def build_player_payload(
    frames: list[SimulationFrame],
    config: SimulationConfig,
    *,
    compact: bool = False,
    autoplay: bool = False,
) -> dict[str, object]:
    stride = player_stride(frames)
    selected = list(frames[::stride])
    if selected[-1] is not frames[-1]:
        selected.append(frames[-1])
    node_count = len(frames[0].positions)
    return {
        "meta": {
            "w": config.area_width,
            "h": config.area_height,
            "r": config.communication_range,
            "n": node_count,
            "beta": config.beta,
            "gamma": config.gamma,
            "q": config.detection_probability,
            "multiplier": config.defense_range_multiplier,
            "defense": DEFENSE_LABELS.get(config.defense_strategy, config.defense_strategy.value),
            "compact": compact,
            "autoplay": autoplay,
            "notice": (
                f"Akıcı oynatma için her {stride}. kare gösteriliyor." if stride > 1 else ""
            ),
        },
        "frames": [_frame_payload(frame, node_count) for frame in selected],
    }


@lru_cache(maxsize=1)
def _template() -> str:
    return (
        files("swarmguard.dashboard")
        .joinpath("assets", "swarm_player.html")
        .read_text(encoding="utf-8")
    )


def player_html(payload: dict[str, object]) -> str:
    # "<" is escaped so no value can close the JSON <script> block early.
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return _template().replace("__SWARM_DATA__", data)


def render_swarm_player(
    st,
    frames: list[SimulationFrame],
    config: SimulationConfig,
    *,
    height: int = 680,
    compact: bool = False,
    autoplay: bool = False,
) -> None:
    import streamlit.components.v1 as components

    payload = build_player_payload(frames, config, compact=compact, autoplay=autoplay)
    components.html(player_html(payload), height=height, scrolling=False)
