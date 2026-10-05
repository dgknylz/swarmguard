from __future__ import annotations

from dataclasses import dataclass

from ...experiments import RESULT_METRICS
from ..error_states import render_empty_state
from .experiment_center import EXPERIMENT_LABELS, METHOD_LABELS, METRIC_LABELS

LOWER_IS_BETTER = {
    "final_infected_ratio",
    "peak_infected_ratio",
    "mean_infected_ratio",
    "total_intervention_cost",
}


@dataclass(frozen=True, slots=True)
class ComparisonRow:
    rank: int
    method: str
    label: str
    mean: float
    ci95_low: float
    ci95_high: float
    paired_delta: float | None
    is_baseline: bool


def baseline_method(result: dict[str, object]) -> str:
    methods = {str(summary["method"]) for summary in result["summaries"]}
    preferred = "none" if result["kind"] == "monte_carlo" else "full"
    return preferred if preferred in methods else str(result["summaries"][0]["method"])


def build_comparison_rows(result: dict[str, object], metric: str) -> tuple[ComparisonRow, ...]:
    baseline = baseline_method(result)
    deltas = {
        str(comparison["method"]): float(comparison["mean_deltas"][metric])
        for comparison in result["paired_comparisons"]
        if metric in comparison["mean_deltas"]
    }
    values = []
    for summary in result["summaries"]:
        method = str(summary["method"])
        statistics = summary["metrics"][metric]
        values.append(
            {
                "method": method,
                "mean": float(statistics["mean"]),
                "ci95_low": float(statistics["ci95_low"]),
                "ci95_high": float(statistics["ci95_high"]),
                "paired_delta": 0.0 if method == baseline else deltas.get(method),
            }
        )
    values.sort(key=lambda row: row["mean"], reverse=metric not in LOWER_IS_BETTER)
    return tuple(
        ComparisonRow(
            rank=index,
            method=str(row["method"]),
            label=METHOD_LABELS.get(str(row["method"]), str(row["method"])),
            mean=float(row["mean"]),
            ci95_low=float(row["ci95_low"]),
            ci95_high=float(row["ci95_high"]),
            paired_delta=(float(row["paired_delta"]) if row["paired_delta"] is not None else None),
            is_baseline=row["method"] == baseline,
        )
        for index, row in enumerate(values, start=1)
    )


def build_normalized_scorecard(result: dict[str, object]) -> list[dict[str, object]]:
    summaries = result["summaries"]
    ranges: dict[str, tuple[float, float]] = {}
    for metric in RESULT_METRICS:
        values = [float(summary["metrics"][metric]["mean"]) for summary in summaries]
        ranges[metric] = (min(values), max(values))

    rows = []
    for summary in summaries:
        method = str(summary["method"])
        scores: dict[str, float] = {}
        for metric in RESULT_METRICS:
            value = float(summary["metrics"][metric]["mean"])
            low, high = ranges[metric]
            normalized = 0.5 if high == low else (value - low) / (high - low)
            scores[metric] = 1 - normalized if metric in LOWER_IS_BETTER else normalized
        rows.append(
            {
                "method": method,
                "label": METHOD_LABELS.get(method, method),
                "scores": scores,
                "overall": sum(scores.values()) / len(scores),
            }
        )
    return sorted(rows, key=lambda row: float(row["overall"]), reverse=True)


def _render_empty(st) -> None:
    render_empty_state(
        st,
        icon="⇄",
        title="Karşılaştırılacak deney bulunamadı",
        message="Önce Deney Merkezi'nden bir Monte Carlo veya GTAD ablation deneyi çalıştır.",
        action_label="Deney Merkezi'ne git",
        action_href="experiments",
    )


def render_comparison_panel(st, history: list[dict[str, object]]) -> None:
    import pandas as pd
    import plotly.graph_objects as go

    st.markdown(
        """
        <section class="sg-comparison-hero">
            <div><span>KARŞILAŞTIRMA EKRANI</span><h2>Yöntemleri aynı kanıt düzleminde karşılaştır.</h2></div>
            <p>Sıralama, eşleştirilmiş seed farkları ve çok metrikli skor kartı; yöntemlerin güvenlik, bağlantısallık ve maliyet dengesini birlikte gösterir.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if not history:
        _render_empty(st)
        return

    control_left, control_right = st.columns([1.35, 1])
    ids = [str(result["experiment_id"]) for result in history]
    selected_id = control_left.selectbox(
        "Karşılaştırılacak deney",
        options=ids,
        format_func=lambda experiment_id: next(
            f"{EXPERIMENT_LABELS[str(item['kind'])]} · {item['run_count']} koşu · {experiment_id}"
            for item in history
            if item["experiment_id"] == experiment_id
        ),
        key="comparison-experiment",
    )
    metric = control_right.selectbox(
        "Birincil başarı metriği",
        options=RESULT_METRICS,
        index=2,
        format_func=lambda value: METRIC_LABELS[value],
        key="comparison-metric",
    )
    result = next(item for item in history if str(item["experiment_id"]) == selected_id)
    rows = build_comparison_rows(result, metric)
    scorecard = build_normalized_scorecard(result)
    baseline = baseline_method(result)
    best = rows[0]

    metric_columns = st.columns(4)
    metric_columns[0].metric("En iyi yöntem", best.label)
    metric_columns[1].metric("En iyi ortalama", f"{best.mean:.4f}")
    metric_columns[2].metric("Karşılaştırılan yöntem", len(rows))
    metric_columns[3].metric("Eşleştirilmiş seed", len(result["seeds"]))

    chart_column, ranking_column = st.columns([1.55, 1], vertical_alignment="top")
    with chart_column:
        st.markdown("##### Ortalama ve %95 güven aralığı")
        figure = go.Figure()
        figure.add_bar(
            x=[row.label for row in rows],
            y=[row.mean for row in rows],
            marker_color=["#57e7d6" if row.rank == 1 else "#315b61" for row in rows],
            error_y={
                "type": "data",
                "symmetric": False,
                "array": [row.ci95_high - row.mean for row in rows],
                "arrayminus": [row.mean - row.ci95_low for row in rows],
                "color": "#a6dcd5",
            },
            hovertemplate="%{x}<br>Ortalama: %{y:.4f}<extra></extra>",
        )
        figure.update_layout(
            height=390,
            margin={"l": 10, "r": 10, "t": 20, "b": 10},
            paper_bgcolor="#08151a",
            plot_bgcolor="#08151a",
            font={"color": "#789097"},
            yaxis={"gridcolor": "rgba(148,197,202,0.09)", "title": METRIC_LABELS[metric]},
            showlegend=False,
        )
        st.plotly_chart(figure, width="stretch", key=f"comparison-primary-{selected_id}")

    with ranking_column:
        st.markdown("##### Yöntem sıralaması")
        ranking_rows = [
            {
                "sıra": row.rank,
                "yöntem": row.label,
                "ortalama": row.mean,
                "baseline farkı": row.paired_delta,
                "referans": "Baseline" if row.is_baseline else "",
            }
            for row in rows
        ]
        st.dataframe(ranking_rows, width="stretch", hide_index=True, height=390)

    st.markdown("##### Çok metrikli performans matrisi")
    heatmap = go.Figure(
        data=go.Heatmap(
            z=[[row["scores"][metric_name] for metric_name in RESULT_METRICS] for row in scorecard],
            x=[METRIC_LABELS[metric_name] for metric_name in RESULT_METRICS],
            y=[str(row["label"]) for row in scorecard],
            zmin=0,
            zmax=1,
            colorscale=[[0, "#12262c"], [0.5, "#2b7777"], [1, "#57e7d6"]],
            colorbar={"title": "Başarı", "tickformat": ".0%"},
            hovertemplate="%{y}<br>%{x}<br>Normalize başarı: %{z:.1%}<extra></extra>",
        )
    )
    heatmap.update_layout(
        height=max(300, 90 + len(scorecard) * 58),
        margin={"l": 10, "r": 10, "t": 20, "b": 80},
        paper_bgcolor="#08151a",
        plot_bgcolor="#08151a",
        font={"color": "#789097"},
    )
    st.plotly_chart(heatmap, width="stretch", key=f"comparison-heatmap-{selected_id}")
    st.caption(
        "Her sütun kendi yöntem aralığında 0–1 ölçeğine normalize edilir; yüksek değer daha iyi sonucu "
        "gösterir. Genel skor, yedi metriğin eşit ağırlıklı ortalamasıdır."
    )

    seed_column, delta_column = st.columns([1.4, 1], vertical_alignment="top")
    with seed_column:
        st.markdown("##### Seed bazlı sonuçlar")
        run_rows = [
            {
                "seed": int(run["seed"]),
                "yöntem": METHOD_LABELS.get(str(run["method"]), str(run["method"])),
                "değer": float(run[metric]),
            }
            for run in result["runs"]
        ]
        st.line_chart(pd.DataFrame(run_rows), x="seed", y="değer", color="yöntem", height=320)

    with delta_column:
        st.markdown("##### Baseline etkisi")
        st.caption(f"Referans yöntem: {METHOD_LABELS.get(baseline, baseline)}")
        delta_rows = [
            {
                "yöntem": row.label,
                "eşleştirilmiş ortalama fark": row.paired_delta,
                "yorum": (
                    "Referans"
                    if row.is_baseline
                    else (
                        "İyileşme"
                        if row.paired_delta is not None
                        and ((row.paired_delta < 0) == (metric in LOWER_IS_BETTER))
                        else "Gerileme"
                    )
                ),
            }
            for row in rows
        ]
        st.dataframe(delta_rows, width="stretch", hide_index=True, height=320)
