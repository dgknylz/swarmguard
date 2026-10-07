from __future__ import annotations

from dataclasses import dataclass

from ..design_system import render_design_system_showcase


@dataclass(frozen=True, slots=True)
class ArchitectureLayer:
    key: str
    title: str
    technology: str
    responsibility: str


@dataclass(frozen=True, slots=True)
class ProjectProfile:
    name: str
    version: str
    completed_steps: int
    total_steps: int
    architecture: tuple[ArchitectureLayer, ...]
    capabilities: tuple[str, ...]
    principles: tuple[str, ...]


def calculate_progress(completed: int, total: int) -> float:
    if total <= 0:
        raise ValueError("Toplam adım pozitif olmalıdır")
    if not 0 <= completed <= total:
        raise ValueError("Tamamlanan adım geçerli aralıkta olmalıdır")
    return completed / total


def get_project_profile() -> ProjectProfile:
    return ProjectProfile(
        name="SwarmGuard",
        version="1.1.0",
        completed_steps=47,
        total_steps=47,
        architecture=(
            ArchitectureLayer(
                "experience",
                "Ürün deneyimi",
                "Streamlit",
                "Çok sayfalı web arayüzü, oturum yönetimi ve araştırma iş akışları.",
            ),
            ArchitectureLayer(
                "simulation",
                "Simülasyon çekirdeği",
                "Python · NetworkX · NumPy",
                "Dinamik hareket, haberleşme grafı, SIS yayılımı ve savunma yaşam döngüsü.",
            ),
            ArchitectureLayer(
                "science",
                "Deney ve istatistik",
                "SciPy · PyArrow",
                "Monte Carlo, eşleştirilmiş seed analizi, güven aralıkları ve veri çıktıları.",
            ),
            ArchitectureLayer(
                "service",
                "Servis sözleşmesi",
                "FastAPI · WebSocket",
                "Simülasyon kontrolü ve alternatif istemciler için tip güvenli API katmanı.",
            ),
        ),
        capabilities=(
            "Dinamik İHA haberleşme ağı",
            "Senkron SIS saldırı yayılımı",
            "Dört savunma yaklaşımı",
            "Canlı replay ve düğüm inceleme",
            "Monte Carlo ve GTAD ablation",
            "Karşılaştırma ve araştırma raporları",
        ),
        principles=(
            "Tekrarlanabilirlik",
            "Denetlenebilirlik",
            "Yöntemler arası adalet",
            "Sorumlu güvenlik araştırması",
        ),
    )


def render_about_center(st) -> None:
    profile = get_project_profile()
    progress = calculate_progress(profile.completed_steps, profile.total_steps)
    st.markdown(
        f"""
        <section class="sg-about-hero">
            <div class="sg-about-copy">
                <span>SWARMGUARD · v{profile.version}</span>
                <h2>İHA sürülerinin siber dayanıklılığını görünür ve ölçülebilir kılıyoruz.</h2>
                <p>SwarmGuard; saldırı yayılımını, ağ topolojisini ve savunma kararlarını aynı tekrarlanabilir araştırma ortamında bir araya getiren açık, denetlenebilir bir simülasyon platformudur.</p>
                <div><a href="simulation" target="_self">Simülasyonu aç →</a><a href="methodology" target="_self">Bilimsel temeli incele</a></div>
            </div>
            <div class="sg-about-mark"><div>◈</div><strong>{progress:.0%}</strong><span>ÜRÜN YOL HARİTASI</span><small>{profile.completed_steps} / {profile.total_steps} adım</small></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="sg-about-statement">
            <small>PROBLEM</small><h3>Hareket eden bir sürüde güvenlik ve bağlantısallık aynı anda değişir.</h3>
            <p>Bir savunma enfeksiyon temasını azaltırken ağı parçalayabilir; bağlantısallığı artıran bir müdahale ise saldırı yüzeyini büyütebilir. SwarmGuard bu gerilimi tek bir başarı sayısına gizlemek yerine enfeksiyon, bağlantısallık ve müdahale maliyetini birlikte ölçer.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Platform neler sunuyor?")
    capability_html = "".join(
        f"<article><b>{index:02d}</b><span>{capability}</span></article>"
        for index, capability in enumerate(profile.capabilities, start=1)
    )
    st.markdown(
        f"<section class='sg-capability-grid'>{capability_html}</section>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Sistem mimarisi")
    architecture_html = "".join(
        f"<article><small>{layer.key.upper()}</small><h4>{layer.title}</h4><b>{layer.technology}</b><p>{layer.responsibility}</p></article>"
        for layer in profile.architecture
    )
    st.markdown(
        f"<section class='sg-architecture-grid'>{architecture_html}</section>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Streamlit sürümü tek uygulama olarak yayınlanır. FastAPI/WebSocket ve Next.js katmanları, "
        "ayrık istemci-servis dağıtımı için korunan alternatif mimaridir."
    )

    principle_column, audience_column = st.columns(2, vertical_alignment="top")
    with principle_column:
        st.markdown("#### Tasarım ilkeleri")
        st.markdown(
            """
            - **Tekrarlanabilirlik:** Aynı yapılandırma ve seed aynı sonucu üretir.
            - **Denetlenebilirlik:** Savunma kararları, risk skorları ve eylemler raporlanır.
            - **Adil karşılaştırma:** Yöntemler aynı seed kümeleriyle eşleştirilir.
            - **Çok amaçlı değerlendirme:** Güvenlik, bağlantısallık ve maliyet birlikte okunur.
            """
        )
    with audience_column:
        st.markdown("#### Kimler için?")
        st.markdown(
            """
            - Siber-fiziksel sistem ve ağ güvenliği araştırmacıları
            - İHA sürüleri ve dayanıklı haberleşme üzerine çalışan öğrenciler
            - Savunma algoritmalarını karşılaştırmak isteyen geliştiriciler
            - Bilimsel simülasyon sonuçlarını görsel olarak anlatan ekipler
            """
        )

    st.markdown(
        """
        <section class="sg-responsibility-note">
            <div>⚑</div><article><small>SORUMLU KULLANIM</small><h4>Araştırma ve karar desteği için tasarlandı.</h4><p>SwarmGuard gerçek sistemlere saldırı gerçekleştirmez, fiziksel İHA kontrol etmez ve uçuş güvenliği sertifikasyonu sunmaz. Üretilen sonuçlar tanımlı model varsayımları içinde yorumlanmalıdır.</p></article>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="sg-about-actions">
            <div><small>SONRAKİ ADIM</small><h3>Kendi senaryonu oluştur ve savunmaları karşılaştır.</h3></div>
            <a href="simulation" target="_self">Laboratuvara git →</a>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Tasarım sistemi vitrini"):
        render_design_system_showcase(st)
