from ...presets import SHOWCASE_CONFIG
from ..components.theory_lab import render_theory_lab


def render_theory_page() -> None:
    import streamlit as st

    render_theory_lab(st, st.session_state.get("config", SHOWCASE_CONFIG))
