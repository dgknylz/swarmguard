from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

PAGE_DESCRIPTIONS = {
    "Genel Bakış": "Sürü güvenliği, aktif senaryo ve araştırma araçlarının operasyon özeti.",
    "Simülasyon": "Dinamik İHA ağında saldırı yayılımını ve adaptif savunmayı izle.",
    "Çalışma Alanı": "Aktif senaryoyu, simülasyonu ve deney geçmişini kaydet veya geri yükle.",
    "Deneyler": "Monte Carlo koşularını, ablation analizlerini ve savunma sonuçlarını yönet.",
    "Metodoloji": "Model varsayımlarını, algoritmaları ve tekrarlanabilir deney tasarımını incele.",
    "Hakkında": "SwarmGuard'ın amacını, mimarisini, ilkelerini ve ürün kapsamını keşfet.",
}


@dataclass(frozen=True)
class ShellContext:
    scenario_status: str
    node_count: str
    defense: str
    seed: str
    current_step: str
    infected_count: str


def get_shell_context(session_state: Mapping[str, Any]) -> ShellContext:
    config = session_state.get("config")
    frames = session_state.get("frames") or []
    frame = frames[-1] if frames else None
    metrics = frame.metrics if frame is not None else {}

    return ShellContext(
        scenario_status="Aktif" if config is not None else "Beklemede",
        node_count=str(config.node_count) if config is not None else "—",
        defense=(config.defense_strategy.value if config is not None else "—"),
        seed=str(config.seed) if config is not None else "—",
        current_step=str(frame.step) if frame is not None else "—",
        infected_count=str(metrics.get("infected_count", "—")),
    )


def render_site_header(st) -> None:
    context = get_shell_context(st.session_state)
    tone = "online" if context.scenario_status == "Aktif" else "idle"
    st.markdown(
        f"""
        <div class="sg-site-header">
            <div class="sg-brand">
                <div class="sg-brand-mark">◈</div>
                <div>
                    <div class="sg-brand-name">SWARMGUARD</div>
                    <div class="sg-brand-subtitle">UAV CYBER RESILIENCE PLATFORM</div>
                </div>
            </div>
            <div class="sg-site-meta">
                <div class="sg-scenario-chip">
                    <span class="sg-status-dot sg-status-{tone}"></span>
                    SENARYO {context.scenario_status.upper()}
                </div>
                <span>İHA {context.node_count}</span>
                <span>SEED {context.seed}</span>
                <span>{context.defense.upper()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(st, page_title: str) -> None:
    description = PAGE_DESCRIPTIONS.get(page_title, "SwarmGuard araştırma platformu")
    st.markdown(
        f"""
        <header class="sg-topbar">
            <div>
                <div class="sg-eyebrow">OPERASYON MERKEZİ / {page_title.upper()}</div>
                <h1>{page_title}</h1>
                <p>{description}</p>
            </div>
            <div class="sg-system-pill">
                <span class="sg-status-dot sg-status-online"></span>
                SİSTEM ÇEVRİMİÇİ
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_footer(st) -> None:
    st.markdown(
        """
        <footer class="sg-footer">
            <span>SWARMGUARD RESEARCH PLATFORM</span>
            <span>v1.1.0 · M13 · REPRODUCIBLE BUILD</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )
