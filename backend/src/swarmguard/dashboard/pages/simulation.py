from __future__ import annotations

from ...presets import SCENARIO_PRESETS
from ..charts import frames_to_records
from ..components.event_center import render_event_center
from ..components.live_lab import render_live_lab
from ..components.scenario_builder import render_preset_library, render_scenario_builder
from ..performance import cached_simulation
from ..simulation_session import reset_playback
from ..state import get_or_create


def render_simulation_page() -> None:
    import pandas as pd
    import streamlit as st

    view = st.segmented_control(
        "Simülasyon bölümü",
        options=("live", "settings", "analysis"),
        default="live",
        format_func={
            "live": "📡 Canlı Ağ",
            "settings": "⚙️ Senaryo Ayarları",
            "analysis": "📊 Analiz ve Olaylar",
        }.get,
        key="simulation-view",
        label_visibility="collapsed",
        width="stretch",
    )
    default_config = SCENARIO_PRESETS[0].config
    config = get_or_create(st.session_state, "config", lambda: default_config)
    frames = get_or_create(st.session_state, "frames", lambda: cached_simulation(config))

    if view == "settings":
        st.subheader("Simülasyon senaryosu")
        st.caption(
            "Sürü, fiziksel alan, SIS saldırı modeli ve savunma kısıtlarını "
            "tek bir doğrulanabilir deney tanımında birleştir."
        )
        preset = render_preset_library(st, SCENARIO_PRESETS)
        base = preset.config if preset is not None else config
        builder = render_scenario_builder(
            st,
            base,
            key_prefix=f"preset-{preset.slug}" if preset is not None else "custom-scenario",
        )

        if builder.submitted and builder.config is not None:
            config = builder.config
            frames = cached_simulation(config)
            st.session_state.frames = frames
            st.session_state.config = config
            reset_playback(st.session_state, len(frames), autoplay=True)

    elif view == "live":
        render_live_lab(st, frames)

    else:
        records = pd.DataFrame(frames_to_records(frames))
        st.subheader("Bilimsel zaman serileri")
        st.caption("Enfeksiyon ve bağlantısallık metriklerini aynı deney ekseninde karşılaştır.")
        st.line_chart(
            records,
            x="step",
            y=["infected_ratio", "largest_component_ratio", "global_efficiency"],
        )
        render_event_center(st, frames)
