from __future__ import annotations

from dataclasses import dataclass
from html import escape

from ...experiments import RESULT_METRICS
from ..error_states import render_empty_state
from .comparison_panel import baseline_method, build_comparison_rows
from .experiment_center import EXPERIMENT_LABELS, METHOD_LABELS, METRIC_LABELS


@dataclass(frozen=True, slots=True)
class ReportDocument:
    experiment_id: str
    title: str
    author: str
    note: str
    kind: str
    run_count: int
    seed_count: int
    baseline: str
    best_security_method: str
    best_connectivity_method: str
    fingerprint: str


def build_report_document(
    result: dict[str, object],
    *,
    title: str = "SwarmGuard Deney Raporu",
    author: str = "SwarmGuard Araştırma Ekibi",
    note: str = "",
) -> ReportDocument:
    security = build_comparison_rows(result, "mean_infected_ratio")[0]
    connectivity = build_comparison_rows(result, "mean_largest_component_ratio")[0]
    return ReportDocument(
        experiment_id=str(result["experiment_id"]),
        title=title.strip() or "SwarmGuard Deney Raporu",
        author=author.strip() or "SwarmGuard Araştırma Ekibi",
        note=note.strip(),
        kind=str(result["kind"]),
        run_count=int(result["run_count"]),
        seed_count=len(result["seeds"]),
        baseline=baseline_method(result),
        best_security_method=security.method,
        best_connectivity_method=connectivity.method,
        fingerprint=str(result["manifest"]["fingerprint"]),
    )


def _format_number(value: object) -> str:
    number = float(value)
    return f"{number:.4f}"


def _summary_table_markdown(result: dict[str, object]) -> str:
    headers = ["Yöntem", *[METRIC_LABELS[metric] for metric in RESULT_METRICS]]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for summary in result["summaries"]:
        method = str(summary["method"])
        values = [_format_number(summary["metrics"][metric]["mean"]) for metric in RESULT_METRICS]
        lines.append("| " + " | ".join([METHOD_LABELS.get(method, method), *values]) + " |")
    return "\n".join(lines)


