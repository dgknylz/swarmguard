"""Charts of the project's headline findings (data: ``swarmguard.findings``)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import log10

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
RING = {"color": "#061014", "width": 2}
LEGEND_BELOW = {
    "orientation": "h",
    "yanchor": "top",
    "y": -0.24,
    "x": 0,
    "bgcolor": "rgba(0,0,0,0)",
}


def _layout(figure, height: int, **extra):
    base = {**PLOT_LAYOUT, "margin": {"l": 10, "r": 10, "t": 44, "b": 10}}
    figure.update_layout(height=height, **{**base, **extra})
    figure.update_xaxes(gridcolor=GRID, zeroline=False)
    figure.update_yaxes(gridcolor=GRID, zeroline=False)
    return figure


def _ratio_axis(figure, multipliers: Sequence[float]) -> None:
    figure.update_xaxes(
        type="log",
        title="β / β*  (Teorem 2 eşiğine oran)",
        tickvals=[0.5, 1, 2, 4, 8],
        ticktext=["0.5", "1", "2", "4", "8"],
        range=[log10(multipliers[0]), log10(multipliers[-1])],
    )
    figure.update_yaxes(title="Uzun dönem enfekte oranı", tickformat=".0%", rangemode="tozero")


def _note(figure, text: str, x: float, y: float, color: str = INK) -> None:
    """A left-aligned label at data x (log axis) and paper y."""
    figure.add_annotation(
        x=log10(x),
        y=y,
        yref="paper",
        text=text,
        showarrow=False,
        align="left",
        font={"color": color, "size": 11},
        xanchor="left",
        xshift=6,
        yanchor="top",
    )


def _guarantee_band(figure, first: float) -> None:
    figure.add_vrect(x0=first, x1=1, fillcolor=SAFE_FILL, line_width=0, layer="below")
    figure.add_vline(x=1, line={"color": AMBER, "width": 2})
    _note(figure, "<b>β*</b>", 1, 1.0, AMBER)
    _note(figure, "Teorem 2:<br>sönüm garantili", first, 1.0, MINT)


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
        _note(figure, f"gözlenen eşik<br>×{float(tightness):.2f}", float(tightness), 0.7)
    ratio = beta / threshold if threshold else float("inf")
    if multipliers[0] <= ratio <= multipliers[-1]:
        nearest = min(range(len(levels)), key=lambda index: abs(multipliers[index] - ratio))
        figure.add_scatter(
            x=[ratio],
            y=[levels[nearest]],
            mode="markers+text",
            marker={"symbol": "diamond", "size": 13, "color": AMBER, "line": RING},
            text=[f"senaryo β (×{ratio:.2f})"],
            textposition="top center",
            textfont={"color": INK, "size": 11},
            hovertemplate=f"Senaryonun β değeri {beta:.3f}<extra></extra>",
            showlegend=False,
        )
    else:
        figure.add_annotation(
            x=1.0,
            xref="paper",
            y=0.1,
            yref="paper",
            text=f"senaryo β = ×{ratio:.1f} →",
            showarrow=False,
            font={"color": INK, "size": 11},
            xanchor="right",
        )
    _layout(figure, 400, title="Bu senaryoda garanti nerede bitiyor, salgın nerede başlıyor?")
    _ratio_axis(figure, multipliers)
    return figure


def threshold_collapse_figure(findings: Mapping[str, object], highlight: str | None = None):
    """Every scenario on the β/β* axis: the curves leave zero right after one."""
    import plotly.graph_objects as go

    multipliers = list(findings["sweep_multipliers"])
    figure = go.Figure()
    onsets = [float(item["tightness"]) for item in findings["thresholds"] if item["tightness"]]
    if onsets:
        figure.add_vrect(
            x0=min(onsets), x1=max(onsets), fillcolor="rgba(251,113,133,0.10)", line_width=0
        )
        _note(
            figure,
            f"gözlenen eşikler<br>×{min(onsets):.2f} – ×{max(onsets):.2f}",
            min(onsets),
            1.0,
        )
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
    _layout(figure, 380, title=f"{len(findings['thresholds'])} farklı sürü, tek eksen")
    _ratio_axis(figure, multipliers)
    return figure


def ordering_figure(findings: Mapping[str, object]):
    """Dumbbell: Perron-ordered quarantine against the same defense in random order."""
    import plotly.graph_objects as go

    rows = list(findings["ordering"])[::-1]
    labels = [row["label"] for row in rows]
    figure = go.Figure()
    for row in rows:
        figure.add_scatter(
            x=[row["shield"]["mean"], row["control"]["mean"]],
            y=[row["label"], row["label"]],
            mode="lines",
            line={"color": "rgba(147,169,173,0.5)", "width": 3},
            hoverinfo="skip",
            showlegend=False,
        )
    series = (
        ("control", "Rastgele sıra (kontrol)", ORANGE, "diamond"),
        ("shield", "Perron sırası (Spektral Kalkan)", MINT, "circle"),
    )
    for key, name, color, symbol in series:
        figure.add_scatter(
            x=[row[key]["mean"] for row in rows],
            y=labels,
            mode="markers",
            name=name,
            marker={"color": color, "size": 14, "symbol": symbol, "line": RING},
            customdata=[[row[key]["ci95_low"], row[key]["ci95_high"]] for row in rows],
            hovertemplate=(
                f"{name}<br>ortalama %{{x:.1%}}"
                "<br>%95 GA %{customdata[0]:.1%} – %{customdata[1]:.1%}<extra></extra>"
            ),
        )
    for row in rows:
        same = row["wins"] == 0 and row["losses"] == 0
        difference = (
            f"Δ {row['delta']['mean'] * 100:+.1f} puan · {row['wins']}–{row['losses']} seed"
        )
        figure.add_annotation(
            x=1.0,
            xref="paper",
            y=row["label"],
            text="aynı sonuç" if same else difference,
            showarrow=False,
            xanchor="right",
            yshift=0,
            font={"color": INK, "size": 11},
        )
    _layout(
        figure,
        380,
        title="Aynı savunma, yalnızca karantina sırası farklı",
        legend=LEGEND_BELOW,
        margin={"l": 10, "r": 10, "t": 44, "b": 84},
    )
    figure.update_xaxes(
        title="Ortalama enfeksiyon oranı",
        tickformat=".0%",
        range=[-0.03, 1.18],
        tickvals=[0, 0.2, 0.4, 0.6, 0.8],
    )
    figure.update_yaxes(showgrid=False)
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
        subplot_titles=[table["label"] for table in tables],
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
                legendgroup=method,
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
                    f"<b>{METHOD_LABELS[method]}</b><br>enfeksiyon %{{x:.1%}}"
                    f"<br>en büyük bileşen %{{y:.1%}}<br>maliyet {row['cost']:.1f}<extra></extra>"
                ),
                row=1,
                col=column,
            )
    figure.add_annotation(
        x=0.0,
        xref="paper",
        y=0.0,
        yref="paper",
        text="↖ sol üst: hem güvenli hem bağlı",
        showarrow=False,
        font={"color": MUTED, "size": 11},
        xanchor="left",
        yanchor="bottom",
        xshift=8,
        yshift=6,
    )
    _layout(figure, 440, legend=LEGEND_BELOW, margin={"l": 10, "r": 10, "t": 44, "b": 110})
    figure.update_annotations(font_size=12)
    figure.update_xaxes(title="Ortalama enfeksiyon oranı", tickformat=".0%", range=[-0.05, 1.0])
    figure.update_yaxes(tickformat=".0%")
    figure.update_yaxes(title="Ortalama en büyük bileşen", col=1)
    return figure


def tightness_figure(findings: Mapping[str, object]):
    """Observed onset over β* per scenario, ordered from the sparsest to the densest swarm."""
    import plotly.graph_objects as go

    items = [item for item in findings["thresholds"] if item["tightness"]]
    ordered = sorted(items, key=lambda item: -item["mean_spectral_radius"])
    labels = [
        f"{item['title'].split(' · ')[0]} · λ₁ {item['mean_spectral_radius']:.1f}"
        for item in ordered
    ]
    figure = go.Figure()
    figure.add_vrect(x0=0, x1=1, fillcolor=SAFE_FILL, line_width=0, layer="below")
    figure.add_vline(x=1, line={"color": AMBER, "width": 2})
    for label, item in zip(labels, ordered, strict=True):
        figure.add_scatter(
            x=[1, item["tightness"]],
            y=[label, label],
            mode="lines",
            line={"color": "rgba(147,169,173,0.5)", "width": 3},
            hoverinfo="skip",
            showlegend=False,
        )
    figure.add_scatter(
        x=[item["tightness"] for item in ordered],
        y=labels,
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
    figure.add_annotation(
        x=1,
        y=1.0,
        yref="paper",
        text="<b>β*</b>",
        showarrow=False,
        font={"color": AMBER, "size": 11},
        xanchor="left",
        xshift=5,
        yanchor="bottom",
    )
    figure.add_annotation(
        x=0.5,
        y=1.0,
        yref="paper",
        text="sönüm garantili",
        showarrow=False,
        font={"color": MINT, "size": 11},
        yanchor="bottom",
    )
    _layout(figure, 400, title="Yoğun sürülerde eşik daha keskin")
    upper = max(item["tightness"] for item in ordered)
    figure.update_xaxes(title="Gözlenen eşik / β*", range=[0, upper + 0.6], ticksuffix="×")
    figure.update_yaxes(showgrid=False)
    return figure
