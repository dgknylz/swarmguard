from __future__ import annotations

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
    navigation = build_navigation(st)
    render_site_header(st)
    render_topbar(st, navigation.title)
    navigation.run()
    render_footer(st)
