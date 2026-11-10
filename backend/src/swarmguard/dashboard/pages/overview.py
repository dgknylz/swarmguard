from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ...config import SimulationConfig
from ...presets import SHOWCASE_CONFIG

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
class Finding:
    kicker: str
    headline: str
    body: str
    figure: str


def _percent(value: float) -> str:
    return f"%{value * 100:.1f}"


def build_findings(findings: Mapping[str, Any]) -> tuple[Finding, ...]:
    """Three headline sentences written from the shipped experiment data."""
    onsets = [float(item["tightness"]) for item in findings["thresholds"] if item["tightness"]]
    # The ordering settings run from the loosest (ample budget) to the tightest one.
    loose, tight = findings["ordering"][0], findings["ordering"][-1]
    tables = {
        item["key"]: {row["method"]: row for row in item["rows"]} for item in findings["tables"]
    }
    easy, hard = tables["perfect"], tables["constrained"]
    dense = min(findings["thresholds"], key=lambda item: item["tightness"] or float("inf"))
    rival = hard["centrality_quarantine"]
    return (
        Finding(
            "BULGU 1 · EŞİK DOĞRU YERDE",
            f"Salgın, teorik eşiğin ×{min(onsets):.1f}–×{max(onsets):.1f} katında başlıyor.",
            f"β < β* iken sönüm ispatlıdır ve {len(onsets)} farklı sürünün hiçbirinde bozulmuyor. "
            "β eşiğin katları olarak tarandığında bütün eğriler sıfırdan eşiğin sağında ayrılıyor; "
            f"sürü yoğunlaştıkça fark kapanıyor ({dense['node_count']} İHA'lık "
            f"{dense['title']} senaryosunda ×{dense['tightness']:.1f}).",
            "collapse",
        ),
        Finding(
            "BULGU 2 · SIRALAMANIN DEĞERİ",
            f"Bütçe daraldığında Perron sırası {tight['wins']}–{tight['losses']} öne geçiyor.",
            "Kontrol grubu Spektral Kalkan'ın aynısıdır, yalnızca karantina sırası rastgeledir. "
            + (
                "Bütçe bolken iki yöntem aynı sonucu verir; "
                if loose["wins"] == loose["losses"] == 0
                else "Bütçe bolken fark küçüktür; "
            )
            + "adım başına tek müdahale ve %50 tespitte ortalama enfeksiyon "
            f"{_percent(tight['control']['mean'])} yerine {_percent(tight['shield']['mean'])} olur "
            f"(eşleştirilmiş t testi, p = {tight['p_value']:.3f}).",
            "ordering",
        ),
        Finding(
            "BULGU 3 · GÜVENLİK VE BAĞLANTI BİRLİKTE",
            "Karantina yöntemleri içinde en bağlı ağ Spektral Kalkan'da.",
            "Bağlantı ekleyen yöntemler (GTAD, rastgele ekleme) yayılımı düşürmüyor; karantina "
            "düşürüyor ama ağı parçalıyor. Spektral Kalkan kalan bütçeyle ağı onarır: kusursuz "
            f"tespitte merkeziyet karantinasıyla aynı enfeksiyonda "
            f"({_percent(easy['spectral_shield']['infection']['mean'])}) en büyük bileşen "
            f"{_percent(easy['centrality_quarantine']['connectivity']['mean'])} yerine "
            f"{_percent(easy['spectral_shield']['connectivity']['mean'])}; kısıtlı koşulda "
            f"{_percent(rival['connectivity']['mean'])} yerine "
            f"{_percent(hard['spectral_shield']['connectivity']['mean'])} "
            f"({rival['shield_connectivity']['wins']}–{rival['shield_connectivity']['losses']} seed).",
            "tradeoff",
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
        defense=config.defense_strategy.value.upper()
        if config is not None
        else SHOWCASE_CONFIG.defense_strategy.value.upper(),
    )


def showcase_config() -> SimulationConfig:
    """The landing animation runs the same scenario the simulation page opens with."""
    return SHOWCASE_CONFIG


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

    _render_findings(st)

    snapshot = get_home_snapshot(st.session_state)
    st.markdown("#### Oturum durumu")
    status = st.columns(4)
    status[0].metric("Durum", snapshot.status.title())
    status[1].metric("Son adım", snapshot.step)
    status[2].metric("Enfekte İHA", snapshot.infected)
    status[3].metric("En büyük bileşen", snapshot.connectivity)


def _render_findings(st) -> None:
    from ...findings import load_findings
    from ..components import findings_charts

    findings = load_findings()
    figures = {
        "collapse": findings_charts.threshold_collapse_figure,
        "ordering": findings_charts.ordering_figure,
        "tradeoff": findings_charts.tradeoff_figure,
    }
    first, last = findings["seeds"]
    st.markdown(
        f"""
        <div class="sg-findings-head">
            <span class="sg-th-kicker">DENEY BULGULARI</span>
            <div class="sg-th-title">Teoremler ne öngördü, simülasyon ne gösterdi?</div>
            <p>Seed {first}–{last}, eşleştirilmiş koşular. Bütün sayılar
            <code>python -m swarmguard.findings</code> komutuyla yeniden üretilir.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for index, finding in enumerate(build_findings(findings)):
        with st.container(border=True):
            if index % 2:
                chart, text = st.columns([1.5, 1], vertical_alignment="center", gap="large")
            else:
                text, chart = st.columns([1, 1.5], vertical_alignment="center", gap="large")
            text.markdown(
                f"""
                <div class="sg-finding">
                    <span class="sg-card-title">{finding.kicker}</span>
                    <h3>{finding.headline}</h3>
                    <p>{finding.body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            chart.plotly_chart(
                figures[finding.figure](findings),
                width="stretch",
                key=f"finding-{finding.figure}",
                config={"displayModeBar": False},
            )
