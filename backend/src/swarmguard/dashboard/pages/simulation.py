from __future__ import annotations

from ...config import SimulationConfig
from ...presets import PRESET_BY_SLUG, SCENARIO_PRESETS
from ..charts import summarize_run, timeseries_figure
from ..components.event_center import render_event_center
from ..components.node_inspector import render_node_inspector
from ..components.scenario_builder import render_scenario_builder
from ..performance import cached_simulation
from ..player import render_swarm_player
from ..simulation_session import reset_playback
from ..state import get_or_create


def activate_scenario(session_state, config: SimulationConfig) -> None:
    frames = cached_simulation(config)
    session_state["config"] = config
    session_state["frames"] = frames
    reset_playback(session_state, len(frames))


def render_simulation_page() -> None:
    import streamlit as st

    default_config = SCENARIO_PRESETS[0].config
    config = get_or_create(st.session_state, "config", lambda: default_config)
    frames = get_or_create(st.session_state, "frames", lambda: cached_simulation(config))

    def load_preset() -> None:
        slug = st.session_state.get("simulation-preset")
        if slug in PRESET_BY_SLUG:
            activate_scenario(st.session_state, PRESET_BY_SLUG[slug].config)

    active_slug = next(
        (preset.slug for preset in SCENARIO_PRESETS if preset.config == config), None
    )
    st.pills(
        "Hazır senaryolar · seç ve anında çalıştır",
        [preset.slug for preset in SCENARIO_PRESETS],
        default=active_slug,
        format_func=lambda slug: f"{PRESET_BY_SLUG[slug].icon} {PRESET_BY_SLUG[slug].title}",
        key="simulation-preset",
        on_change=load_preset,
        width="stretch",
    )

    with st.expander("⚙️ Senaryo parametrelerini düzenle", expanded=False):
        builder = render_scenario_builder(st, config, key_prefix="simulation-builder")
        if builder.submitted and builder.config is not None:
            activate_scenario(st.session_state, builder.config)
            config, frames = st.session_state["config"], st.session_state["frames"]

    render_swarm_player(st, frames, config, height=700)

    summary = summarize_run(frames, config)
    columns = st.columns(5)
    columns[0].metric("Tepe enfeksiyon", f"%{summary.peak_infected * 100:.1f}")
    columns[1].metric("Son enfeksiyon", f"%{summary.final_infected * 100:.1f}")
    columns[2].metric("Ortalama büyük bileşen", f"%{summary.mean_component * 100:.1f}")
    columns[3].metric(
        "Geometrik ortalama σ̄",
        f"{summary.geometric_sigma:.3f}",
        "sönüm garantili" if summary.geometric_sigma < 1 else "eşik üstü",
        delta_color="normal" if summary.geometric_sigma < 1 else "inverse",
        help="Teorem 2: σ(t) = 1 − γ + β·λ₁(A(t)) çarpanlarının geometrik ortalaması 1'in "
        "altındaysa beklenen enfekte sayısı üstel hızla sıfıra iner.",
    )
    columns[4].metric("Müdahale maliyeti", f"{summary.intervention_cost:.0f}")

    series_tab, node_tab, events_tab = st.tabs(
        ["📈 Zaman serileri", "🔎 Düğüm analizi", "🧾 Olay merkezi"]
    )
    with series_tab:
        st.plotly_chart(timeseries_figure(frames, config), width="stretch")
        st.caption(
            "Sarı eğri σ(t), sağ eksende. Kesikli çizginin altında kalan her adım, Teorem 2'deki "
            "üst sınırı küçültür."
        )
    with node_tab:
        node_column, step_column = st.columns([1, 2.4], vertical_alignment="bottom")
        node = node_column.selectbox(
            "İHA incele",
            options=range(len(frames[0].positions)),
            format_func=lambda value: f"UAV-{value:02d}",
            key="node_picker",
        )
        step = step_column.slider(
            "Analiz karesi", 0, len(frames) - 1, len(frames) - 1, key="analysis_step"
        )
        st.session_state["selected_uav"] = int(node)
        render_node_inspector(st, frames, int(step), int(node))
    with events_tab:
        render_event_center(st, frames)
