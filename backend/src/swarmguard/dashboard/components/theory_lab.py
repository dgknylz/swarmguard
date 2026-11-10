"""Teori Laboratuvarı: every theorem of the project next to its numerical check."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
from math import hypot, pi

import numpy as np

from ...config import DefenseStrategy, SimulationConfig
from ...findings import (
    ENDEMIC_LEVEL,
    SWEEP_HORIZON,
    SWEEP_MULTIPLIERS,
    load_findings,
    sweep_key,
    threshold_sweep,
)
from ...spectral import adjacency_from_edges
from ...theory import (
    adjacency_sequence,
    expected_degree,
    initial_vector,
    linear_bound,
    link_statistics,
    mean_field,
    naive_expected_degree,
    perturbation_check,
    phase_diagram,
    rectangle_distance_cdf,
    simulate_replicates,
    spectral_bound,
    spectral_profile,
)
from ..charts import GRID, PLOT_LAYOUT
from ..performance import cached_simulation
from .findings_charts import scenario_threshold_figure, tightness_figure

RED, MINT, CYAN, AMBER, VIOLET, MUTED = (
    "#fb7185",
    "#5eead4",
    "#38bdf8",
    "#fbbf24",
    "#a78bfa",
    "#7f989d",
)


@dataclass(frozen=True, slots=True)
class TheoryInputs:
    config: SimulationConfig
    distances: np.ndarray
    mean_degrees: np.ndarray
    spectral_radius: np.ndarray
    spread_factor: np.ndarray
    geometric_mean: float
    threshold_beta: float
    monte_carlo: np.ndarray
    monte_carlo_low: np.ndarray
    monte_carlo_high: np.ndarray
    mean_field: np.ndarray
    linear_bound: np.ndarray
    spectral_bound: np.ndarray
    new_infections: np.ndarray
    expected_new: np.ndarray
    upper_new: np.ndarray
    lower_new: np.ndarray
    replicates: int


def undefended(config: SimulationConfig) -> SimulationConfig:
    """Teorem 2 needs a graph sequence chosen independently of the epidemic."""
    return replace(config, defense_strategy=DefenseStrategy.NONE, defense_budget=0)


@lru_cache(maxsize=8)
def compute_theory(config: SimulationConfig) -> TheoryInputs:
    base = undefended(config)
    frames = cached_simulation(base)
    adjacencies = adjacency_sequence(frames)
    initial = initial_vector(frames)
    replicates = int(min(600, max(80, 60_000 // base.node_count)))
    run = simulate_replicates(adjacencies, initial, base.beta, base.gamma, replicates, base.seed)
    profile = spectral_profile(adjacencies, base.beta, base.gamma)
    distances, mean_degrees = link_statistics(frames, base.communication_range)
    upper = base.beta * run.boundary
    return TheoryInputs(
        config=base,
        distances=distances,
        mean_degrees=mean_degrees,
        spectral_radius=profile.spectral_radius,
        spread_factor=profile.spread_factor,
        geometric_mean=profile.geometric_mean,
        threshold_beta=profile.threshold_beta,
        monte_carlo=run.infected.mean(axis=0),
        monte_carlo_low=np.quantile(run.infected, 0.1, axis=0),
        monte_carlo_high=np.quantile(run.infected, 0.9, axis=0),
        mean_field=mean_field(adjacencies, initial, base.beta, base.gamma),
        linear_bound=linear_bound(adjacencies, initial, base.beta, base.gamma),
        spectral_bound=spectral_bound(base.node_count, int(initial.sum()), profile.spread_factor),
        new_infections=run.new_infections.mean(axis=0),
        expected_new=run.expected_new.mean(axis=0),
        upper_new=upper.mean(axis=0),
        lower_new=np.maximum(upper - base.beta**2 * run.pair_term, 0).mean(axis=0),
        replicates=replicates,
    )


@lru_cache(maxsize=8)
def compute_threshold_sweep(config: SimulationConfig) -> dict[str, object]:
    """β sweep around β* for one scenario: shipped for the presets, computed otherwise."""
    key = list(sweep_key(config))
    for item in load_findings()["thresholds"]:
        if item["key"] == key:
            return item
    replicates = int(min(200, max(40, 3_200 // config.node_count)))
    return threshold_sweep(config, replicates=replicates)


def _layout(figure, height: int = 360, **extra):
    below = {
        "legend": {"orientation": "h", "y": -0.24, "x": 0, "bgcolor": "rgba(0,0,0,0)"},
        "margin": {"l": 10, "r": 10, "t": 48, "b": 70},
    }
    figure.update_layout(height=height + 40, **{**PLOT_LAYOUT, **below, **extra})
    figure.update_xaxes(gridcolor=GRID, zeroline=False)
    figure.update_yaxes(gridcolor=GRID, zeroline=False)
    return figure


def _theorem_header(st, label: str, title: str, summary: str) -> None:
    st.markdown(
        f"""
        <div class="sg-theorem-head"><div class="sg-th-kicker">{label}</div><div class="sg-th-title">{title}</div><p>{summary}</p></div>
        """,
        unsafe_allow_html=True,
    )


def _render_intro(st, inputs: TheoryInputs) -> None:
    config = inputs.config
    st.markdown(
        """
        <section class="sg-theory-hero">
            <div>
                <div class="sg-th-kicker">MATEMATİKSEL OMURGA</div>
                <div class="sg-th-hero-title">Dört sonuç, dört sayısal doğrulama.</div>
                <p>Her teorem aşağıda ispatıyla birlikte verilir ve aktif senaryonun savunmasız
                hareket verisiyle sınanır. Grafikler ispatın öngördüğü eşitsizliğin gerçekten
                sağlandığını gösterir.</p>
            </div>
            <ol>
                <li><b>Teorem 1</b> Bağlantı olasılığının kesin formülü</li>
                <li><b>Teorem 2</b> Spektral üst sınır ve sönüm eşiği</li>
                <li><b>Önerme 3</b> Tek adımda yeni enfeksiyon sınırı</li>
                <li><b>Lemma 4</b> Rayleigh pertürbasyon sınırları</li>
            </ol>
        </section>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(5)
    columns[0].metric("İHA sayısı · n", config.node_count)
    mean_radius = float(inputs.spectral_radius.mean())
    columns[1].metric(
        "τ = β/γ",
        f"{config.beta / config.gamma:.2f}" if config.gamma else "∞",
        f"eşik 1/λ̄₁ = {1 / mean_radius:.3f}" if mean_radius else None,
        delta_color="off",
        help="Statik ağda τ < 1/λ₁ ise salgın söner (Teorem 2'nin sonucu).",
    )
    columns[2].metric("Ortalama λ₁", f"{inputs.spectral_radius.mean():.2f}")
    columns[3].metric(
        "σ̄ geometrik ortalama",
        f"{inputs.geometric_mean:.3f}",
        "sönüm garantili" if inputs.geometric_mean < 1 else "eşik üstü",
        delta_color="normal" if inputs.geometric_mean < 1 else "inverse",
    )
    threshold = inputs.threshold_beta
    columns[4].metric(
        "Kritik β*",
        "∞" if threshold == float("inf") else f"{threshold:.4f}",
        help="β < β* ise σ̄ < 1 olur ve Teorem 2 sönümü garanti eder.",
    )


