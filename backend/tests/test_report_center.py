from swarmguard.config import DefenseStrategy, SimulationConfig
from swarmguard.dashboard.components.report_center import (
    build_report_document,
    report_to_html,
    report_to_markdown,
)
from swarmguard.experiments import run_monte_carlo


def sample_result() -> dict[str, object]:
    return run_monte_carlo(
        SimulationConfig(node_count=8, steps=2, speed=0),
        (DefenseStrategy.NONE, DefenseStrategy.GTAD_RISK),
        (3, 5),
    )


def test_report_document_derives_leaders_and_reproducibility_identity() -> None:
    result = sample_result()
    document = build_report_document(result, title="Saha Deneyi", author="Araştırma Ekibi")

    assert document.title == "Saha Deneyi"
    assert document.author == "Araştırma Ekibi"
    assert document.experiment_id == result["experiment_id"]
    assert document.run_count == 4
    assert document.seed_count == 2
    assert document.baseline == "none"
    assert document.best_security_method in {"none", "gtad_risk"}
    assert document.fingerprint.startswith("sha256:")


def test_markdown_report_contains_scientific_context_and_all_methods() -> None:
    result = sample_result()
    document = build_report_document(result, note="Bir sonraki çalışma için not.")
    report = report_to_markdown(document, result).decode("utf-8")

    assert "# SwarmGuard Deney Raporu" in report
    assert "## Yönetici Özeti" in report
    assert "## Baseline'a Göre Eşleştirilmiş Farklar" in report
    assert "istatistiksel anlamlılık iddiası değildir" in report
    assert "Savunmasız" in report
    assert "GTAD Risk" in report
    assert document.fingerprint in report
    assert document.note in report


def test_html_report_is_standalone_utf8_and_escapes_user_metadata() -> None:
    result = sample_result()
    document = build_report_document(
        result,
        title="<script>alert(1)</script>",
        author="A & B",
        note="<b>ham not</b>",
    )
    report = report_to_html(document, result).decode("utf-8")

    assert report.startswith("<!doctype html>")
    assert '<meta charset="utf-8">' in report
    assert "<script>alert(1)</script>" not in report
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report
    assert "A &amp; B" in report
    assert "&lt;b&gt;ham not&lt;/b&gt;" in report
