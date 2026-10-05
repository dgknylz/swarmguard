"""Backward-compatible imports for the Streamlit dashboard."""

from .dashboard.app import run_dashboard as render_app
from .dashboard.charts import frames_to_records, topology_figure

__all__ = ["frames_to_records", "render_app", "topology_figure"]
