from __future__ import annotations

from ..presets import DEMO_CONFIG
from .components.shell import (
    render_footer,
    render_site_header,
    render_topbar,
)
from .navigation import build_navigation
from .theme import apply_theme


def run_dashboard() -> None:
    import streamlit as st

    st.set_page_config(
        page_title="SwarmGuard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_theme(st)
    # Every page works on the same scenario; start from the demo so the header and the
    # experiment pages agree before the simulation page is ever opened.
    st.session_state.setdefault("config", DEMO_CONFIG)
    navigation = build_navigation(st)
    render_site_header(st)
    render_topbar(st, navigation.title)
    navigation.run()
    render_footer(st)
