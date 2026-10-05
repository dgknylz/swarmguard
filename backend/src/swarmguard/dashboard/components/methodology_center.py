from __future__ import annotations

from dataclasses import asdict, dataclass

from ...config import AttackStrategy, DefenseStrategy
from ...experiments import GTAD_ABLATIONS, RESULT_METRICS


@dataclass(frozen=True, slots=True)
class MethodDefinition:
    key: str
    title: str
    summary: str
    rule: str


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    key: str
    title: str
    direction: str
    meaning: str


ATTACK_METHODS = (
    MethodDefinition(
        "random",
        "Rastgele başlangıç",
        "Başlangıç enfeksiyonlarını tekrarsız rastgele örnekler.",
        "Seed kontrollü NumPy seçimidir.",
    ),
    MethodDefinition(
        "highest_degree",
        "En yüksek derece",
        "En fazla doğrudan komşuya sahip düğümleri hedefler.",
        "Eşitlikte küçük düğüm kimliği önce gelir.",
    ),
    MethodDefinition(
        "highest_betweenness",
        "En yüksek betweenness",
        "En çok kısa yol üzerinde bulunan köprü düğümleri hedefler.",
        "Normalize NetworkX betweenness merkeziyeti kullanılır.",
    ),
)

DEFENSE_METHODS = (
    MethodDefinition(
        "none",
        "Savunmasız baseline",
        "Topolojiye müdahale etmez; karşılaştırmaların referansıdır.",
        "Müdahale maliyeti her adımda sıfırdır.",
    ),
    MethodDefinition(
        "random_rewiring",
        "Rastgele yeniden bağlantı",
        "Riskli sağlıklı-enfekte kenarları kesip sağlıklı düğümler arasında bağlantı kurar.",
        "Her yeniden bağlantı iki eylem tüketir ve fiziksel menzile uyar.",
    ),
    MethodDefinition(
        "centrality_quarantine",
        "Merkeziyet karantinası",
        "Derece ve betweenness bileşiminde öne çıkan enfekte düğümleri izole eder.",
        "Skor: 0.55 normalize derece + 0.45 normalize betweenness.",
    ),
    MethodDefinition(
        "gtad_risk",
        "GTAD Risk",
        "Düğüm riskini izler ve sağlıklı düğümler arasında çok amaçlı bağlantılar ekler.",
        "Menzil, azami derece ve adım bütçesi birlikte uygulanır.",
    ),
)

METRIC_DEFINITIONS = (
    MetricDefinition(
        "final_infected_ratio", "Son enfeksiyon oranı", "Düşük", "Son karede enfekte İHA payı."
    ),
    MetricDefinition(
        "peak_infected_ratio",
        "Tepe enfeksiyon oranı",
        "Düşük",
        "Koşu boyunca görülen en yüksek enfekte İHA payı.",
    ),
    MetricDefinition(
        "mean_infected_ratio",
        "Ortalama enfeksiyon oranı",
        "Düşük",
        "Başlangıç sonrası bütün karelerin enfeksiyon ortalaması.",
    ),
    MetricDefinition(
        "mean_largest_component_ratio",
        "Ortalama büyük bileşen",
        "Yüksek",
        "En büyük bağlı bileşendeki düğüm payının zaman ortalaması.",
    ),
    MetricDefinition(
        "mean_global_efficiency",
        "Ortalama ağ verimliliği",
        "Yüksek",
        "Düğüm çiftleri arasındaki ters kısa yol uzunluklarının ortalaması.",
    ),
    MetricDefinition(
        "mean_algebraic_connectivity",
        "Ortalama λ₂",
        "Yüksek",
        "Graf Laplasyeninin ikinci küçük özdeğeri; kopuk ağda sıfır.",
    ),
    MetricDefinition(
        "total_intervention_cost",
        "Toplam müdahale maliyeti",
        "Düşük",
        "Uygulanan bağlantı ekleme, kesme ve karantina eylemlerinin toplamı.",
    ),
)

GTAD_RISK_WEIGHTS = {
    "infection": 0.45,
    "exposure": 0.30,
    "degree": 0.15,
    "betweenness": 0.10,
}

GTAD_LINK_WEIGHTS = {"connectivity": 0.50, "safety": 0.30, "distance": 0.20}


def methodology_manifest() -> dict[str, object]:
    return {
        "attack_methods": [asdict(method) for method in ATTACK_METHODS],
        "defense_methods": [asdict(method) for method in DEFENSE_METHODS],
        "metrics": [asdict(metric) for metric in METRIC_DEFINITIONS],
        "gtad_risk_weights": GTAD_RISK_WEIGHTS,
        "gtad_link_weights": GTAD_LINK_WEIGHTS,
        "ablation_variants": {name: weights.to_dict() for name, weights in GTAD_ABLATIONS.items()},
        "attack_enum": [strategy.value for strategy in AttackStrategy],
        "defense_enum": [strategy.value for strategy in DefenseStrategy],
        "result_metrics": list(RESULT_METRICS),
    }


