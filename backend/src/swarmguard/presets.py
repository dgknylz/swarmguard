from dataclasses import dataclass, replace

from .config import AttackStrategy, DefenseStrategy, SimulationConfig

DEMO_CONFIG = SimulationConfig(
    node_count=24,
    area_width=1_000,
    area_height=700,
    communication_range=250,
    speed=6,
    beta=0.16,
    gamma=0.09,
    steps=60,
    seed=2025,
    initial_infected_count=2,
    attack_strategy=AttackStrategy.HIGHEST_BETWEENNESS,
    defense_strategy=DefenseStrategy.GTAD_RISK,
    defense_budget=2,
    defense_range_multiplier=1.6,
    defense_max_degree=7,
)

# The showcase: Spektral Kalkan under a tight budget and imperfect detection, the regime
# where the Perron ordering is measurably better than a random one (README, Tablo 2).
SHOWCASE_CONFIG = replace(
    DEMO_CONFIG,
    defense_strategy=DefenseStrategy.SPECTRAL_SHIELD,
    defense_budget=1,
    detection_probability=0.5,
    defense_memory=3,
    initial_infected_count=6,
)

# Undefended pair around the extinction threshold of Teorem 2 (β* ≈ 0.034 for γ = 0.2).
THRESHOLD_BASE = replace(
    DEMO_CONFIG,
    gamma=0.2,
    steps=80,
    initial_infected_count=4,
    defense_strategy=DefenseStrategy.NONE,
    defense_budget=0,
)


@dataclass(frozen=True, slots=True)
class ScenarioPreset:
    slug: str
    title: str
    category: str
    description: str
    icon: str
    config: SimulationConfig


