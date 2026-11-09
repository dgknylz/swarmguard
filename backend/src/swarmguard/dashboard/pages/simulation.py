from __future__ import annotations

import random
from dataclasses import replace

from ...config import DefenseStrategy, SimulationConfig
from ...presets import PRESET_BY_SLUG, SCENARIO_PRESETS
from ..charts import duel_figure, infection_map_figure, summarize_run, timeseries_figure
from ..components.event_center import render_event_center
from ..components.node_inspector import render_node_inspector
from ..components.scenario_builder import DEFENSE_LABELS, render_scenario_builder
from ..components.theory_lab import undefended
from ..control_deck import render_control_deck
from ..performance import cached_simulation
from ..player import render_swarm_player
from ..simulation_session import reset_playback
from ..state import get_or_create

MODES = {"single": "🛰️ Tekli simülasyon", "duel": "⚔️ Düello · iki savunma yan yana"}


def activate_scenario(session_state, config: SimulationConfig) -> None:
    frames = cached_simulation(config)
    session_state["config"] = config
    session_state["frames"] = frames
    # Widgets that mirror the scenario are keyed by this version so they pick up the
    # new values instead of keeping the ones the user typed for the previous scenario.
    session_state["config_version"] = session_state.get("config_version", 0) + 1
    reset_playback(session_state, len(frames))


def _render_quick_lab(st, config: SimulationConfig, version: int, *, with_defense: bool) -> None:
    defense_key = f"quick-defense-{version}"

    def apply_defense() -> None:
        updated = replace(
            st.session_state["config"], defense_strategy=st.session_state[defense_key]
        )
        activate_scenario(st.session_state, updated)

    def reseed() -> None:
        current = st.session_state["config"]
        activate_scenario(st.session_state, replace(current, seed=random.randrange(2**31)))

    # β, γ and range live in the control deck: it redraws σ̄, β* and the phase plane while
    # a slider moves and reports the values once it is released.
    value = render_control_deck(config, cached_simulation(undefended(config)))
    if isinstance(value, dict) and value.get("nonce") != st.session_state.get("deck-nonce"):
        st.session_state["deck-nonce"] = value.get("nonce")
        try:
            updated = replace(
                config,
                beta=float(value["beta"]),
                gamma=float(value["gamma"]),
                communication_range=float(value["range"]),
            )
        except (KeyError, TypeError, ValueError):
            updated = config
        if updated != config:
            activate_scenario(st.session_state, updated)
            st.rerun()

    columns = st.columns([3, 1] if with_defense else [4, 1], vertical_alignment="bottom")
    if with_defense:
        strategies = list(DefenseStrategy)
        columns[0].selectbox(
            "Savunma",
            strategies,
            index=strategies.index(config.defense_strategy),
            format_func=DEFENSE_LABELS.get,
            key=defense_key,
            on_change=apply_defense,
        )
    else:
        columns[0].caption("Düelloda savunmalar aşağıdaki A ve B seçicilerinden belirlenir.")
    columns[-1].button(
        "🎲 Yeni sürü",
        on_click=reseed,
        width="stretch",
        help="Aynı parametrelerle yeni bir rastgele seed: farklı konumlar ve hareket.",
    )