def _render_theorem_1(st, inputs: TheoryInputs) -> None:
    import plotly.graph_objects as go

    config = inputs.config
    width, height, radius = config.area_width, config.area_height, config.communication_range
    _theorem_header(
        st,
        "TEOREM 1 · RASTGELE GEOMETRİK GRAF",
        "İki İHA'nın bağlantılı olma olasılığı tam olarak hesaplanabilir.",
        "Görev alanı sınırları hesaba katıldığında klasik πr²/(WH) tahmini bağlantıyı abartır.",
    )
    st.latex(
        r"F_{W,H}(r)=\Pr\big(\lVert X-Y\rVert\le r\big)=\frac{\pi WHr^{2}-\tfrac43(W+H)\,r^{3}"
        r"+\tfrac12 r^{4}}{W^{2}H^{2}}\qquad(r\le\min\{W,H\})"
    )
    st.latex(
        r"\mathbb{E}[\deg v]=(n-1)\,F_{W,H}(r),\qquad "
        r"\mathbb{E}\,|E|=\binom{n}{2}\,F_{W,H}(r)"
    )
    with st.expander("İspat ve Lemma 1.1 (yansımalı hareket düzgün dağılımı korur)"):
        st.markdown(
            r"""
**İspat.** $X,Y$ bağımsız ve $[0,W]\times[0,H]$ üzerinde düzgün olsun. $U=|X_1-Y_1|$ rastgele
değişkeninin yoğunluğu $f_U(u)=2(W-u)/W^2$, $V=|X_2-Y_2|$ için $f_V(v)=2(H-v)/H^2$'dir ve $U,V$
bağımsızdır. Böylece

$$F(r)=\frac{4}{W^2H^2}\iint_{u^2+v^2\le r^2}(W-u)(H-v)\,du\,dv .$$

$r\le\min\{W,H\}$ iken bölge çeyrek dairedir. Kutupsal koordinatlarda
$\iint 1=\pi r^2/4$, $\iint u=\iint v=r^3/3$ ve $\iint uv=r^4/8$ bulunur; bunları yerine koymak
formülü verir. $r>\min\{W,H\}$ için bölge dikdörtgenle kırpılır; aynı integral parçalı olarak
kapalı biçimde hesaplanır (`theory.rectangle_distance_cdf`). Beklenen derece, $n-1$ İHA çiftinin
her birinin bağlantı göstergesinin beklenen değerlerinin toplamıdır. $\blacksquare$

**Lemma 1.1.** Başlangıç konumları düzgün, hız yönleri düzgün ve konumdan bağımsızsa, sabit hızlı
yansımalı hareket her adımda düzgün dağılımı korur. *Fikir:* her eksen $2W$ çevreli bir çembere
açılır; orada hareket bir dönmedir ve düzgün dağılım dönmeyle değişmez; çember tekrar $[0,W]$'ye
katlandığında yine düzgün dağılım elde edilir. Bu yüzden Teorem 1 yalnız $t=0$'da değil,
**her adımda** geçerlidir.
            """
        )
    distance_grid = np.linspace(0, hypot(width, height), 240)
    theory_cdf = [rectangle_distance_cdf(value, width, height) for value in distance_grid]
    naive_cdf = np.minimum(1.0, pi * distance_grid**2 / (width * height))
    sample = np.sort(inputs.distances)
    empirical_cdf = np.searchsorted(sample, distance_grid, side="right") / len(sample)

    left, right = st.columns(2)
    figure = go.Figure()
    figure.add_scatter(
        x=distance_grid,
        y=empirical_cdf,
        name="Simülasyon (tüm kareler)",
        line={"color": MINT, "width": 5},
        opacity=0.45,
    )
    figure.add_scatter(
        x=distance_grid, y=theory_cdf, name="Teorem 1", line={"color": AMBER, "width": 2}
    )
    figure.add_scatter(
        x=distance_grid,
        y=naive_cdf,
        name="Sınırsız tahmin πd²/(WH)",
        line={"color": RED, "width": 1.5, "dash": "dash"},
    )
    figure.add_vline(
        x=radius,
        line={"color": "rgba(230,244,242,0.4)", "dash": "dot"},
        annotation_text="r",
        annotation_font_color="#e6f4f2",
    )
    _layout(figure, title="İHA çiftleri arası mesafe dağılımı F(d)")
    figure.update_xaxes(title="d (m)")
    left.plotly_chart(figure, width="stretch")

    theory_degree = expected_degree(config.node_count, width, height, radius)
    naive_degree = naive_expected_degree(config.node_count, width, height, radius)
    steps = np.linspace(0, config.steps, len(inputs.mean_degrees))
    figure = go.Figure()
    figure.add_scatter(
        x=steps,
        y=inputs.mean_degrees,
        name="Gözlenen ortalama derece",
        line={"color": MINT, "width": 1.6},
    )
    figure.add_hline(
        y=theory_degree,
        line={"color": AMBER, "width": 2},
        annotation_text=f"Teorem 1: {theory_degree:.2f}",
        annotation_font_color=AMBER,
    )
    figure.add_hline(
        y=naive_degree,
        line={"color": RED, "dash": "dash"},
        annotation_text=f"πr²/(WH): {naive_degree:.2f}",
        annotation_font_color=RED,
        annotation_position="bottom right",
    )
    _layout(figure, title="Ortalama derece zaman içinde teorik değerin etrafında salınır")
    figure.update_xaxes(title="Zaman adımı")
    right.plotly_chart(figure, width="stretch")
    observed = float(inputs.mean_degrees.mean())
    st.caption(
        f"Gözlenen ortalama {observed:.2f}; Teorem 1 {theory_degree:.2f} "
        f"(göreli fark %{abs(observed - theory_degree) / theory_degree * 100:.1f}); sınır etkisini "
        f"yok sayan tahmin {naive_degree:.2f} (%{(naive_degree / theory_degree - 1) * 100:.1f} fazla)."
    )


