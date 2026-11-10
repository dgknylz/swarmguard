from __future__ import annotations

from dataclasses import dataclass
from html import escape
from math import exp, log

from ..config import SimulationConfig
from ..engine import SimulationFrame

PLOT_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#93a9ad", "family": "Inter, Segoe UI, sans-serif", "size": 12},
    "margin": {"l": 10, "r": 10, "t": 30, "b": 10},
    "hoverlabel": {"bgcolor": "#08151a", "bordercolor": "#24414a", "font": {"color": "#e6f4f2"}},
    "legend": {"orientation": "h", "y": 1.08, "x": 0, "bgcolor": "rgba(0,0,0,0)"},
}
GRID = "rgba(148,197,202,0.08)"
LEGEND_DASH = {"dash": "dashed", "dot": "dotted", "dashdot": "dashed", "longdash": "dashed"}
FILLED = ("toself", "tozeroy", "tozerox", "tonexty", "tonextx")


def _legend_swatch(trace) -> str:
    """A small HTML mark that mirrors how the trace is drawn."""
    marker, line = getattr(trace, "marker", None), getattr(trace, "line", None)
    mode = getattr(trace, "mode", None) or ""
    if getattr(trace, "fill", None) in FILLED and line is not None and line.width == 0:
        return f'<i class="box" style="background:{trace.fillcolor}"></i>'
    if trace.type == "bar":
        color = marker.color if isinstance(marker.color, str) else "#7f989d"
        return f'<i class="box" style="background:{color}"></i>'
    if "lines" in mode or (not mode and line is not None and line.color):
        dash = LEGEND_DASH.get(line.dash or "", "solid")
        return f'<i class="line" style="border-top:2px {dash} {line.color}"></i>'
    color = marker.color if marker is not None and isinstance(marker.color, str) else "#7f989d"
    symbol = str(getattr(marker, "symbol", "") or "")
    if symbol.startswith("star"):
        return f'<b style="color:{color}">★</b>'
    kind = "diamond" if symbol.startswith("diamond") else "dot"
    return f'<i class="{kind}" style="background:{color}"></i>'


def legend_html(figure) -> str:
    """The figure's legend as wrapping HTML chips; empty when fewer than two series."""
    chips: dict[str, str] = {}
    for trace in figure.data:
        name = getattr(trace, "name", None)
        if name and trace.showlegend is not False and name not in chips:
            chips[name] = f"<span>{_legend_swatch(trace)}{escape(name)}</span>"
    if len(chips) < 2:
        return ""
    return f'<div class="sg-chart-legend">{"".join(chips.values())}</div>'


def render_chart(target, figure, *, title: str | None = None, key: str | None = None) -> None:
    """Draw a figure with its title and legend as HTML above it.

    Plotly neither wraps a title nor reflows a legend, so on a narrow screen both collide
    with the axes; HTML wraps. The figure itself keeps only the plot.
    """
    title = title or (figure.layout.meta or {}).get("title")
    head = (f'<div class="sg-chart-title">{escape(title)}</div>' if title else "") + legend_html(
        figure
    )
    if head:
        target.markdown(f'<div class="sg-chart-head">{head}</div>', unsafe_allow_html=True)
    figure.update_layout(showlegend=False)
    target.plotly_chart(figure, width="stretch", key=key, config={"displayModeBar": False})


@dataclass(frozen=True, slots=True)
class RunSummary:
    peak_infected: float
    final_infected: float
    mean_infected: float
    mean_component: float
    geometric_sigma: float
    intervention_cost: float


def spread_factors(frames: list[SimulationFrame], config: SimulationConfig) -> list[float]:
    """σ(t) = 1 − γ + β·λ₁(A(t)) for the graphs of steps 1…T (Teorem 2)."""
    return [
        1 - config.gamma + config.beta * float(frame.metrics.get("spectral_radius", 0.0))
        for frame in frames[1:]
    ]


def summarize_run(frames: list[SimulationFrame], config: SimulationConfig) -> RunSummary:
    measured = frames[1:] or frames
    factors = spread_factors(frames, config)
    geometric = (
        exp(sum(log(max(value, 1e-12)) for value in factors) / len(factors)) if factors else 0.0
    )
    return RunSummary(
        peak_infected=max(float(frame.metrics["infected_ratio"]) for frame in measured),
        final_infected=float(frames[-1].metrics["infected_ratio"]),
        mean_infected=sum(float(frame.metrics["infected_ratio"]) for frame in measured)
        / len(measured),
        mean_component=sum(float(frame.metrics["largest_component_ratio"]) for frame in measured)
        / len(measured),
        geometric_sigma=geometric,
        intervention_cost=sum(
            float(frame.defense_report["intervention_cost"])
            for frame in measured
            if frame.defense_report is not None
        ),
    )


def timeseries_figure(frames: list[SimulationFrame], config: SimulationConfig):
    from plotly.subplots import make_subplots

    steps = [frame.step for frame in frames]
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_scatter(
        x=steps,
        y=[float(frame.metrics["infected_ratio"]) for frame in frames],
        name="Enfekte oranı",
        line={"color": "#fb7185", "width": 2.4},
        fill="tozeroy",
        fillcolor="rgba(251,113,133,0.12)",
    )
    figure.add_scatter(
        x=steps,
        y=[float(frame.metrics["largest_component_ratio"]) for frame in frames],
        name="En büyük bileşen",
        line={"color": "#5eead4", "width": 2},
    )
    figure.add_scatter(
        x=steps,
        y=[float(frame.metrics["global_efficiency"]) for frame in frames],
        name="Ağ verimliliği",
        line={"color": "#38bdf8", "width": 1.6, "dash": "dot"},
    )
    figure.add_scatter(
        x=steps[1:],
        y=spread_factors(frames, config),
        name="σ(t) spektral baskı",
        line={"color": "#fbbf24", "width": 1.8},
        secondary_y=True,
    )
    figure.add_hline(
        y=1,
        line={"color": "rgba(251,191,36,0.55)", "dash": "dash", "width": 1},
        secondary_y=True,
        annotation_text="σ = 1 eşiği",
        annotation_font_color="#fbbf24",
    )
    figure.update_layout(height=380, hovermode="x unified", **PLOT_LAYOUT)
    figure.update_layout(margin={"l": 10, "r": 10, "t": 16, "b": 10})
    figure.update_xaxes(title="Zaman adımı", gridcolor=GRID, zeroline=False)
    figure.update_yaxes(title="Oran", range=[0, 1.02], gridcolor=GRID, secondary_y=False)
    figure.update_yaxes(title="σ(t)", showgrid=False, secondary_y=True)
    return figure


