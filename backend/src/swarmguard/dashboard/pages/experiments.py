from __future__ import annotations

from ...presets import DEMO_CONFIG
from ..components.comparison_panel import render_comparison_panel
from ..components.experiment_center import render_experiment_center
from ..components.report_center import render_report_center


def render_experiments_page() -> None:
    import streamlit as st

    config = st.session_state.get("config", DEMO_CONFIG)
    view = st.segmented_control(
        "Deney bölümü",
        options=("center", "comparison", "report"),
        default="center",
        format_func={
            "center": "🧪 Deney Merkezi",
            "comparison": "⇄ Karşılaştırma",
            "report": "▤ Rapor Merkezi",
        }.get,
        key="experiments-view",
        label_visibility="collapsed",
        width="stretch",
    )
    history = st.session_state.get("experiment_history", [])
    if view == "center":
        render_experiment_center(st, config)
    elif view == "comparison":
        render_comparison_panel(st, history)
    else:
        render_report_center(st, history)