def _render_theorem_2(st, inputs: TheoryInputs) -> None:
    import plotly.graph_objects as go

    _theorem_header(
        st,
        "TEOREM 2 · SPEKTRAL ÜST SINIR",
        "Salgının büyüklüğü, ağın spektral yarıçapıyla sınırlanır.",
        "Uyarlamasız her ağ dizisi için geçerli; hareket ve menzil yalnızca λ₁(A(t)) üzerinden etki eder.",
    )
    st.latex(r"\mathbf p(t)\;\le\;M(t)\,\mathbf p(t-1),\qquad M(t)=(1-\gamma)I+\beta A(t)")
    st.latex(
        r"\mathbb{E}[I(t)]\;\le\;\sqrt{n\,I_0}\;\prod_{s=1}^{t}\sigma(s),\qquad "
        r"\sigma(s)=1-\gamma+\beta\,\lambda_1\!\big(A(s)\big)"
    )
    st.latex(
        r"\textbf{Sonuç: }\;\bar\sigma=\Big(\prod_{s=1}^{t}\sigma(s)\Big)^{1/t}<1\;\Longrightarrow\;"
        r"\mathbb{E}[I(t)]\le\sqrt{nI_0}\,\bar\sigma^{\,t}\xrightarrow[t\to\infty]{}0;"
        r"\qquad\text{statik ağda: }\frac{\beta}{\gamma}<\frac{1}{\lambda_1(A)}"
    )
    with st.expander("İspat (dört adım)"):
        st.markdown(
            r"""
1. **Birleşim sınırı.** $p_i(t)=\Pr(i \text{ enfekte})$ olsun. $i$ ya enfekteydi ve iyileşmedi
   ($(1-\gamma)p_i(t-1)$), ya da en az bir enfekte komşusundan bulaştı. İkinci olay için
   $\Pr\big(\bigcup_j B_j\big)\le\sum_j\Pr(B_j)=\beta\sum_j A_{ij}(t)\,p_j(t-1)$.
   Böylece $\mathbf p(t)\le M(t)\,\mathbf p(t-1)$ (bileşen bazında).
2. **Tümevarım.** $M(t)$'nin bütün girdileri negatif değildir, dolayısıyla sırayı korur:
   $\mathbf x\le\mathbf y\Rightarrow M\mathbf x\le M\mathbf y$. Buradan
   $\mathbf p(t)\le M(t)\cdots M(1)\,\mathbf p(0)$.
3. **Cauchy–Schwarz.** $\mathbb E[I(t)]=\mathbf 1^{\top}\mathbf p(t)\le\sqrt n\,\lVert M(t)\cdots M(1)\mathbf p(0)\rVert_2$
   ve $\lVert\mathbf p(0)\rVert_2=\sqrt{I_0}$.
4. **Perron–Frobenius.** $M(s)$ simetrik ve negatif olmayan girdili olduğundan
   $\lVert M(s)\rVert_2=\rho(M(s))=1-\gamma+\beta\lambda_1(A(s))=\sigma(s)$; matris normu
   çarpımsal alt-sınırlı olduğu için $\lVert\prod M(s)\rVert_2\le\prod\sigma(s)$. $\blacksquare$

Sabit bir $A$ için $\sigma<1 \iff \beta\lambda_1<\gamma$: klasik epidemik eşik
(Wang ve ark., 2003). Zamanla değişen ağlarda eşiği çarpım matrisinin özdeğeriyle veren sonuç
Prakash ve ark. (2010) tarafından verilmiştir; buradaki biçim daha kabadır ama her karenin
$\lambda_1$ değerinden doğrudan hesaplanır ve sonlu zaman için açık bir sayı verir
(**Kaynaklar** sekmesi).
            """
        )
    steps = np.arange(len(inputs.monte_carlo))
    figure = go.Figure()
    figure.add_scatter(
        x=np.concatenate([steps, steps[::-1]]),
        y=np.concatenate([inputs.monte_carlo_high, inputs.monte_carlo_low[::-1]]),
        fill="toself",
        fillcolor="rgba(94,234,212,0.12)",
        line={"width": 0},
        name="Monte Carlo %10–%90",
        hoverinfo="skip",
    )
    figure.add_scatter(
        x=steps,
        y=inputs.monte_carlo,
        name=f"Monte Carlo ortalaması ({inputs.replicates} koşu)",
        line={"color": MINT, "width": 3},
    )
    figure.add_scatter(
        x=steps,
        y=inputs.mean_field,
        name="Ortalama alan (NIMFA)",
        line={"color": VIOLET, "width": 2, "dash": "dot"},
    )
    figure.add_scatter(
        x=steps,
        y=inputs.linear_bound,
        name="Doğrusal üst sınır Πₛ M(s)·p(0)",
        line={"color": CYAN, "width": 2},
    )
    figure.add_scatter(
        x=steps,
        y=inputs.spectral_bound,
        name="Teorem 2: √(nI₀)·Π σ(s)",
        line={"color": AMBER, "width": 2.4},
    )
    _layout(figure, height=420, title="Beklenen enfekte sayısı ve üst sınırlar (log ölçek)")
    figure.update_yaxes(type="log", title="İHA sayısı")
    figure.update_xaxes(title="Zaman adımı")
    st.plotly_chart(figure, width="stretch")

    figure = go.Figure()
    figure.add_bar(
        x=steps[1:],
        y=inputs.spread_factor,
        marker_color=[RED if value >= 1 else MINT for value in inputs.spread_factor],
        name="σ(t)",
    )
    figure.add_hline(
        y=1,
        line={"color": AMBER, "dash": "dash"},
        annotation_text="σ = 1",
        annotation_font_color=AMBER,
    )
    figure.add_hline(
        y=inputs.geometric_mean,
        line={"color": "#e6f4f2", "width": 1},
        annotation_text=f"σ̄ = {inputs.geometric_mean:.3f}",
        annotation_position="bottom right",
        annotation_font_color="#e6f4f2",
    )
    _layout(
        figure,
        height=260,
        title="Her adımın spektral baskısı σ(t) = 1 − γ + β·λ₁(A(t))",
        showlegend=False,
    )
    st.plotly_chart(figure, width="stretch")
    violations = int(np.sum(inputs.monte_carlo > inputs.linear_bound + 1e-9))
    st.caption(
        "Simülasyon ortalaması her adımda iki sınırın da altında kalır "
        f"(ihlal: {violations}). Doğrusal sınır yakın erimde sıkıdır; spektral sınır ise "
        "tek bir sayıyla (σ̄) sönüm hakkında kesin hüküm verir."
    )


