from __future__ import annotations

from dataclasses import dataclass

from ...config import DefenseStrategy, SimulationConfig
from ...experiment_exports import manifest_to_json, runs_to_csv, runs_to_parquet
from ...experiments import RESULT_METRICS
from ..performance import cached_gtad_ablation, cached_monte_carlo

EXPERIMENT_LABELS = {
    "monte_carlo": "Monte Carlo",
    "gtad_ablation": "GTAD Ablation",
}

METHOD_LABELS = {
    "none": "Savunmasız",
    "random_rewiring": "Rastgele yeniden bağlantı",
    "centrality_quarantine": "Merkeziyet karantinası",
    "gtad_risk": "GTAD Risk",
    "full": "Tam GTAD",
    "without_connectivity": "Bağlantısallık yok",
    "without_safety": "Güvenlik yok",
    "without_distance": "Mesafe yok",
}

METRIC_LABELS = {
    "final_infected_ratio": "Son enfeksiyon oranı",
    "peak_infected_ratio": "Tepe enfeksiyon oranı",
    "mean_infected_ratio": "Ortalama enfeksiyon oranı",
    "mean_largest_component_ratio": "Ortalama büyük bileşen",
    "mean_global_efficiency": "Ortalama ağ verimliliği",
    "mean_algebraic_connectivity": "Ortalama λ₂",
    "total_intervention_cost": "Toplam müdahale maliyeti",
}


@dataclass(frozen=True, slots=True)
class ExperimentPlan:
    kind: str
    methods: tuple[str, ...]
    seeds: tuple[int, ...]
    run_count: int
    simulated_steps: int


def parse_seeds(raw: str, *, maximum: int = 30) -> tuple[int, ...]:
    tokens = [token.strip() for token in raw.replace(";", ",").split(",") if token.strip()]
    if not tokens:
        raise ValueError("En az bir seed girilmelidir.")
    try:
        seeds = tuple(int(token) for token in tokens)
    except ValueError as exc:
        raise ValueError("Seed değerleri virgülle ayrılmış tam sayılar olmalıdır.") from exc
    if any(seed < 0 for seed in seeds):
        raise ValueError("Seed değerleri negatif olamaz.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seed değerleri benzersiz olmalıdır.")
    if len(seeds) > maximum:
        raise ValueError(f"Tek deneyde en fazla {maximum} seed kullanılabilir.")
    return seeds


def build_experiment_plan(
    kind: str,
    strategies: tuple[DefenseStrategy, ...],
    seeds: tuple[int, ...],
    steps: int,
) -> ExperimentPlan:
    methods = (
        ("full", "without_connectivity", "without_safety", "without_distance")
        if kind == "gtad_ablation"
        else tuple(strategy.value for strategy in strategies)
    )
    if not methods:
        raise ValueError("En az bir savunma yöntemi seçilmelidir.")
    return ExperimentPlan(
        kind=kind,
        methods=methods,
        seeds=seeds,
        run_count=len(methods) * len(seeds),
        simulated_steps=len(methods) * len(seeds) * steps,
    )


def summary_rows(result: dict[str, object], metric: str) -> list[dict[str, object]]:
    return [
        {
            "method": str(summary["method"]),
            "method_label": METHOD_LABELS.get(str(summary["method"]), str(summary["method"])),
            "run_count": int(summary["run_count"]),
            "mean": float(summary["metrics"][metric]["mean"]),
            "std": float(summary["metrics"][metric]["std"]),
            "ci95_low": float(summary["metrics"][metric]["ci95_low"]),
            "ci95_high": float(summary["metrics"][metric]["ci95_high"]),
        }
        for summary in result["summaries"]
    ]


