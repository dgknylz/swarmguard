"""Two-way control deck for β, γ and range with live Teorem 1–2 feedback.

The deck redraws σ̄, β* and the phase plane in the browser while a slider moves and
only reports the final values back, so the simulation re-runs once per release.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

from ..config import SimulationConfig
from ..engine import SimulationFrame

MAX_DECK_FRAMES = 120
MAX_LIVE_NODES = 200
MAX_DECK_RANGE = 600.0


def deck_arguments(config: SimulationConfig, frames: list[SimulationFrame]) -> dict[str, object]:
    """Arguments for the deck; ``frames`` must be the undefended run of ``config``.

    Positions are shipped for small swarms so the browser can recompute λ₁(t) for a
    new range while the slider moves; larger swarms keep the server-side spectrum.
    """
    measured = frames[1:] or frames
    stride = max(1, -(-len(measured) // MAX_DECK_FRAMES))
    sample = measured[::stride]
    node_count = len(frames[0].positions)
    return {
        "beta": config.beta,
        "gamma": config.gamma,
        "range": config.communication_range,
        "width": config.area_width,
        "height": config.area_height,
        "n": node_count,
        "max_range": MAX_DECK_RANGE,
        "radii": [round(float(frame.metrics.get("spectral_radius", 0.0)), 5) for frame in sample],
        "positions": (
            [[round(c, 1) for position in frame.positions for c in position] for frame in sample]
            if node_count <= MAX_LIVE_NODES
            else None
        ),
    }


@lru_cache(maxsize=1)
def _component():
    import streamlit.components.v1 as components

    path = files("swarmguard.dashboard").joinpath("assets", "controls")
    return components.declare_component("swarmguard_control_deck", path=str(path))


def render_control_deck(
    config: SimulationConfig, frames: list[SimulationFrame], *, key: str = "control-deck"
) -> dict[str, object] | None:
    return _component()(**deck_arguments(config, frames), key=key, default=None)