def _render_proposition_3(st, inputs: TheoryInputs) -> None:
    import plotly.graph_objects as go

    _theorem_header(
        st,
        "ÖNERME 3 · BULAŞ SINIRI",
        "Bir adımda beklenen yeni enfeksiyon, S–I kenar sayısıyla sıkıştırılır.",
        "Savunma neden bulaş kanallarını (sağlıklı–enfekte kenarlarını) kesmeli: tam bu nicelik.",
    )
    st.latex(
        r"\beta\,|\partial I|-\beta^{2}\sum_{i\in S}\binom{k_i}{2}\;\le\;"
        r"\mathbb{E}\big[\Delta I^{+}\,\big|\,X\big]=\sum_{i\in S}\Big(1-(1-\beta)^{k_i}\Big)"
        r"\;\le\;\beta\,|\partial I|"
    )
    with st.expander("İspat"):
        st.markdown(
            r"""
$k_i$, sağlıklı $i$ İHA'sının enfekte komşu sayısıdır ve $|\partial I|=\sum_{i\in S}k_i$.
Bernoulli eşitsizliği $(1-\beta)^{k}\ge 1-k\beta$ üst sınırı, Bonferroni eşitsizliği
$(1-\beta)^{k}\le 1-k\beta+\binom{k}{2}\beta^{2}$ alt sınırı verir. Toplama işlemi
sonucu tamamlar. $\blacksquare$ Önerme, adaptif savunmalar için bile geçerlidir; çünkü yalnızca
o anki duruma koşulludur.
            """
        )
    steps = np.arange(1, len(inputs.new_infections) + 1)
    figure = go.Figure()
    figure.add_scatter(
        x=steps, y=inputs.upper_new, name="Üst sınır β|∂I|", line={"color": AMBER, "width": 2}
    )
    figure.add_scatter(
        x=steps, y=inputs.expected_new, name="Koşullu beklenti", line={"color": MINT, "width": 3}
    )
    figure.add_scatter(
        x=steps,
        y=inputs.new_infections,
        name="Gerçekleşen yeni enfeksiyon",
        mode="markers",
        marker={"color": RED, "size": 5},
    )
    figure.add_scatter(
        x=steps,
        y=inputs.lower_new,
        name="Alt sınır (Bonferroni)",
        line={"color": CYAN, "width": 1.6, "dash": "dot"},
    )
    _layout(figure, height=340, title="Adım başına yeni enfeksiyon (Monte Carlo ortalaması)")
    figure.update_xaxes(title="Zaman adımı")
    st.plotly_chart(figure, width="stretch")