def _paired_table_markdown(result: dict[str, object]) -> str:
    comparisons = result["paired_comparisons"]
    if not comparisons:
        return "Bu deneyde eşleştirilmiş baseline karşılaştırması bulunmuyor."
    lines = [
        "| Yöntem | Eşleşme | Ortalama enfeksiyon farkı | Ağ verimliliği farkı | Müdahale maliyeti farkı |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for comparison in comparisons:
        method = str(comparison["method"])
        deltas = comparison["mean_deltas"]
        lines.append(
            "| "
            + " | ".join(
                [
                    METHOD_LABELS.get(method, method),
                    str(comparison["pair_count"]),
                    _format_number(deltas["mean_infected_ratio"]),
                    _format_number(deltas["mean_global_efficiency"]),
                    _format_number(deltas["total_intervention_cost"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def report_to_markdown(document: ReportDocument, result: dict[str, object]) -> bytes:
    scenario = result["scenario"]
    note = f"\n## Araştırmacı Notu\n\n{document.note}\n" if document.note else ""
    content = f"""# {document.title}

**Hazırlayan:** {document.author}  
**Deney kimliği:** `{document.experiment_id}`  
**Deney türü:** {EXPERIMENT_LABELS[document.kind]}  
**Manifest parmak izi:** `{document.fingerprint}`

## Yönetici Özeti

Bu rapor {document.seed_count} eşleştirilmiş seed üzerinde yürütülen {document.run_count} koşuyu özetler.
Ortalama enfeksiyon oranında en iyi gözlenen yöntem **{METHOD_LABELS.get(document.best_security_method, document.best_security_method)}**,
ortalama büyük bileşen oranında en iyi gözlenen yöntem **{METHOD_LABELS.get(document.best_connectivity_method, document.best_connectivity_method)}** olmuştur.
Referans yöntem **{METHOD_LABELS.get(document.baseline, document.baseline)}** olarak alınmıştır.

> Bu sıralamalar gözlenen örneklem ortalamalarını gösterir; tek başına istatistiksel anlamlılık iddiası değildir.

## Senaryo

- İHA sayısı: {scenario["node_count"]}
- Simülasyon adımı: {scenario["steps"]}
- Görev alanı: {scenario["area_width"]} × {scenario["area_height"]} m
- Haberleşme menzili: {scenario["communication_range"]} m
- Bulaşma / iyileşme: β={scenario["beta"]} / γ={scenario["gamma"]}
- Saldırı stratejisi: {scenario["attack_strategy"]}
- Seed kümesi: {", ".join(map(str, result["seeds"]))}

## Yöntem Sonuçları

Tablodaki değerler yöntem ortalamalarıdır. Ayrıntılı dağılım ve iki taraflı %95 Student-t güven aralıkları uygulamadaki karşılaştırma ekranında bulunur.

{_summary_table_markdown(result)}

## Baseline'a Göre Eşleştirilmiş Farklar

Farklar `yöntem - baseline` biçimindedir ve aynı seed sonuçları eşleştirilmiştir.

{_paired_table_markdown(result)}
{note}
## Tekrarlanabilirlik

- Yazılım: swarmguard {result["manifest"]["software"]["version"]}
- Şema: {result["manifest"]["schema_version"]}
- Eşleştirme anahtarı: seed
- Güven aralığı: iki taraflı %95 Student-t
- Deney kimliği: `{document.experiment_id}`
- SHA-256: `{document.fingerprint}`
"""
    return content.encode("utf-8")


def report_to_html(document: ReportDocument, result: dict[str, object]) -> bytes:
    scenario = result["scenario"]
    summary_rows = "".join(
        "<tr><td>"
        + escape(METHOD_LABELS.get(str(summary["method"]), str(summary["method"])))
        + "</td>"
        + "".join(
            f"<td>{_format_number(summary['metrics'][metric]['mean'])}</td>"
            for metric in RESULT_METRICS
        )
        + "</tr>"
        for summary in result["summaries"]
    )
    header_cells = "".join(f"<th>{escape(METRIC_LABELS[metric])}</th>" for metric in RESULT_METRICS)
    note = (
        f"<section><h2>Araştırmacı Notu</h2><p>{escape(document.note)}</p></section>"
        if document.note
        else ""
    )
    html = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(document.title)}</title><style>
body{{margin:0;background:#071216;color:#dceae8;font:14px Arial,sans-serif;line-height:1.6}}main{{max-width:1180px;margin:auto;padding:48px 32px}}header{{padding:36px;border:1px solid #244047;border-radius:18px;background:#0b1c21}}small{{color:#57e7d6;letter-spacing:.14em}}h1{{margin:.35rem 0;font-size:38px}}h2{{margin-top:36px;color:#9aeee4}}p,li{{color:#91a8ad}}.meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:20px 0}}.meta div{{padding:14px;border:1px solid #20383e;border-radius:10px}}.meta b{{display:block;color:#668087;font-size:10px;letter-spacing:.1em}}table{{width:100%;border-collapse:collapse;font-size:12px}}th,td{{padding:10px;border:1px solid #20383e;text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{color:#789097;background:#0c1d22}}code{{color:#9aeee4;word-break:break-all}}blockquote{{margin:20px 0;padding:12px 18px;border-left:3px solid #57e7d6;background:#0b1c21;color:#91a8ad}}@media print{{body{{background:white;color:#111}}main{{max-width:none;padding:16px}}header,th{{background:#f4f7f7}}p,li{{color:#333}}}}
</style></head><body><main><header><small>SWARMGUARD · ARAŞTIRMA RAPORU</small><h1>{escape(document.title)}</h1><p>{escape(document.author)}</p><code>{escape(document.fingerprint)}</code></header>
<div class="meta"><div><b>DENEY</b>{escape(document.experiment_id)}</div><div><b>TÜR</b>{escape(EXPERIMENT_LABELS[document.kind])}</div><div><b>KOŞU</b>{document.run_count}</div><div><b>SEED</b>{document.seed_count}</div></div>
<section><h2>Yönetici Özeti</h2><p>Enfeksiyon kontrolünde en iyi gözlenen yöntem <strong>{escape(METHOD_LABELS.get(document.best_security_method, document.best_security_method))}</strong>; bağlantısallıkta en iyi gözlenen yöntem <strong>{escape(METHOD_LABELS.get(document.best_connectivity_method, document.best_connectivity_method))}</strong>. Referans yöntem: <strong>{escape(METHOD_LABELS.get(document.baseline, document.baseline))}</strong>.</p><blockquote>Bu sıralamalar gözlenen örneklem ortalamalarını gösterir; tek başına istatistiksel anlamlılık iddiası değildir.</blockquote></section>
<section><h2>Senaryo</h2><ul><li>{scenario["node_count"]} İHA, {scenario["steps"]} adım</li><li>Alan: {scenario["area_width"]} × {scenario["area_height"]} m</li><li>Menzil: {scenario["communication_range"]} m</li><li>β={scenario["beta"]} · γ={scenario["gamma"]}</li><li>Seed: {escape(", ".join(map(str, result["seeds"])))}</li></ul></section>
<section><h2>Yöntem Ortalamaları</h2><div style="overflow:auto"><table><thead><tr><th>Yöntem</th>{header_cells}</tr></thead><tbody>{summary_rows}</tbody></table></div></section>{note}
<section><h2>Tekrarlanabilirlik</h2><p>SwarmGuard {escape(str(result["manifest"]["software"]["version"]))} · Şema {escape(str(result["manifest"]["schema_version"]))} · İki taraflı %95 Student-t güven aralığı.</p><code>{escape(document.fingerprint)}</code></section>
</main></body></html>"""
    return html.encode("utf-8")


def render_report_center(st, history: list[dict[str, object]]) -> None:
    st.markdown(
        """
        <section class="sg-report-hero">
            <div><span>RAPOR MERKEZİ</span><h2>Deneyden paylaşılabilir araştırma çıktısına.</h2></div>
            <p>Sonuçları, senaryo sözleşmesini ve tekrarlanabilirlik kimliğini tek bir raporda birleştir; tarayıcıda açılabilen HTML veya düzenlenebilir Markdown olarak dışa aktar.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if not history:
        render_empty_state(
            st,
            icon="▤",
            title="Raporlanacak deney bulunamadı",
            message="Rapor oluşturmak için önce Deney Merkezi'nde bir deney çalıştır.",
            action_label="Deney Merkezi'ne git",
            action_href="experiments",
        )
        return

    ids = [str(result["experiment_id"]) for result in history]
    selected_id = st.selectbox(
        "Raporlanacak deney",
        options=ids,
        format_func=lambda experiment_id: next(
            f"{EXPERIMENT_LABELS[str(item['kind'])]} · {item['run_count']} koşu · {experiment_id}"
            for item in history
            if item["experiment_id"] == experiment_id
        ),
        key="report-experiment",
    )
    result = next(item for item in history if str(item["experiment_id"]) == selected_id)
    title_column, author_column = st.columns(2)
    title = title_column.text_input("Rapor başlığı", "SwarmGuard Deney Raporu")
    author = author_column.text_input("Hazırlayan", "SwarmGuard Araştırma Ekibi")
    note = st.text_area(
        "Araştırmacı notu",
        placeholder="Deney bağlamı, yorum veya sonraki çalışma notu…",
        height=90,
    )
    document = build_report_document(result, title=title, author=author, note=note)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Deney", document.experiment_id)
    metric_columns[1].metric("Koşu", document.run_count)
    metric_columns[2].metric("Seed", document.seed_count)
    metric_columns[3].metric("Baseline", METHOD_LABELS.get(document.baseline, document.baseline))

    st.markdown("##### Rapor önizleme")
    st.markdown(
        f"""
        <section class="sg-report-preview">
            <small>SWARMGUARD · {EXPERIMENT_LABELS[document.kind].upper()}</small>
            <h3>{escape(document.title)}</h3><p>{escape(document.author)}</p>
            <div><span>GÜVENLİK LİDERİ</span><strong>{escape(METHOD_LABELS.get(document.best_security_method, document.best_security_method))}</strong></div>
            <div><span>BAĞLANTISALLIK LİDERİ</span><strong>{escape(METHOD_LABELS.get(document.best_connectivity_method, document.best_connectivity_method))}</strong></div>
            <code>{escape(document.fingerprint)}</code>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Rapor, gözlenen ortalamaları bilimsel anlamlılık iddiasından ayırır ve deney manifestinin "
        "SHA-256 parmak izini içerir."
    )

    markdown_data = report_to_markdown(document, result)
    html_data = report_to_html(document, result)
    markdown_column, html_column, info_column = st.columns([1, 1, 2.5], vertical_alignment="center")
    markdown_column.download_button(
        "Markdown indir",
        markdown_data,
        file_name=f"swarmguard-{document.experiment_id}-report.md",
        mime="text/markdown",
        width="stretch",
    )
    html_column.download_button(
        "HTML indir",
        html_data,
        file_name=f"swarmguard-{document.experiment_id}-report.html",
        mime="text/html",
        width="stretch",
    )
    info_column.caption(
        "HTML raporu doğrudan tarayıcıda açabilir veya yazdır menüsünden PDF olarak kaydedebilirsin."
    )

    with st.expander("Markdown rapor içeriği"):
        st.code(markdown_data.decode("utf-8"), language="markdown")
