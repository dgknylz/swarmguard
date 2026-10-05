from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import pi

from ...config import AttackStrategy, DefenseStrategy, SimulationConfig
from ...presets import ScenarioPreset

ATTACK_LABELS = {
    AttackStrategy.RANDOM: "Rastgele başlangıç",
    AttackStrategy.HIGHEST_DEGREE: "En yüksek derece",
    AttackStrategy.HIGHEST_BETWEENNESS: "En yüksek betweenness",
}

DEFENSE_LABELS = {
    DefenseStrategy.NONE: "Savunmasız baseline",
    DefenseStrategy.RANDOM_REWIRING: "Rastgele yeniden bağlantı",
    DefenseStrategy.CENTRALITY_QUARANTINE: "Merkeziyet karantinası",
    DefenseStrategy.GTAD_RISK: "GTAD risk tabanlı",
}


@dataclass(frozen=True)
class ScenarioSummary:
    area: str
    expected_degree: float
    attack_pressure: str
    workload: str
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class BuilderResult:
    submitted: bool
    config: SimulationConfig | None


def summarize_scenario(config: SimulationConfig) -> ScenarioSummary:
    coverage = min(
        1.0, pi * config.communication_range**2 / (config.area_width * config.area_height)
    )
    expected_degree = coverage * max(0, config.node_count - 1)
    pressure = config.beta / max(config.gamma, 0.01)
    attack_pressure = "Yüksek" if pressure >= 3 else "Orta" if pressure >= 1.25 else "Düşük"
    operations = config.node_count * config.steps
    workload = "Yüksek" if operations >= 30_000 else "Orta" if operations >= 8_000 else "Hızlı"
    warnings: list[str] = []

    if expected_degree < 2:
        warnings.append("Haberleşme menzili parçalı bir başlangıç ağı oluşturabilir.")
    if config.initial_infected_count / config.node_count > 0.25:
        warnings.append("Başlangıçtaki enfekte oranı %25'in üzerinde.")
    if config.defense_max_degree >= config.node_count:
        warnings.append("Azami derece düğüm sayısına göre etkisiz kalabilir.")
    if config.defense_strategy is DefenseStrategy.NONE:
        warnings.append("Bu koşu savunmasız baseline olarak çalışacak.")

    return ScenarioSummary(
        area=f"{config.area_width:.0f} × {config.area_height:.0f} m",
        expected_degree=expected_degree,
        attack_pressure=attack_pressure,
        workload=workload,
        warnings=tuple(warnings),
    )