def _render_plan(st, config: SimulationConfig, plan: ExperimentPlan | None) -> None:
    st.markdown("##### Çalışma planı")
    if plan is None:
        st.caption("Geçerli seed ve yöntem seçimi yapıldığında koşu planı burada görünecek.")
        return
    method_chips = "".join(
        f"<span>{METHOD_LABELS.get(method, method)}</span>" for method in plan.methods
    )
    st.markdown(
        f"""
        <section class="sg-experiment-plan">
            <div><small>DENEY TÜRÜ</small><strong>{EXPERIMENT_LABELS[plan.kind]}</strong></div>
            <div><small>TOPLAM KOŞU</small><strong>{plan.run_count}</strong></div>
            <div><small>SİMÜLE ADIM</small><strong>{plan.simulated_steps:,}</strong></div>
            <div><small>SENARYO</small><strong>{config.node_count} İHA · {config.steps} adım</strong></div>
            <article>{method_chips}</article>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        f"Seed kümesi: {', '.join(map(str, plan.seeds))} · "
        "Her yöntem aynı seed kümesiyle eşleştirilir."
    )


def _render_result(st, result: dict[str, object]) -> None:
    import pandas as pd
    import plotly.graph_objects as go

    experiment_id = str(result["experiment_id"])
    fingerprint = str(result["manifest"]["fingerprint"])
    st.markdown(
        f"""
        <section class="sg-result-banner">
            <div><span>DENEY TAMAMLANDI</span><h3>{EXPERIMENT_LABELS[str(result["kind"])]}</h3></div>
            <div><small>DENEY KİMLİĞİ</small><strong>{experiment_id}</strong></div>
            <div><small>KOŞU</small><strong>{result["run_count"]}</strong></div>
            <div><small>PARMAK İZİ</small><strong>{fingerprint[7:19]}…</strong></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    metric = st.selectbox(
        "Sonuç metriği",
        RESULT_METRICS,
        index=2,
        format_func=lambda value: METRIC_LABELS[value],
        key=f"experiment-metric-{experiment_id}",
    )
    rows = summary_rows(result, metric)
    figure = go.Figure()
    figure.add_bar(
        x=[row["method_label"] for row in rows],
        y=[row["mean"] for row in rows],
        error_y={
            "type": "data",
            "symmetric": False,
            "array": [row["ci95_high"] - row["mean"] for row in rows],
            "arrayminus": [row["mean"] - row["ci95_low"] for row in rows],
            "color": "#9aeee4",
        },
        marker_color="#57e7d6",
        hovertemplate="%{x}<br>Ortalama: %{y:.4f}<extra></extra>",
    )
    figure.update_layout(
        height=360,
        margin={"l": 10, "r": 10, "t": 25, "b": 10},
        paper_bgcolor="#08151a",
        plot_bgcolor="#08151a",
        font={"color": "#789097"},
        yaxis={"gridcolor": "rgba(148,197,202,0.09)", "title": METRIC_LABELS[metric]},
        xaxis={"gridcolor": "rgba(148,197,202,0.05)"},
        showlegend=False,
    )
    st.plotly_chart(figure, width="stretch", key=f"experiment-chart-{experiment_id}")

    st.dataframe(
        pd.DataFrame(rows).rename(
            columns={
                "method_label": "yöntem",
                "run_count": "koşu",
                "mean": "ortalama",
                "std": "std. sapma",
                "ci95_low": "%95 GA alt",
                "ci95_high": "%95 GA üst",
            }
        )[["yöntem", "koşu", "ortalama", "std. sapma", "%95 GA alt", "%95 GA üst"]],
        width="stretch",
        hide_index=True,
    )

    csv_column, parquet_column, manifest_column, note_column = st.columns(
        [1, 1, 1, 2], vertical_alignment="center"
    )
    csv_column.download_button(
        "CSV indir",
        runs_to_csv(result),
        file_name=f"swarmguard-{experiment_id}-runs.csv",
        mime="text/csv",
        width="stretch",
    )
    parquet_column.download_button(
        "Parquet indir",
        runs_to_parquet(result),
        file_name=f"swarmguard-{experiment_id}-runs.parquet",
        mime="application/vnd.apache.parquet",
        width="stretch",
    )
    manifest_column.download_button(
        "Manifest indir",
        manifest_to_json(result),
        file_name=f"swarmguard-{experiment_id}-manifest.json",
        mime="application/json",
        width="stretch",
    )
    note_column.caption("Grafikteki hata çubukları iki taraflı %95 Student-t güven aralığıdır.")

    with st.expander("Ham koşu kayıtları"):
        st.dataframe(result["runs"], width="stretch", hide_index=True)


def render_experiment_center(st, config: SimulationConfig) -> None:
    st.markdown(
        """
        <section class="sg-experiment-hero">
            <div><span>DENEY MERKEZİ</span><h2>Savunmayı tek koşuyla değil, kanıtla.</h2></div>
            <p>Yöntemleri eşleştirilmiş seed kümeleriyle çalıştır; ortalama, dağılım ve %95 güven aralıklarını tekrarlanabilir bir deney manifestiyle üret.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    form_column, plan_column = st.columns([1.15, 0.85], vertical_alignment="top")
    with form_column:
        with st.form("experiment-designer"):
            st.markdown("##### Deney tasarımı")
            kind = st.radio(
                "Deney türü",
                options=("monte_carlo", "gtad_ablation"),
                format_func=lambda value: EXPERIMENT_LABELS[value],
                horizontal=True,
            )
            strategies = st.multiselect(
                "Savunma yöntemleri",
                options=list(DefenseStrategy),
                default=[DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK],
                format_func=lambda value: METHOD_LABELS[value.value],
                disabled=kind == "gtad_ablation",
            )
            seed_text = st.text_input(
                "Seed kümesi",
                value="11, 23, 37, 53, 71",
                help="Virgülle ayrılmış, benzersiz ve negatif olmayan tam sayılar.",
            )
            submitted = st.form_submit_button("Deneyi çalıştır", type="primary", width="stretch")

        try:
            seeds = parse_seeds(seed_text)
            plan = build_experiment_plan(kind, tuple(strategies), seeds, config.steps)
            plan_error = None
        except ValueError as exc:
            plan = None
            plan_error = str(exc)

    with plan_column:
        _render_plan(st, config, plan)
        if plan_error:
            st.error(plan_error)
        st.info(
            "Aktif Simülasyon sayfasındaki senaryo temel alınır. Deneyler bu senaryonun "
            "seed ve savunma yöntemini kontrollü biçimde değiştirir."
        )

    if submitted:
        if plan is None:
            st.error(plan_error)
        else:
            with st.spinner(f"{plan.run_count} koşu yürütülüyor…"):
                if plan.kind == "gtad_ablation":
                    result = cached_gtad_ablation(config, plan.seeds)
                else:
                    result = cached_monte_carlo(config, tuple(strategies), plan.seeds)
            history = st.session_state.setdefault("experiment_history", [])
            history = [item for item in history if item["experiment_id"] != result["experiment_id"]]
            history.insert(0, result)
            st.session_state["experiment_history"] = history[:8]
            st.session_state["active_experiment_id"] = result["experiment_id"]

    history = st.session_state.get("experiment_history", [])
    if not history:
        st.markdown(
            """
            <section class="sg-experiment-empty">
                <div>Δ</div><h3>İlk deneyini tasarla</h3>
                <p>Bir yöntem kümesi ve seed listesi seçtiğinde sonuçlar, güven aralıkları ve indirilebilir araştırma çıktıları burada oluşacak.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        return

    ids = [str(result["experiment_id"]) for result in history]
    active_id = st.selectbox(
        "Deney geçmişi",
        options=ids,
        index=ids.index(st.session_state.get("active_experiment_id", ids[0]))
        if st.session_state.get("active_experiment_id", ids[0]) in ids
        else 0,
        format_func=lambda experiment_id: next(
            f"{EXPERIMENT_LABELS[str(item['kind'])]} · {item['run_count']} koşu · {experiment_id}"
            for item in history
            if item["experiment_id"] == experiment_id
        ),
    )
    st.session_state["active_experiment_id"] = active_id
    active_result = next(item for item in history if item["experiment_id"] == active_id)
    _render_result(st, active_result)