def _render_single(st, config: SimulationConfig, frames) -> None:
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

    series_tab, map_tab, node_tab, events_tab = st.tabs(
        ["📈 Zaman serileri", "🔥 Enfeksiyon haritası", "🔎 Düğüm analizi", "🧾 Olay merkezi"]
    )
    with series_tab:
        st.plotly_chart(timeseries_figure(frames, config), width="stretch")
        st.caption(
            "Sarı eğri σ(t), sağ eksende. Kesikli çizginin altında kalan her adım, Teorem 2'deki "
            "üst sınırı küçültür."
        )
    with map_tab:
        st.plotly_chart(infection_map_figure(frames), width="stretch")
        st.caption(
            "Her satır bir İHA, her sütun bir zaman adımı: kırmızı enfekte, sarı karantinada. "
            "Satırlar ilk enfeksiyon anına göre sıralandığından salgının şelalesi yukarıdan aşağı okunur."
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


def _render_duel(st, config: SimulationConfig) -> None:
    strategies = list(DefenseStrategy)
    left, right = st.columns(2, gap="small")
    defense_a = left.selectbox(
        "A · savunma",
        strategies,
        index=strategies.index(DefenseStrategy.NONE),
        format_func=DEFENSE_LABELS.get,
        key="duel-a",
    )
    defense_b = right.selectbox(
        "B · savunma",
        strategies,
        index=strategies.index(DefenseStrategy.SPECTRAL_SHIELD),
        format_func=DEFENSE_LABELS.get,
        key="duel-b",
    )
    config_a = replace(config, defense_strategy=defense_a)
    config_b = replace(config, defense_strategy=defense_b)
    frames_a, frames_b = cached_simulation(config_a), cached_simulation(config_b)
    with left:
        render_swarm_player(st, frames_a, config_a, height=620, sync="duel", badge="A", leader=True)
    with right:
        render_swarm_player(st, frames_b, config_b, height=620, sync="duel", badge="B")
    st.caption(
        "Aynı seed: aynı hareket, aynı saldırı başlangıcı ve aynı rastgele sayılar; aradaki her "
        "fark yalnızca savunmadan gelir. Oynatıcılardan birini oynatmak, sarmak, 3B'ye veya bir "
        "matematik katmanına geçirmek ikisini birden yönetir."
    )

    a, b = summarize_run(frames_a, config_a), summarize_run(frames_b, config_b)
    columns = st.columns(4)
    columns[0].metric(
        "Tepe enfeksiyon · B",
        f"%{b.peak_infected * 100:.1f}",
        f"{(b.peak_infected - a.peak_infected) * 100:+.1f} puan (A'ya göre)",
        delta_color="inverse",
    )
    columns[1].metric(
        "Ortalama enfeksiyon · B",
        f"%{b.mean_infected * 100:.1f}",
        f"{(b.mean_infected - a.mean_infected) * 100:+.1f} puan",
        delta_color="inverse",
    )
    columns[2].metric(
        "Ortalama büyük bileşen · B",
        f"%{b.mean_component * 100:.1f}",
        f"{(b.mean_component - a.mean_component) * 100:+.1f} puan",
    )
    columns[3].metric(
        "σ̄ · B",
        f"{b.geometric_sigma:.3f}",
        f"{b.geometric_sigma - a.geometric_sigma:+.3f}",
        delta_color="inverse",
    )
    st.plotly_chart(
        duel_figure(
            [
                (f"A · {DEFENSE_LABELS[defense_a]}", frames_a, "#94a3b8"),
                (f"B · {DEFENSE_LABELS[defense_b]}", frames_b, "#5eead4"),
            ],
            config,
        ),
        width="stretch",
    )


def render_simulation_page() -> None:
    import streamlit as st

    default_config = SCENARIO_PRESETS[0].config
    config = get_or_create(st.session_state, "config", lambda: default_config)
    frames = get_or_create(st.session_state, "frames", lambda: cached_simulation(config))
    version = st.session_state.get("config_version", 0)

    mode = st.segmented_control(
        "Simülasyon modu",
        options=list(MODES),
        default="single",
        format_func=MODES.get,
        key="simulation-mode",
        label_visibility="collapsed",
        width="stretch",
    )
    preset_key = f"simulation-preset-{version}"

    def load_preset() -> None:
        slug = st.session_state.get(preset_key)
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
        key=preset_key,
        on_change=load_preset,
        width="stretch",
    )
    _render_quick_lab(st, config, version, with_defense=mode != "duel")

    with st.expander("⚙️ Bütün senaryo parametreleri", expanded=False):
        builder = render_scenario_builder(st, config, key_prefix=f"simulation-builder-{version}")
        if builder.submitted and builder.config is not None:
            activate_scenario(st.session_state, builder.config)
            config, frames = st.session_state["config"], st.session_state["frames"]

    if mode == "duel":
        _render_duel(st, config)
    else:
        _render_single(st, config, frames)
