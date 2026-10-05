from ..components.methodology_center import render_methodology_center


def render_methodology_page() -> None:
    import streamlit as st

    render_methodology_center(st)
