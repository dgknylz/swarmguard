from ..components.workspace_center import render_workspace_center


def render_workspace_page() -> None:
    import streamlit as st

    render_workspace_center(st)