def _render_lemma_4(st, config: SimulationConfig) -> None:
    from plotly.subplots import make_subplots

    _theorem_header(
        st,
        "LEMMA 4 · RAYLEIGH SINIRLARI",
        "Tek bir müdahalenin özdeğerlere etkisi, özvektörlerle önceden sınırlanır.",
        "Spektral Kalkan savunması bu dört eşitsizlikten türetilmiştir.",
    )
    st.latex(
        r"\lambda_1(A-E_{ij})\ge\lambda_1-2u_iu_j,\qquad \lambda_1(A+E_{ij})\ge\lambda_1+2u_iu_j"
    )
    st.latex(
        r"\lambda_1(A_{-i})\ge\lambda_1\,(1-2u_i^{2}),\qquad "
        r"\lambda_2(L+L_{ij})\le\lambda_2+(v_i-v_j)^{2}"
    )
    with st.expander("İspat ve Spektral Kalkan algoritması"):
        st.markdown(
            r"""
**İspat.** Rayleigh bölümü: $\lambda_1(A)=\max_{\lVert x\rVert=1}x^{\top}Ax$ ve
$\lambda_2(L)=\min_{x\perp\mathbf 1,\ \lVert x\rVert=1}x^{\top}Lx$. Değiştirilmiş matrise
sırasıyla $x=u$ (Perron vektörü) ve $x=v$ (Fiedler vektörü) koymak yeterlidir:
$u^{\top}(A\pm E_{ij})u=\lambda_1\pm2u_iu_j$, $u^{\top}A_{-i}u=\lambda_1-2u_i(Au)_i=\lambda_1(1-2u_i^2)$,
$v^{\top}(L+L_{ij})v=\lambda_2+(v_i-v_j)^2$. Maksimum her test vektöründeki değerden büyük,
minimum ise küçük olduğundan eşitsizlikler çıkar. $\blacksquare$
            """
        )
        st.code(
            "Spektral Kalkan (her adımda, bütçe B):\n"
            "  1. Bilinen enfekte İHA'ları u_i'ye göre sırala; ilk B tanesini izole et\n"
            "     (Lemma 4: λ₁ en fazla 2·λ₁·u_i² düşer → Teorem 2'deki σ(t) küçülür)\n"
            "  2. Kalan bütçe ile sağlıklı bağlantı ekle:\n"
            "       kopuk bileşenleri birleştiren bağlantılar önce,\n"
            "       sonra puan = (v_i − v_j)² / maks  −  κ · 2·u_i·u_j / maks  (> 0 ise)\n"
            "       menzil ≤ çarpan·r ve derece ≤ azami derece kısıtlarıyla",
            language=None,
        )
    frames = cached_simulation(undefended(config))
    frame_index = st.slider(
        "Analiz edilen kare", 0, len(frames) - 1, len(frames) // 2, key="lemma-frame"
    )
    check = perturbation_check(
        adjacency_from_edges(len(frames[0].positions), frames[frame_index].edges)
    )
    panels = (
        ("Kenar kesme: Δλ₁ ≥ −2uᵢuⱼ", check.edge_removal, RED),
        ("İzolasyon: Δλ₁ ≥ −2λ₁uᵢ²", check.node_isolation, AMBER),
        ("Bağlantı maliyeti: Δλ₁ ≥ 2uᵢuⱼ", check.link_cost, VIOLET),
        ("Bağlantı kazancı: Δλ₂ ≤ (vᵢ−vⱼ)²", check.link_gain, MINT),
    )
    figure = make_subplots(rows=1, cols=4, subplot_titles=[title for title, _, _ in panels])
    violations = 0
    for column, (title, data, color) in enumerate(panels, start=1):
        if len(data.bound):
            low = float(min(data.bound.min(), data.exact.min()))
            high = float(max(data.bound.max(), data.exact.max()))
            figure.add_scatter(
                x=[low, high],
                y=[low, high],
                mode="lines",
                line={"color": "rgba(230,244,242,0.35)", "dash": "dash"},
                showlegend=False,
                row=1,
                col=column,
            )
            figure.add_scatter(
                x=data.bound,
                y=data.exact,
                mode="markers",
                marker={"color": color, "size": 6, "opacity": 0.8},
                name=title,
                showlegend=False,
                row=1,
                col=column,
            )
        sign = 1 if column < 4 else -1
        violations += int(np.sum(sign * (data.exact - data.bound) < -1e-9))
    _layout(figure, height=330)
    figure.update_xaxes(title_text="Lemma 4 sınırı")
    figure.update_yaxes(title_text="Gerçek değişim", col=1)
    st.plotly_chart(figure, width="stretch")
    total = sum(len(data.bound) for _, data, _ in panels)
    st.caption(
        f"{len(check.nodes)} İHA'lık en büyük bileşende {total} müdahale tek tek hesaplandı; "
        f"eşitsizliği ihlal eden müdahale sayısı: {violations}. Noktalar kesikli y = x çizgisinin "
        "doğru tarafında kalır; yakınlık, birinci mertebe tahminin ne kadar isabetli olduğunu gösterir."
    )


