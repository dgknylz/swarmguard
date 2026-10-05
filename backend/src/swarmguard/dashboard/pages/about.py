from ..components.about_center import render_about_center


def render_about_page() -> None:
    import streamlit as st

    render_about_center(st)
