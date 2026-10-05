from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


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


def render_overview_page() -> None:
    import streamlit as st

    snapshot = get_home_snapshot(st.session_state)
    st.markdown(
        f"""
        <section class="sg-hero">
            <div class="sg-hero-copy">
                <div class="sg-hero-kicker"><span></span> OTONOM SÜRÜ SAVUNMA ARAŞTIRMA PLATFORMU</div>
                <h2>Dinamik İHA ağlarını<br><em>saldırıya karşı dayanıklı</em> tasarla.</h2>
                <p>Saldırı yayılımını modelle, adaptif topoloji savunmalarını çalıştır ve bilimsel sonuçları aynı tekrarlanabilir deney ortamında karşılaştır.</p>
                <div class="sg-hero-actions">
                    <a class="sg-button sg-button-primary" href="simulation" target="_self">Simülasyonu aç <span>→</span></a>
                    <a class="sg-button sg-button-secondary" href="methodology" target="_self">Metodolojiyi incele</a>
                </div>
                <div class="sg-hero-proof">
                    <div><strong>04</strong><span>Savunma yaklaşımı</span></div>
                    <div><strong>04</strong><span>Bilimsel ağ metriği</span></div>
                    <div><strong>100%</strong><span>Seed tekrarlanabilirliği</span></div>
                </div>
            </div>
            <div class="sg-hero-visual" aria-label="Sürü ağı görselleştirmesi">
                <div class="sg-radar-ring sg-ring-one"></div>
                <div class="sg-radar-ring sg-ring-two"></div>
                <div class="sg-radar-ring sg-ring-three"></div>
                <div class="sg-network-line sg-line-one"></div>
                <div class="sg-network-line sg-line-two"></div>
                <div class="sg-network-line sg-line-three"></div>
                <span class="sg-network-node sg-node-one"></span>
                <span class="sg-network-node sg-node-two"></span>
                <span class="sg-network-node sg-node-three"></span>
                <span class="sg-network-node sg-node-four"></span>
                <span class="sg-network-node sg-node-five"></span>
                <div class="sg-radar-core">◈</div>
                <div class="sg-visual-status"><span class="sg-status-dot sg-status-online"></span>{snapshot.status}</div>
            </div>
        </section>

        <section class="sg-kpi-grid">
            <article><span>DOĞRULAMA</span><strong>111</strong><small>otomatik test</small></article>
            <article><span>SİMÜLASYON</span><strong>SIS</strong><small>senkron yayılım</small></article>
            <article><span>SAVUNMA</span><strong>{snapshot.defense}</strong><small>aktif yaklaşım</small></article>
            <article><span>YAYIN</span><strong>READY</strong><small>Streamlit Cloud</small></article>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sg-section-heading">
            <div><span>UÇTAN UCA İŞ AKIŞI</span><h3>Bir senaryodan bilimsel sonuca.</h3></div>
            <p>Parametreleri tanımla, dinamik ağı çalıştır ve savunma etkisini aynı deney tasarımında ölç.</p>
        </div>
        <section class="sg-process-grid">
            <article><b>01</b><div class="sg-process-icon">⊕</div><h4>Senaryoyu kur</h4><p>Sürü boyutu, hareket, haberleşme menzili, saldırı ve savunma parametrelerini belirle.</p></article>
            <article><b>02</b><div class="sg-process-icon">◎</div><h4>Ağı izle</h4><p>Enfeksiyon yayılımını, topoloji müdahalelerini ve kritik olayları zaman çizelgesinde takip et.</p></article>
            <article><b>03</b><div class="sg-process-icon">∿</div><h4>Sonucu kanıtla</h4><p>Monte Carlo koşuları, güven aralıkları ve eşleştirilmiş seed analiziyle yöntemleri karşılaştır.</p></article>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sg-section-heading sg-section-spaced">
            <div><span>PLATFORM MODÜLLERİ</span><h3>Araştırmanın her aşaması tek yerde.</h3></div>
        </div>
        <section class="sg-module-grid">
            <a href="simulation" target="_self"><span class="sg-module-index">01</span><div class="sg-module-icon">◉</div><h4>Simülasyon Laboratuvarı</h4><p>Canlı ağ, senaryo ayarları, replay ve olay analizi.</p><b>Aç →</b></a>
            <a href="experiments" target="_self"><span class="sg-module-index">02</span><div class="sg-module-icon">Δ</div><h4>Deney Merkezi</h4><p>Monte Carlo, ablation ve savunma karşılaştırmaları.</p><b>Aç →</b></a>
            <a href="methodology" target="_self"><span class="sg-module-index">03</span><div class="sg-module-icon">λ</div><h4>Bilimsel Metodoloji</h4><p>Modeller, denklemler, metrikler ve deney sözleşmesi.</p><b>Aç →</b></a>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <section class="sg-run-banner">
            <div>
                <span>OPERASYON ÖZETİ</span>
                <h3>{snapshot.status.title()}</h3>
                <p>Demo senaryosu seed 2025 ve GTAD savunmasıyla tek tıkla çalıştırılmaya hazır.</p>
            </div>
            <div class="sg-run-stats">
                <div><span>SON ADIM</span><strong>{snapshot.step}</strong></div>
                <div><span>ENFEKTE</span><strong>{snapshot.infected}</strong></div>
                <div><span>GCC</span><strong>{snapshot.connectivity}</strong></div>
            </div>
            <a class="sg-button sg-button-primary" href="simulation" target="_self">Laboratuvara git <span>→</span></a>
        </section>
        """,
        unsafe_allow_html=True,
    )