def _render_phase_diagram(st, inputs: TheoryInputs) -> None:
    import plotly.graph_objects as go

    _theorem_header(
        st,
        "FAZ DİYAGRAMI · TEORİ VE SİMÜLASYON",
        "Teorem 2'nin eşik eğrisi, salgının söndüğü bölgeyi önceden çizer.",
        "Isı haritası simülasyonun uzun dönem enfeksiyonu; sarı eğri β*(γ) sınırı.",
    )
    if not st.button("Faz diyagramını hesapla", key="phase-run", type="primary"):
        st.caption("14 × 14 parametre ızgarası, hücre başına 24 koşu; birkaç saniye sürer.")
        return
    config = inputs.config
    frames = cached_simulation(config)
    betas = np.linspace(0.01, 0.5, 14)
    gammas = np.linspace(0.02, 0.5, 14)
    with st.spinner("196 parametre hücresi simüle ediliyor…"):
        diagram = phase_diagram(
            adjacency_sequence(frames),
            initial_vector(frames),
            betas,
            gammas,
            replicates=24,
            seed=config.seed,
        )
    figure = go.Figure()
    figure.add_heatmap(
        x=betas,
        y=gammas,
        z=diagram.endemic_level,
        colorscale="Inferno",
        colorbar={"title": "Enfekte<br>oranı"},
        zmin=0,
        zmax=1,
    )
    curve = np.minimum(diagram.threshold_betas, 0.5)
    figure.add_scatter(
        x=curve,
        y=gammas,
        mode="lines+markers",
        name="Teorem 2 eşiği β*(γ)",
        line={"color": AMBER, "width": 3},
    )
    _layout(figure, height=440, title="Eğrinin solunda (β < β*) sönüm matematiksel olarak garanti")
    figure.update_xaxes(title="β (bulaş olasılığı)")
    figure.update_yaxes(title="γ (iyileşme olasılığı)")
    st.plotly_chart(figure, width="stretch")
    safe = diagram.endemic_level[np.asarray(betas)[None, :] < diagram.threshold_betas[:, None]]
    st.caption(
        f"Eşiğin altındaki {safe.size} hücrede ortalama uzun dönem enfeksiyon "
        f"%{(safe.mean() if safe.size else 0) * 100:.2f}. Sınır yeterli koşuldur: gerçek geçiş "
        "eğrinin biraz sağında gerçekleşir, çünkü ispat en kötü durumu varsayar."
    )


