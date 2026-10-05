from dataclasses import dataclass

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
        slug="gtad-demo",
        title="GTAD Dengeli Demo",
        category="Önerilen",
        description="Adaptif topoloji savunmasını dengeli saldırı ve hareket koşullarında gösterir.",
        icon="◈",
        config=DEMO_CONFIG,
    ),
    ScenarioPreset(
        slug="rapid-outbreak",
        title="Hızlı Salgın",
        category="Saldırı",
        description="Yüksek beta ve düşük iyileşme oranıyla savunmanın tepki hızını zorlar.",
        icon="↗",
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
            defense_strategy=DefenseStrategy.GTAD_RISK,
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
            defense_strategy=DefenseStrategy.GTAD_RISK,
            defense_budget=3,
            defense_range_multiplier=1.9,
            defense_max_degree=8,
        ),
    ),
)

PRESET_BY_SLUG = {preset.slug: preset for preset in SCENARIO_PRESETS}


def get_scenario_preset(slug: str) -> ScenarioPreset:
    try:
        return PRESET_BY_SLUG[slug]
    except KeyError as error:
        raise ValueError(f"Bilinmeyen senaryo profili: {slug}") from error
