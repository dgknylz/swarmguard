from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from ...config import DefenseStrategy, SimulationConfig
from ...presets import DEMO_CONFIG

THEOREM_CARDS = (
    (
        "TEOREM 1",
        "Bağlantı olasılığı",
        r"F(r)=\dfrac{\pi WHr^2-\frac43(W+H)r^3+\frac12r^4}{W^2H^2}",
        "Görev alanının sınırları dahil kesin beklenen derece.",
    ),
    (
        "TEOREM 2",
        "Spektral üst sınır",
        r"\mathbb E[I(t)]\le\sqrt{nI_0}\,\prod_{s\le t}\sigma(s)",
        "σ̄ < 1 ise salgın üstel hızla söner.",
    ),
    (
        "ÖNERME 3",
        "Bulaş sınırı",
        r"\mathbb E[\Delta I^+\mid X]\le\beta\,|\partial I|",
        "Kesilmesi gereken nicelik: sağlıklı–enfekte kenarları.",
    ),
    (
        "LEMMA 4",
        "Rayleigh pertürbasyonu",
        r"\lambda_1(A_{-i})\ge\lambda_1(1-2u_i^2)",
        "Spektral Kalkan savunmasının matematiksel temeli.",
    ),
)


@dataclass(frozen=True)
class HomeSnapshot:
    status: str
    step: str
    infected: str
    connectivity: str
    defense: str


def get_home_snapshot(session_state: Mapping[str, Any]) -> HomeSnapshot:
    config = session_state.get("config")
    frames = session_state.get("frames") or []
    frame = frames[-1] if frames else None
    metrics = frame.metrics if frame is not None else {}
    connectivity = metrics.get("largest_component_ratio")

    return HomeSnapshot(
        status="SON KOŞU HAZIR" if frame is not None else "PLATFORM HAZIR",
        step=str(frame.step) if frame is not None else "—",
        infected=str(metrics.get("infected_count", "—")),
        connectivity=f"%{float(connectivity) * 100:.1f}" if connectivity is not None else "—",
        defense=config.defense_strategy.value.upper() if config is not None else "GTAD",
    )


def showcase_config() -> SimulationConfig:
    """The landing animation runs the spectral defense on the demo swarm."""
    return replace(DEMO_CONFIG, defense_strategy=DefenseStrategy.SPECTRAL_SHIELD)


def render_overview_page() -> None:
    import streamlit as st

    from ..performance import cached_simulation
    from ..player import render_swarm_player

    hero_text, hero_visual = st.columns([1, 1.15], vertical_alignment="center", gap="large")
    with hero_text:
        st.markdown(
            """
            <section class="sg-landing">
                <span class="sg-kicker">◈ SWARMGUARD · TÜBİTAK 2204 MATEMATİK</span>
                <h1>Dinamik İHA ağlarını <em>spektral teoriyle</em> savun.</h1>
                <p>Hareket eden bir İHA sürüsünde siber saldırının nasıl yayıldığını modelliyor,
                yayılımın büyüklüğünü komşuluk matrisinin en büyük özdeğeriyle sınırlıyor ve bu
                teoremden türetilen savunmayı simülasyonla sınıyoruz.</p>
                <div class="sg-equation">σ(t) = 1 − γ + β · λ₁(A(t))
                    <small>Projenin anahtar denklemi: geometrik ortalaması 1'in altındaysa salgın söner.</small>
                </div>
                <div class="sg-hero-actions">
                    <a class="sg-button sg-button-primary" href="simulation" target="_self">Simülasyonu aç <span>→</span></a>
                    <a class="sg-button sg-button-secondary" href="theory" target="_self">Teoremleri incele</a>
                    <a class="sg-button sg-button-secondary" href="experiments" target="_self">Deney çalıştır</a>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with hero_visual:
        config = showcase_config()
        render_swarm_player(
            st,
            cached_simulation(config),
            config,
            height=460,
            compact=True,
            autoplay=True,
            view="3d",
        )

    st.markdown("#### Matematiksel omurga")
    for column, (label, title, formula, caption) in zip(st.columns(4), THEOREM_CARDS, strict=True):
        with column.container(border=True):
            st.markdown(f'<span class="sg-card-title">{label}</span>', unsafe_allow_html=True)
            st.markdown(f"**{title}**")
            st.latex(formula)
            st.caption(caption)

    snapshot = get_home_snapshot(st.session_state)
    st.markdown("#### Oturum durumu")
    status = st.columns(4)
    status[0].metric("Durum", snapshot.status.title())
    status[1].metric("Son adım", snapshot.step)
    status[2].metric("Enfekte İHA", snapshot.infected)
    status[3].metric("En büyük bileşen", snapshot.connectivity)