def _render_threshold(st, inputs: TheoryInputs) -> None:
    _theorem_header(
        st,
        "EŞİK SIKILIĞI · TEOREM 2 NE KADAR KESKİN?",
        "Garanti β* değerinde biter; salgın bundan ne kadar sonra gerçekten başlıyor?",
        f"β, eşiğin katları olarak taranır; savunmasız sürü her noktada {SWEEP_HORIZON} adım "
        "boyunca yeniden simüle edilir.",
    )
    with st.spinner("Eşik taraması yapılıyor…"):
        sweep = compute_threshold_sweep(inputs.config)
    threshold, tightness = float(sweep["threshold_beta"]), sweep["tightness"]
    ratio = inputs.config.beta / threshold if threshold else float("inf")
    columns = st.columns(4)
    columns[0].metric("Teorem 2 eşiği β*", f"{threshold:.4f}")
    columns[1].metric(
        "Gözlenen eşik",
        f"{sweep['empirical_beta']:.4f}" if tightness else "—",
        help=f"Uzun dönem enfekte oranının %{ENDEMIC_LEVEL * 100:.0f} düzeyini geçtiği ilk β.",
    )
    columns[2].metric(
        "Sıkılık oranı",
        f"×{tightness:.2f}" if tightness else "> ×8",
        help="Gözlenen eşik / β*. 1'e ne kadar yakınsa Teorem 2 o kadar keskin.",
    )
    columns[3].metric(
        "Senaryonun konumu",
        f"×{ratio:.1f}",
        "eşik altı" if ratio < 1 else "eşik üstü",
        delta_color="normal" if ratio < 1 else "inverse",
    )
    left, right = st.columns(2)
    left.plotly_chart(
        scenario_threshold_figure(sweep, SWEEP_MULTIPLIERS, inputs.config.beta, ENDEMIC_LEVEL),
        width="stretch",
    )
    findings = load_findings()
    right.plotly_chart(tightness_figure(findings), width="stretch")
    onsets = [float(item["tightness"]) for item in findings["thresholds"] if item["tightness"]]
    below = max(float(item["level_below_threshold"]) for item in findings["thresholds"])
    st.caption(
        f"Solda aktif senaryo: {sweep['replicates']} koşu/nokta, {SWEEP_HORIZON} adımın son üçte "
        f"birindeki ortalama enfekte oranı; noktalı çizgi %{ENDEMIC_LEVEL * 100:.0f} düzeyi. "
        f"Buradaki β* {SWEEP_HORIZON} adımlık hareketten hesaplandığı için üstteki değerden biraz "
        f"farklı olabilir. Sağda yedi hazır senaryo: gözlenen eşik β*'ın ×{min(onsets):.2f}–"
        f"×{max(onsets):.2f} katında ve sürü yoğunlaştıkça (λ₁ büyüdükçe) 1'e yaklaşıyor. Eşiğin "
        f"altındaki en yüksek uzun dönem düzey %{below * 100:.1f}: garanti hiçbir senaryoda "
        "bozulmuyor. Aradaki boşluk ispatın bedelidir (birleşim sınırı ve Cauchy–Schwarz) ve "
        "küçük sürülerde salgının rastlantıyla sönmesinden büyür."
    )
    with st.expander("Senaryo bazında eşik tablosu"):
        st.dataframe(
            [
                {
                    "Senaryo": item["title"],
                    "n": item["node_count"],
                    "γ": item["gamma"],
                    "ortalama λ₁": item["mean_spectral_radius"],
                    "β* (Teorem 2)": item["threshold_beta"],
                    "gözlenen eşik": item["empirical_beta"],
                    "oran": item["tightness"],
                }
                for item in findings["thresholds"]
            ],
            hide_index=True,
            width="stretch",
        )


REFERENCES = (
    (
        "Teorem 1",
        (
            "B. Ghosh (1951). *Random distances within a rectangle and between two rectangles.* "
            "Bull. Calcutta Math. Soc. 43, 17–24."
        ),
        (
            "Dikdörtgende iki rastgele nokta arasındaki mesafenin dağılımı. Teorem 1 bu klasik "
            "sonucun haberleşme menziline uygulanmış biçimidir."
        ),
    ),
    (
        "Lemma 1.1",
        (
            "P. Nain, D. Towsley, B. Liu, Z. Liu (2005). *Properties of random direction models.* "
            "IEEE INFOCOM, 1897–1907."
        ),
        "Yansımalı rastgele yön hareketinde düzgün dağılımın korunması.",
    ),
    (
        "Teorem 2 · statik eşik",
        (
            "Y. Wang, D. Chakrabarti, C. Wang, C. Faloutsos (2003). *Epidemic spreading in real "
            "networks: an eigenvalue viewpoint.* SRDS, 25–34."
        ),
        "Sabit ağda epidemik eşik 1/λ₁(A).",
    ),
    (
        "Ortalama alan",
        (
            "P. Van Mieghem, J. Omic, R. Kooij (2009). *Virus spread in networks.* IEEE/ACM "
            "Trans. Networking 17(1), 1–14."
        ),
        "Grafiklerdeki NIMFA eğrisinin kaynağı (N-intertwined ortalama alan yaklaşımı).",
    ),
    (
        "Teorem 2 · değişen ağ",
        (
            "B. A. Prakash, H. Tong, N. Valler, M. Faloutsos, C. Faloutsos (2010). *Virus "
            "propagation on time-varying networks: theory and immunization algorithms.* "
            "ECML PKDD, LNCS 6323, 99–114."
        ),
        (
            "Zamanla değişen ağlarda eşik, sistem matrislerinin çarpımının en büyük özdeğeriyle "
            "verilir."
        ),
    ),
    (
        "Lemma 4 · λ₁",
        (
            "H. Tong ve ark. (2010). *On the vulnerability of large graphs.* ICDM; "
            "H. Tong ve ark. (2012). *Gelling, and melting, large graphs by edge manipulation.* "
            "CIKM, 245–254."
        ),
        "λ₁'i düşürmek için düğüm ve kenar seçiminde özvektör puanları (uᵢ², uᵢuⱼ).",
    ),
    (
        "Lemma 4 · λ₂",
        "A. Ghosh, S. Boyd (2006). *Growing well-connected graphs.* IEEE CDC, 6605–6611.",
        (
            "Cebirsel bağlantısallığı artırmak için Fiedler vektörüne dayalı kenar ekleme, "
            "(vᵢ − vⱼ)² puanı."
        ),
    ),
)