def duel_figure(runs: list[tuple[str, list[SimulationFrame], str]], config: SimulationConfig):
    """Infection, largest component and σ(t) of two runs that share a seed."""
    from plotly.subplots import make_subplots

    figure = make_subplots(
        rows=1,
        cols=3,
        # Short titles: three panels share a phone screen; the full names are in the header.
        subplot_titles=("Enfekte", "Bileşen", "σ(t)"),
        horizontal_spacing=0.06,
    )
    for label, frames, color in runs:
        steps = [frame.step for frame in frames]
        for column, values in (
            (1, [float(frame.metrics["infected_ratio"]) for frame in frames]),
            (2, [float(frame.metrics["largest_component_ratio"]) for frame in frames]),
        ):
            figure.add_scatter(
                x=steps,
                y=values,
                name=label,
                legendgroup=label,
                showlegend=column == 1,
                line={"color": color, "width": 2.4},
                row=1,
                col=column,
            )
        figure.add_scatter(
            x=steps[1:],
            y=spread_factors(frames, config),
            name=label,
            legendgroup=label,
            showlegend=False,
            line={"color": color, "width": 1.8},
            row=1,
            col=3,
        )
    figure.add_hline(y=1, line={"color": "rgba(251,191,36,0.6)", "dash": "dash"}, row=1, col=3)
    figure.update_layout(height=330, hovermode="x unified", **PLOT_LAYOUT)
    figure.update_xaxes(gridcolor=GRID, zeroline=False)
    figure.update_yaxes(gridcolor=GRID, zeroline=False)
    return figure


def infection_map_figure(frames: list[SimulationFrame]):
    """UAV × time raster: healthy, quarantined and infected cells; rows ordered by
    first infection so the cascade reads top to bottom."""
    import plotly.graph_objects as go

    node_count = len(frames[0].positions)
    first: dict[int, int] = {}
    for frame in frames:
        for node in frame.infected:
            first.setdefault(node, frame.step)
    order = sorted(range(node_count), key=lambda node: (first.get(node, 10**9), node))
    grid = [
        [
            1.0 if node in set(frame.infected) else 0.5 if node in set(frame.quarantined) else 0.0
            for frame in frames
        ]
        for node in order
    ]
    figure = go.Figure(
        go.Heatmap(
            z=grid,
            x=[frame.step for frame in frames],
            y=[f"UAV-{node:02d}" for node in order],
            zmin=0,
            zmax=1,
            colorscale=[
                [0.0, "#0b1e24"],
                [0.33, "#0b1e24"],
                [0.34, "#fbbf24"],
                [0.66, "#fbbf24"],
                [0.67, "#fb7185"],
                [1.0, "#fb7185"],
            ],
            showscale=False,
            xgap=1,
            ygap=1,
            hovertemplate="%{y} · t=%{x}<extra></extra>",
        )
    )
    figure.update_layout(height=max(320, 14 * node_count + 80), **PLOT_LAYOUT)
    figure.update_xaxes(title="Zaman adımı", showgrid=False)
    figure.update_yaxes(autorange="reversed", showgrid=False, tickfont={"size": 9})
    return figure


def frames_to_records(frames: list[SimulationFrame]) -> list[dict[str, float | int]]:
    return [
        {
            "step": frame.step,
            "infected_ratio": float(frame.metrics["infected_ratio"]),
            "largest_component_ratio": float(frame.metrics["largest_component_ratio"]),
            "global_efficiency": float(frame.metrics["global_efficiency"]),
            "algebraic_connectivity": float(frame.metrics["algebraic_connectivity"]),
        }
        for frame in frames
    ]


def topology_figure(frame: SimulationFrame):
    import plotly.graph_objects as go

    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for source, target in frame.edges:
        edge_x.extend([frame.positions[source][0], frame.positions[target][0], None])
        edge_y.extend([frame.positions[source][1], frame.positions[target][1], None])

    infected = set(frame.infected)
    colors = ["#fb7185" if node in infected else "#6ee7b7" for node in range(len(frame.positions))]
    labels = [f"UAV-{node:02d}" for node in range(len(frame.positions))]
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line={"color": "rgba(87,231,214,0.22)", "width": 1},
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[position[0] for position in frame.positions],
            y=[position[1] for position in frame.positions],
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker={"color": colors, "size": 15, "line": {"color": "#07161b", "width": 1}},
            customdata=[
                [node, "Enfekte" if node in infected else "Sağlıklı"]
                for node in range(len(frame.positions))
            ],
            hovertemplate="%{text}<br>%{customdata[1]}<br>Seçmek için tıkla<extra></extra>",
        )
    )
    figure.update_layout(
        height=620,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        paper_bgcolor="#08151a",
        plot_bgcolor="#08151a",
        showlegend=False,
        xaxis={"visible": False},
        yaxis={"visible": False, "scaleanchor": "x", "scaleratio": 1},
    )
    return figure
