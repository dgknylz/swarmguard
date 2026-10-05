from __future__ import annotations

from ..engine import SimulationFrame


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