def _render_model(st) -> None:
    st.markdown("#### Dinamik ağ ve hareket modeli")
    st.caption(
        "Her İHA iki boyutlu görev alanında sabit hız vektörüyle hareket eder. Sınırda yansıma "
        "uygulanır; haberleşme grafı her adımda güncel konumlardan yeniden kurulur."
    )
    st.latex(r"G_t=(V,E_t),\qquad (i,j)\in E_t \iff \lVert p_i(t)-p_j(t)\rVert_2\leq r")
    st.markdown(
        """
        <div class="sg-method-flow">
            <div><b>01</b><span>Konumları ilerlet</span><small>Sınırda yansıt</small></div>
            <i>→</i><div><b>02</b><span>Grafı yeniden kur</span><small>Öklid menzili</small></div>
            <i>→</i><div><b>03</b><span>Savunmayı uygula</span><small>Topoloji eylemleri</small></div>
            <i>→</i><div><b>04</b><span>SIS adımını çöz</span><small>Senkron geçiş</small></div>
            <i>→</i><div><b>05</b><span>Metrikleri kaydet</span><small>Denetlenebilir kare</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### SIS saldırı yayılımı")
    probability_column, recovery_column = st.columns(2)
    with probability_column:
        st.markdown("**Sağlıklı → enfekte**")
        st.latex(r"P(S\rightarrow I\mid k)=1-(1-\beta)^k")
        st.caption("k, adım başındaki enfekte komşu sayısı; β, komşu başına bulaşma olasılığıdır.")
    with recovery_column:
        st.markdown("**Enfekte → sağlıklı**")
        st.latex(r"P(I\rightarrow S)=\gamma")
        st.caption("γ, her enfekte düğümün bağımsız iyileşme olasılığıdır.")
    st.info(
        "Bütün sağlık geçişleri adımın başlangıcındaki durumdan hesaplanır ve birlikte uygulanır. "
        "Bu nedenle düğüm sırası sonucu değiştirmez."
    )


def _render_algorithms(st) -> None:
    st.markdown("#### Saldırı başlangıç stratejileri")
    attack_columns = st.columns(3)
    for column, method in zip(attack_columns, ATTACK_METHODS):
        with column:
            st.markdown(
                f"<article class='sg-method-card'><small>{method.key}</small><h4>{method.title}</h4><p>{method.summary}</p><b>{method.rule}</b></article>",
                unsafe_allow_html=True,
            )

    st.markdown("#### Ortak savunma sözleşmesi")
    st.markdown(
        "<div class='sg-lifecycle'><span>OBSERVE</span><i>→</i><span>DECIDE</span><i>→</i><span>APPLY</span><i>→</i><span>REPORT</span></div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Her algoritma aynı bağlamı gözler, deterministik bir karar üretir, geçerli eylemleri uygular "
        "ve uygulanan/reddedilen eylemlerle müdahale maliyetini raporlar."
    )
    for method in DEFENSE_METHODS:
        with st.expander(method.title, expanded=method.key == "gtad_risk"):
            st.write(method.summary)
            st.caption(method.rule)

    st.markdown("#### GTAD risk ve bağlantı puanı")
    st.latex(r"R_i=0.45I_i+0.30X_i+0.15\frac{d_i}{d_{max}}+0.10\frac{b_i}{b_{max}}")
    st.caption(
        "I: enfeksiyon göstergesi, X: enfekte komşu oranı, d: derece, b: betweenness. "
        "Bileşenler [0,1] aralığına normalize edilir."
    )
    st.latex(r"S_{ij}=0.50C_{ij}+0.30H_{ij}+0.20D_{ij}")
    st.caption(
        "C: bağlantısallık kazanımı, H: uç noktaların güvenliği, D: radyo mesafesi verimi. "
        "Yalnızca sağlıklı düğüm çiftleri adaydır."
    )
    constraint_columns = st.columns(3)
    constraint_columns[0].metric("Fiziksel kısıt", "d ≤ r × çarpan")
    constraint_columns[1].metric("Topoloji kısıtı", "derece ≤ üst sınır")
    constraint_columns[2].metric("Operasyon kısıtı", "eylem ≤ bütçe")


def _render_experiment_protocol(st) -> None:
    st.markdown("#### Metrik sözlüğü")
    st.dataframe(
        [
            {
                "metrik": metric.title,
                "tercih": metric.direction,
                "tanım": metric.meaning,
                "anahtar": metric.key,
            }
            for metric in METRIC_DEFINITIONS
        ],
        width="stretch",
        hide_index=True,
    )
    protocol_column, statistics_column = st.columns(2, vertical_alignment="top")
    with protocol_column:
        st.markdown("#### Eşleştirilmiş deney protokolü")
        st.markdown(
            """
            1. Tek bir temel senaryo sabitlenir.
            2. Her savunma yöntemi aynı seed kümesiyle çalıştırılır.
            3. Her `(yöntem, seed)` çifti bağımsız koşudur.
            4. Yöntem ortalamaları ve seed-eşli baseline farkları hesaplanır.
            5. Senaryo, yöntemler, metrikler ve yazılım sürümü manifestte mühürlenir.
            """
        )
    with statistics_column:
        st.markdown("#### Belirsizlik raporlama")
        st.latex(r"CI_{95\%}=\bar{x}\pm t_{0.975,n-1}\frac{s}{\sqrt{n}}")
        st.caption(
            "İki taraflı Student-t aralığı kullanılır. n=1 için standart sapma ve aralık genişliği "
            "sıfır raporlanır; güçlü çıkarım için birden fazla seed gerekir."
        )
        st.warning(
            "Güven aralıklarının örtüşmesi veya ayrılması tek başına hipotez testi değildir. "
            "Karşılaştırma ekranındaki farklar gözlenen etki yönünü gösterir."
        )
    st.markdown("#### GTAD ablation tasarımı")
    st.dataframe(
        [
            {
                "varyant": name,
                "bağlantısallık": weights.to_dict()["connectivity"],
                "güvenlik": weights.to_dict()["safety"],
                "mesafe": weights.to_dict()["distance"],
            }
            for name, weights in GTAD_ABLATIONS.items()
        ],
        width="stretch",
        hide_index=True,
    )


def _render_scope(st) -> None:
    scope_column, limitation_column = st.columns(2, vertical_alignment="top")
    with scope_column:
        st.markdown("#### Modelin kapsadığı alan")
        st.success(
            "2B hareket · dinamik yönsüz graf · mesafe tabanlı radyo bağlantısı · SIS yayılımı · "
            "topoloji savunmaları · seed kontrollü Monte Carlo"
        )
        st.markdown("#### Tekrarlanabilirlik ilkeleri")
        st.markdown(
            "- Aynı yapılandırma ve seed aynı sonucu üretir.\n"
            "- Yöntemler aynı seed kümesinde karşılaştırılır.\n"
            "- Her deney SHA-256 parmak izli manifest üretir.\n"
            "- Simülasyon çekirdeği arayüzden bağımsız test edilir."
        )
    with limitation_column:
        st.markdown("#### Kapsam dışı ve sınırlamalar")
        st.error(
            "Gerçek uçuş kontrolü · fiziksel İHA bağlantısı · 3B aerodinamik · gerçek zararlı yazılım · "
            "kriptografik saldırı yürütme · makine öğrenmesi tabanlı tespit"
        )
        st.markdown("#### Yorumlama sınırları")
        st.markdown(
            "- Sonuçlar seçilen hareket, menzil ve SIS varsayımlarına bağlıdır.\n"
            "- Müdahale maliyeti eylem sayısıdır; enerji tüketimi değildir.\n"
            "- Daha yüksek bağlantısallık her zaman daha düşük enfeksiyon anlamına gelmez.\n"
            "- Bu platform karar desteği ve araştırma prototipidir; uçuş sertifikasyon aracı değildir."
        )


def render_methodology_center(st) -> None:
    st.markdown(
        """
        <section class="sg-methodology-hero">
            <div><span>METODOLOJİ VE ALGORİTMALAR</span><h2>Her sonucun arkasındaki model açık.</h2></div>
            <p>SwarmGuard'ın varsayımlarını, denklemlerini, algoritma kararlarını ve deney protokolünü uygulama davranışıyla aynı sözleşme altında incele.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <section class="sg-research-question">
            <small>ARAŞTIRMA SORUSU</small>
            <h3>Graf yapısını dikkate alan adaptif topoloji yeniden yapılandırması, dinamik İHA ağlarında SIS tipi bir siber saldırıya karşı dayanıklılığı temel yöntemlerden daha fazla artırır mı?</h3>
        </section>
        """,
        unsafe_allow_html=True,
    )
    model_tab, algorithms_tab, experiment_tab, scope_tab = st.tabs(
        ["◎ Model", "◇ Algoritmalar", "∿ Metrikler ve Deney", "◌ Kapsam ve Sınırlar"]
    )
    with model_tab:
        _render_model(st)
    with algorithms_tab:
        _render_algorithms(st)
    with experiment_tab:
        _render_experiment_protocol(st)
    with scope_tab:
        _render_scope(st)