CONTRIBUTIONS = (
    (
        "Sonlu zamanlı, açık sabitli sınır",
        (
            "Teorem 2 yalnızca bir eşik değil, her t için hesaplanabilen bir sayı verir: "
            "E[I(t)] ≤ √(nI₀)·Πσ(s). Periyodiklik varsayımı yoktur; uyarlamasız her ağ dizisinde "
            "geçerlidir ve ispatı dört adımda kendi içinde tamamdır."
        ),
    ),
    (
        "Hareket modeliyle birleştirme ve sıkılık ölçümü",
        (
            "Teorem 1 ve Lemma 1.1 sürünün her adımdaki beklenen derecesini kesin verir. "
            "Teorem 2'nin eşiği yedi farklı sürüde uzun ufuklu simülasyonla karşılaştırılmış; "
            "gözlenen eşiğin β*'ın kaç katında kaldığı ve yoğunlukla nasıl değiştiği ölçülmüştür "
            "(Eşik sıkılığı sekmesi)."
        ),
    ),
    (
        "Spektral Kalkan",
        (
            "Perron ağırlıklı karantina ile Fiedler kazançlı onarım tek bir adım bütçesinde, "
            "kusurlu tespit ve kalıcı müdahale altında birleştirilmiştir."
        ),
    ),
    (
        "Adil kontroller ve açık sınırlar",
        (
            "Her bileşenin katkısı kendi kontrol grubuyla ayrıştırılır (rastgele ekleme, rastgele "
            "karantina; eşleştirilmiş seed, Holm düzeltmesi). Olumsuz sonuçlar da raporlanır: bütçe "
            "bolken sıralama fark yaratmaz, GTAD yayılımı düşürmez, Teorem 2 uyarlamalı savunmada "
            "geçerli değildir."
        ),
    ),
)


def _render_references(st) -> None:
    _theorem_header(
        st,
        "KAYNAKLAR VE ÖZGÜNLÜK",
        "Hangi sonuç literatürden, hangisi bu projeden?",
        "Teoremlerin dayandığı bilinen sonuçlar ve projenin bunların üzerine eklediği katkı.",
    )
    known, new = st.columns([1.15, 1], gap="large")
    with known:
        st.markdown("##### Dayandığımız sonuçlar")
        for label, citation, role in REFERENCES:
            with st.container(border=True):
                st.markdown(
                    f'<span class="sg-card-title">{label.upper()}</span>', unsafe_allow_html=True
                )
                st.markdown(citation)
                st.caption(role)
    with new:
        st.markdown("##### Bu projenin katkısı")
        for index, (title, body) in enumerate(CONTRIBUTIONS, start=1):
            with st.container(border=True):
                st.markdown(
                    f'<span class="sg-card-title">KATKI {index}</span>', unsafe_allow_html=True
                )
                st.markdown(f"**{title}**")
                st.caption(body)


def render_theory_lab(st, config: SimulationConfig) -> None:
    with st.spinner("Teorem hesapları yapılıyor…"):
        inputs = compute_theory(config)
    _render_intro(st, inputs)
    sections = st.tabs(
        [
            "Teorem 1 · Bağlantı",
            "Teorem 2 · Spektral sınır",
            "Önerme 3 · Bulaş",
            "Lemma 4 · Pertürbasyon",
            "Eşik sıkılığı",
            "Faz diyagramı",
            "Kaynaklar",
        ]
    )
    with sections[0]:
        _render_theorem_1(st, inputs)
    with sections[1]:
        _render_theorem_2(st, inputs)
    with sections[2]:
        _render_proposition_3(st, inputs)
    with sections[3]:
        _render_lemma_4(st, config)
    with sections[4]:
        _render_threshold(st, inputs)
    with sections[5]:
        _render_phase_diagram(st, inputs)
    with sections[6]:
        _render_references(st)