def render_preset_library(st, presets: Sequence[ScenarioPreset]) -> ScenarioPreset | None:
    options = [preset.slug for preset in presets] + ["custom"]
    labels = {preset.slug: f"{preset.icon} {preset.title}" for preset in presets}
    labels["custom"] = "+ Özel senaryo"
    selected_slug = st.pills(
        "Senaryo kütüphanesi",
        options,
        default=presets[0].slug,
        format_func=labels.get,
        key="scenario-preset",
        width="stretch",
        wrap=True,
    )
    if selected_slug == "custom" or selected_slug is None:
        st.markdown(
            """
            <section class="sg-preset-detail">
                <div class="sg-preset-symbol">+</div>
                <div><span>ÖZEL YAPILANDIRMA</span><h4>Kendi bilimsel senaryonu oluştur.</h4><p>Varsayılan model değerlerinden başla ve bütün parametreleri aşağıdaki formdan belirle.</p></div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        return None

    preset = next(item for item in presets if item.slug == selected_slug)
    config = preset.config
    st.markdown(
        f"""
        <section class="sg-preset-detail">
            <div class="sg-preset-symbol">{preset.icon}</div>
            <div>
                <span>{preset.category.upper()} · SEED {config.seed}</span>
                <h4>{preset.title}</h4>
                <p>{preset.description}</p>
            </div>
            <div class="sg-preset-facts">
                <div><b>{config.node_count}</b><small>İHA</small></div>
                <div><b>{config.steps}</b><small>ADIM</small></div>
                <div><b>{config.beta:.2f}</b><small>BETA</small></div>
                <div><b>{config.defense_strategy.value.upper()}</b><small>SAVUNMA</small></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    return preset


def render_scenario_builder(st, base: SimulationConfig, *, key_prefix: str) -> BuilderResult:
    with st.form(f"{key_prefix}-form", border=False):
        st.markdown("#### 01 · Sürü ve görev alanı")
        st.caption(
            "Fiziksel alanı, sürü büyüklüğünü ve hareket modelinin temel sınırlarını tanımla."
        )
        node_col, width_col, height_col, range_col = st.columns(4)
        node_count = node_col.number_input(
            "İHA sayısı",
            min_value=2,
            max_value=500,
            value=base.node_count,
            key=f"{key_prefix}-nodes",
        )
        area_width = width_col.number_input(
            "Alan genişliği (m)",
            min_value=100.0,
            max_value=100_000.0,
            value=float(base.area_width),
            step=50.0,
            key=f"{key_prefix}-width",
        )
        area_height = height_col.number_input(
            "Alan yüksekliği (m)",
            min_value=100.0,
            max_value=100_000.0,
            value=float(base.area_height),
            step=50.0,
            key=f"{key_prefix}-height",
        )
        communication_range = range_col.number_input(
            "Haberleşme menzili (m)",
            min_value=1.0,
            max_value=100_000.0,
            value=float(base.communication_range),
            step=10.0,
            key=f"{key_prefix}-range",
        )
        speed_col, steps_col, seed_col = st.columns(3)
        speed = speed_col.number_input(
            "Hareket hızı",
            min_value=0.0,
            max_value=1_000.0,
            value=float(base.speed),
            step=1.0,
            key=f"{key_prefix}-speed",
        )
        steps = steps_col.number_input(
            "Zaman adımı",
            min_value=1,
            max_value=10_000,
            value=base.steps,
            key=f"{key_prefix}-steps",
        )
        seed = seed_col.number_input(
            "Rastgelelik seed'i",
            min_value=0,
            max_value=2**32 - 1,
            value=base.seed,
            key=f"{key_prefix}-seed",
        )

        st.markdown("#### 02 · Saldırı modeli")
        st.caption("SIS yayılımını ve saldırının başlayacağı kritik düğüm stratejisini belirle.")
        infected_col, attack_col, beta_col, gamma_col = st.columns(4)
        initial_infected_count = infected_col.number_input(
            "İlk enfekte İHA",
            min_value=1,
            max_value=int(node_count),
            value=min(base.initial_infected_count, int(node_count)),
            key=f"{key_prefix}-infected",
        )
        attack_strategy = attack_col.selectbox(
            "Saldırı başlangıcı",
            list(AttackStrategy),
            index=list(AttackStrategy).index(base.attack_strategy),
            format_func=ATTACK_LABELS.get,
            key=f"{key_prefix}-attack",
        )
        beta = beta_col.slider(
            "Enfeksiyon · β",
            0.0,
            1.0,
            float(base.beta),
            0.01,
            key=f"{key_prefix}-beta",
        )
        gamma = gamma_col.slider(
            "İyileşme · γ",
            0.0,
            1.0,
            float(base.gamma),
            0.01,
            key=f"{key_prefix}-gamma",
        )

        st.markdown("#### 03 · Savunma ve GTAD kısıtları")
        st.caption(
            "Savunma algoritmasını ve her adımda kullanabileceği müdahale kapasitesini sınırla."
        )
        defense_col, budget_col, multiplier_col, degree_col = st.columns(4)
        defense_strategy = defense_col.selectbox(
            "Savunma algoritması",
            list(DefenseStrategy),
            index=list(DefenseStrategy).index(base.defense_strategy),
            format_func=DEFENSE_LABELS.get,
            key=f"{key_prefix}-defense",
        )
        defense_budget = budget_col.number_input(
            "Müdahale bütçesi",
            min_value=0,
            max_value=100,
            value=base.defense_budget,
            key=f"{key_prefix}-budget",
        )
        defense_range_multiplier = multiplier_col.slider(
            "Menzil çarpanı",
            1.0,
            5.0,
            float(base.defense_range_multiplier),
            0.1,
            key=f"{key_prefix}-multiplier",
        )
        defense_max_degree = degree_col.number_input(
            "Azami düğüm derecesi",
            min_value=1,
            max_value=max(1, int(node_count) - 1),
            value=min(base.defense_max_degree, max(1, int(node_count) - 1)),
            key=f"{key_prefix}-max-degree",
        )
        submitted = st.form_submit_button(
            "Senaryoyu doğrula ve çalıştır",
            type="primary",
            width="stretch",
        )

    try:
        config = SimulationConfig(
            node_count=int(node_count),
            area_width=float(area_width),
            area_height=float(area_height),
            communication_range=float(communication_range),
            speed=float(speed),
            beta=float(beta),
            gamma=float(gamma),
            steps=int(steps),
            seed=int(seed),
            initial_infected_count=int(initial_infected_count),
            attack_strategy=attack_strategy,
            defense_strategy=defense_strategy,
            defense_budget=int(defense_budget),
            defense_range_multiplier=float(defense_range_multiplier),
            defense_max_degree=int(defense_max_degree),
        )
    except ValueError as error:
        st.error(f"Senaryo doğrulanamadı: {error}")
        return BuilderResult(submitted=submitted, config=None)

    summary = summarize_scenario(config)
    st.markdown(
        f"""
        <section class="sg-scenario-summary">
            <div><span>GÖREV ALANI</span><strong>{summary.area}</strong></div>
            <div><span>BEKLENEN DERECE</span><strong>{summary.expected_degree:.1f}</strong></div>
            <div><span>SALDIRI BASINCI</span><strong>{summary.attack_pressure}</strong></div>
            <div><span>HESAP YÜKÜ</span><strong>{summary.workload}</strong></div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    for warning in summary.warnings:
        st.warning(warning, icon="⚠️")
    if submitted:
        st.success("Senaryo doğrulandı. Simülasyon sonucu Canlı Ağ sekmesine aktarıldı.")
    return BuilderResult(submitted=submitted, config=config)