SCENARIO_PRESETS = (
    ScenarioPreset(
        slug="spectral-demo",
        title="Spektral Kalkan Demo",
        category="Önerilen",
        description="Adım başına tek müdahale ve %50 tespitle Perron sıralı karantinayı gösterir.",
        icon="◈",
        config=SHOWCASE_CONFIG,
    ),
    ScenarioPreset(
        slug="below-threshold",
        title="Eşik Altı · Garantili Sönüm",
        category="Teori",
        description="β < β*: Teorem 2 savunma olmadan da salgının söneceğini garanti eder.",
        icon="↘",
        config=replace(THRESHOLD_BASE, beta=0.027),
    ),
    ScenarioPreset(
        slug="above-threshold",
        title="Eşik Üstü · Kalıcı Salgın",
        category="Teori",
        description="Aynı sürü, β ≈ 3β*: garanti biter ve salgın savunmasız ağda tutunur.",
        icon="↗",
        config=replace(THRESHOLD_BASE, beta=0.10),
    ),
    ScenarioPreset(
        slug="rapid-outbreak",
        title="Hızlı Salgın",
        category="Saldırı",
        description="Yüksek beta ve düşük iyileşme oranıyla savunmanın tepki hızını zorlar.",
        icon="⚡",
        config=SimulationConfig(
            node_count=36,
            area_width=1_100,
            area_height=750,
            communication_range=245,
            speed=7,
            beta=0.34,
            gamma=0.03,
            steps=80,
            seed=1307,
            initial_infected_count=3,
            attack_strategy=AttackStrategy.HIGHEST_BETWEENNESS,
            defense_strategy=DefenseStrategy.SPECTRAL_SHIELD,
            defense_budget=3,
            defense_range_multiplier=1.7,
            defense_max_degree=9,
        ),
    ),
    ScenarioPreset(
        slug="fragile-network",
        title="Kırılgan Haberleşme",
        category="Topoloji",
        description="Düşük menzilli seyrek ağda bağlantısallık kaybını ve GTAD onarımını inceler.",
        icon="∿",
        config=SimulationConfig(
            node_count=28,
            area_width=1_300,
            area_height=850,
            communication_range=150,
            speed=10,
            beta=0.18,
            gamma=0.06,
            steps=100,
            seed=41,
            initial_infected_count=2,
            attack_strategy=AttackStrategy.HIGHEST_DEGREE,
            defense_strategy=DefenseStrategy.GTAD_RISK,
            defense_budget=3,
            defense_range_multiplier=2.0,
            defense_max_degree=7,
        ),
    ),
    ScenarioPreset(
        slug="dense-swarm",
        title="Yoğun Sürü",
        category="Ölçek",
        description="Seksen İHA'lı yoğun topolojide yeniden bağlantı davranışını ve hesap yükünü ölçer.",
        icon="∷",
        config=SimulationConfig(
            node_count=80,
            area_width=900,
            area_height=650,
            communication_range=260,
            speed=5,
            beta=0.14,
            gamma=0.10,
            steps=80,
            seed=8080,
            initial_infected_count=4,
            attack_strategy=AttackStrategy.RANDOM,
            defense_strategy=DefenseStrategy.RANDOM_REWIRING,
            defense_budget=3,
            defense_range_multiplier=1.5,
            defense_max_degree=12,
        ),
    ),
    ScenarioPreset(
        slug="quarantine-defense",
        title="Kritik Düğüm Karantinası",
        category="Savunma",
        description="Merkezi düğümleri hedefleyen saldırıya merkeziyet tabanlı karantina uygular.",
        icon="⊘",
        config=SimulationConfig(
            node_count=40,
            area_width=1_000,
            area_height=700,
            communication_range=240,
            speed=6,
            beta=0.22,
            gamma=0.07,
            steps=90,
            seed=314,
            initial_infected_count=3,
            attack_strategy=AttackStrategy.HIGHEST_BETWEENNESS,
            defense_strategy=DefenseStrategy.CENTRALITY_QUARANTINE,
            defense_budget=2,
            defense_range_multiplier=1.5,
            defense_max_degree=9,
        ),
    ),
    ScenarioPreset(
        slug="gtad-demo",
        title="GTAD Dengeli Demo",
        category="Karşılaştırma",
        description="Rapor Tablo 6–7'nin koşulu: GTAD bağlantısallığı artırır, yayılımı değiştirmez.",
        icon="◇",
        config=DEMO_CONFIG,
    ),
    ScenarioPreset(
        slug="unprotected-baseline",
        title="Savunmasız Baseline",
        category="Referans",
        description="GTAD demosuyla aynı seed ve koşullarda savunmasız referans sonucu üretir.",
        icon="—",
        config=SimulationConfig(
            node_count=24,
            area_width=1_000,
            area_height=700,
            communication_range=250,
            speed=6,
            beta=0.16,
            gamma=0.09,
            steps=60,
            seed=2025,
            initial_infected_count=2,
            attack_strategy=AttackStrategy.HIGHEST_BETWEENNESS,
            defense_strategy=DefenseStrategy.NONE,
            defense_budget=0,
            defense_range_multiplier=1.6,
            defense_max_degree=7,
        ),
    ),
    ScenarioPreset(
        slug="mobility-stress",
        title="Hareketlilik Stresi",
        category="Dayanıklılık",
        description="Yüksek hız ve sınırlı menzille sık bağlantı kopmaları altında adaptasyonu sınar.",
        icon="≋",
        config=SimulationConfig(
            node_count=45,
            area_width=1_200,
            area_height=800,
            communication_range=190,
            speed=24,
            beta=0.20,
            gamma=0.08,
            steps=120,
            seed=9001,
            initial_infected_count=3,
            attack_strategy=AttackStrategy.HIGHEST_DEGREE,
            defense_strategy=DefenseStrategy.SPECTRAL_SHIELD,
            defense_budget=3,
            defense_range_multiplier=1.9,
            defense_max_degree=8,
            detection_probability=0.5,
            defense_memory=3,
        ),
    ),
)

PRESET_BY_SLUG = {preset.slug: preset for preset in SCENARIO_PRESETS}


def get_scenario_preset(slug: str) -> ScenarioPreset:
    try:
        return PRESET_BY_SLUG[slug]
    except KeyError as error:
        raise ValueError(f"Bilinmeyen senaryo profili: {slug}") from error
