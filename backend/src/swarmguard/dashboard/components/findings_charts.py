"""Charts of the project's headline findings (data: ``swarmguard.findings``).

Titles and legends are left to ``charts.render_chart``, which draws them as HTML so that
they wrap on narrow screens; every label inside a plot is short enough for a phone.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import log10, sqrt

from ..charts import GRID, PLOT_LAYOUT
from .experiment_center import METHOD_COLORS, METHOD_LABELS

INK, MUTED, MINT, AMBER, RED, ORANGE = (
    "#e6f4f2",
    "#7f989d",
    "#5eead4",
    "#fbbf24",
    "#fb7185",
    "#fb923c",
)
SAFE_FILL = "rgba(94,234,212,0.07)"
STEM = {"color": "rgba(147,169,173,0.5)", "width": 3}
RING = {"color": "#061014", "width": 2}


def _layout(figure, height: int, **extra):
    base = {**PLOT_LAYOUT, "margin": {"l": 10, "r": 10, "t": 30, "b": 10}}
    figure.update_layout(height=height, **{**base, **extra})
    figure.update_xaxes(gridcolor=GRID, zeroline=False)
    figure.update_yaxes(gridcolor=GRID, zeroline=False)
    return figure


def _ratio_axis(figure, multipliers: Sequence[float]) -> None:
    figure.update_xaxes(
        type="log",
        title="β / β*",
        tickvals=[0.5, 1, 2, 4, 8],
        ticktext=["0.5", "1", "2", "4", "8"],
        range=[log10(multipliers[0]), log10(multipliers[-1])],
    )
    figure.update_yaxes(title="Uzun dönem enfekte oranı", tickformat=".0%", rangemode="tozero")


def _top_label(figure, text: str, x: float, color: str, *, anchor: str = "left", log: bool = True):
    """A short label sitting on the top edge of the plot at data position x."""
    figure.add_annotation(
        x=log10(x) if log else x,
        y=1.0,
        yref="paper",
        text=text,
        showarrow=False,
        font={"color": color, "size": 11},
        xanchor=anchor,
        xshift=4 if anchor == "left" else 0,
        yanchor="bottom",
    )


def _row_label(figure, text: str, row: float, *, side: str = "left") -> None:
    """A label above a horizontal row, so the plot keeps the full width on a phone."""
    figure.add_annotation(
        x=0.0 if side == "left" else 1.0,
        xref="paper",
        y=row,
        text=text,
        showarrow=False,
        font={"color": INK if side == "left" else "#b7cbcb", "size": 11},
        xanchor=side,
        yanchor="bottom",
        yshift=9,
    )


def _guarantee_band(figure, first: float) -> None:
    figure.add_vrect(x0=first, x1=1, fillcolor=SAFE_FILL, line_width=0, layer="below")
    figure.add_vline(x=1, line={"color": AMBER, "width": 2})
    _top_label(figure, "garantili", sqrt(first), MINT, anchor="center")
    _top_label(figure, "<b>β*</b>", 1, AMBER)


def scenario_threshold_figure(
    sweep: Mapping[str, object], multipliers: Sequence[float], beta: float, endemic_level: float
):
    """Endemic level of one scenario against β/β*, with the guarantee and the observed onset."""
    import plotly.graph_objects as go

    levels = list(sweep["levels"])
    threshold = float(sweep["threshold_beta"])
    figure = go.Figure()
    figure.add_scatter(
        x=list(multipliers),
        y=levels,
        mode="lines+markers",
        line={"color": MINT, "width": 2.5},
        marker={"size": 5},
        customdata=[multiplier * threshold for multiplier in multipliers],
        hovertemplate="β/β* = %{x:.2f}<br>β = %{customdata:.4f}<br>enfekte %{y:.1%}<extra></extra>",
        showlegend=False,
    )
    _guarantee_band(figure, multipliers[0])
    figure.add_hline(y=endemic_level, line={"color": MUTED, "width": 1, "dash": "dot"})
    tightness = sweep.get("tightness")
    if tightness:
        figure.add_vline(x=tightness, line={"color": RED, "width": 1.5, "dash": "dash"})
        _top_label(figure, f"gözlenen ×{float(tightness):.2f}", float(tightness), INK)
    ratio = beta / threshold if threshold else float("inf")
    if multipliers[0] <= ratio <= multipliers[-1]:
        nearest = min(range(len(levels)), key=lambda index: abs(multipliers[index] - ratio))
        figure.add_scatter(
            x=[ratio],
            y=[levels[nearest]],
            mode="markers",
            marker={"symbol": "diamond", "size": 13, "color": AMBER, "line": RING},
            hovertemplate=f"Senaryonun β değeri {beta:.3f} (×{ratio:.2f})<extra></extra>",
            showlegend=False,
        )
    _layout(figure, 380)
    _ratio_axis(figure, multipliers)
    return figure


def threshold_collapse_figure(findings: Mapping[str, object], highlight: str | None = None):
    """Every scenario on the β/β* axis: the curves leave zero to the right of one."""
    import plotly.graph_objects as go

    multipliers = list(findings["sweep_multipliers"])
    figure = go.Figure()
    onsets = [float(item["tightness"]) for item in findings["thresholds"] if item["tightness"]]
    if onsets:
        figure.add_vrect(
            x0=min(onsets), x1=max(onsets), fillcolor="rgba(251,113,133,0.10)", line_width=0
        )
        _top_label(figure, f"gözlenen ×{min(onsets):.1f}–×{max(onsets):.1f}", min(onsets), INK)
    for item in findings["thresholds"]:
        chosen = item["slug"] == highlight
        figure.add_scatter(
            x=multipliers,
            y=item["levels"],
            mode="lines",
            line={
                "color": MINT if chosen else "rgba(147,169,173,0.55)",
                "width": 3 if chosen else 1.4,
            },
            name=item["title"],
            hovertemplate=(
                f"<b>{item['title']}</b> · n = {item['node_count']}<br>"
                f"β* = {item['threshold_beta']:.4f}<br>"
                "β/β* = %{x:.2f} · enfekte %{y:.1%}<extra></extra>"
            ),
            showlegend=False,
        )
    _guarantee_band(figure, multipliers[0])
    _layout(figure, 360)
    _ratio_axis(figure, multipliers)
    return figure


def ordering_figure(findings: Mapping[str, object]):
    """Dumbbell: Perron-ordered quarantine against the same defense in random order."""
    import plotly.graph_objects as go

    rows = list(findings["ordering"])[::-1]
    positions = list(range(len(rows)))
    figure = go.Figure()
    for position, row in zip(positions, rows, strict=True):
        figure.add_scatter(
            x=[row["shield"]["mean"], row["control"]["mean"]],
            y=[position, position],
            mode="lines",
            line=STEM,
            hoverinfo="skip",
            showlegend=False,
        )
        same = row["wins"] == 0 and row["losses"] == 0
        difference = f"{row['delta']['mean'] * 100:+.1f} puan · {row['wins']}–{row['losses']}"
        _row_label(figure, row["label"], position)
        _row_label(figure, "aynı sonuç" if same else difference, position, side="right")
    series = (
        ("control", "Rastgele sıra (kontrol)", ORANGE, "diamond"),
        ("shield", "Perron sırası (Spektral Kalkan)", MINT, "circle"),
    )
    for key, name, color, symbol in series:
        figure.add_scatter(
            x=[row[key]["mean"] for row in rows],
            y=positions,
            mode="markers",
            name=name,
            marker={"color": color, "size": 14, "symbol": symbol, "line": RING},
            customdata=[
                [row["label"], row[key]["ci95_low"], row[key]["ci95_high"]] for row in rows
            ],
            hovertemplate=(
                f"%{{customdata[0]}}<br>{name}<br>ortalama %{{x:.1%}}"
                "<br>%95 GA %{customdata[1]:.1%} – %{customdata[2]:.1%}<extra></extra>"
            ),
        )
    _layout(figure, 90 + 62 * len(rows))
    figure.update_xaxes(
        title="Ortalama enfeksiyon oranı", tickformat=".0%", range=[-0.04, 1.0], dtick=0.2
    )
    figure.update_yaxes(visible=False, range=[-0.5, len(rows) - 0.25])
    return figure


def _whiskers(statistics: Mapping[str, float]) -> dict[str, object]:
    return {
        "type": "data",
        "symmetric": False,
        "array": [statistics["ci95_high"] - statistics["mean"]],
        "arrayminus": [statistics["mean"] - statistics["ci95_low"]],
        "color": "rgba(147,169,173,0.55)",
        "thickness": 1.2,
        "width": 0,
    }


def tradeoff_figure(findings: Mapping[str, object]):
    """Security against connectivity for every method, one panel per setting."""
    from plotly.subplots import make_subplots

    tables = list(findings["tables"])
    figure = make_subplots(
        rows=1,
        cols=len(tables),
        shared_yaxes=True,
        horizontal_spacing=0.06,
        subplot_titles=[table["label"].split(" · ")[0] for table in tables],
    )
    for column, table in enumerate(tables, start=1):
        # Spektral Kalkan is drawn last so its star stays on top of coinciding points.
        for row in sorted(table["rows"], key=lambda row: row["method"] == "spectral_shield"):
            method = row["method"]
            hero = method == "spectral_shield"
            figure.add_scatter(
                x=[row["infection"]["mean"]],
                y=[row["connectivity"]["mean"]],
                mode="markers",
                name=METHOD_LABELS[method],
                showlegend=column == 1,
                marker={
                    "color": METHOD_COLORS[method],
                    "size": 18 if hero else 12,
                    "symbol": "star" if hero else "circle",
                    "line": RING,
                },
                error_x=_whiskers(row["infection"]),
                error_y=_whiskers(row["connectivity"]),
                hovertemplate=(
                    f"<b>{METHOD_LABELS[method]}</b><br>{table['label']}"
                    "<br>enfeksiyon %{x:.1%}<br>en büyük bileşen %{y:.1%}"
                    f"<br>maliyet {row['cost']:.1f}<extra></extra>"
                ),
                row=1,
                col=column,
            )
    figure.add_annotation(
        x=0.0,
        xref="paper",
        y=0.0,
        yref="paper",
        text="↖ daha iyi",
        showarrow=False,
        font={"color": MUTED, "size": 11},
        xanchor="left",
        yanchor="bottom",
        xshift=8,
        yshift=6,
    )
    _layout(figure, 380)
    figure.update_annotations(font_size=12)
    figure.update_xaxes(title="Enfeksiyon oranı", tickformat=".0%", range=[-0.06, 1.0], dtick=0.5)
    figure.update_yaxes(tickformat=".0%")
    figure.update_yaxes(title="En büyük bileşen", col=1)
    return figure


def tightness_figure(findings: Mapping[str, object]):
    """Observed onset over β* per scenario, ordered from the sparsest to the densest swarm."""
    import plotly.graph_objects as go

    items = [item for item in findings["thresholds"] if item["tightness"]]
    ordered = sorted(items, key=lambda item: -item["mean_spectral_radius"])
    positions = list(range(len(ordered)))
    upper = max(item["tightness"] for item in ordered) + 0.7
    figure = go.Figure()
    figure.add_vrect(x0=0, x1=1, fillcolor=SAFE_FILL, line_width=0, layer="below")
    figure.add_vline(x=1, line={"color": AMBER, "width": 2})
    for position, item in zip(positions, ordered, strict=True):
        figure.add_scatter(
            x=[1, item["tightness"]],
            y=[position, position],
            mode="lines",
            line=STEM,
            hoverinfo="skip",
            showlegend=False,
        )
        name = item["title"].split(" · ")[0]
        _row_label(figure, f"{name} · λ₁ {item['mean_spectral_radius']:.1f}", position)
    figure.add_scatter(
        x=[item["tightness"] for item in ordered],
        y=positions,
        mode="markers+text",
        marker={"color": MINT, "size": 13, "line": RING},
        text=[f"×{item['tightness']:.2f}" for item in ordered],
        textposition="middle right",
        textfont={"color": INK, "size": 11},
        customdata=[
            [item["title"], item["threshold_beta"], item["empirical_beta"], item["node_count"]]
            for item in ordered
        ],
        hovertemplate=(
            "<b>%{customdata[0]}</b> · n = %{customdata[3]}"
            "<br>β* = %{customdata[1]:.4f} · gözlenen %{customdata[2]:.4f}"
            "<br>oran ×%{x:.2f}<extra></extra>"
        ),
        showlegend=False,
        cliponaxis=False,
    )
    _top_label(figure, "garantili", 0.5, MINT, anchor="center", log=False)
    _top_label(figure, "<b>β*</b>", 1, AMBER, log=False)
    _layout(figure, 70 + 46 * len(ordered))
    figure.update_xaxes(title="Gözlenen eşik / β*", range=[0, upper], ticksuffix="×", dtick=1)
    figure.update_yaxes(visible=False, range=[-0.5, len(ordered) - 0.2])
    return figure
