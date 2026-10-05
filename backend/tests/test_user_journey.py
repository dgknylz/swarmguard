from pathlib import Path

from streamlit.testing.v1 import AppTest


def contains_markdown(app: AppTest, text: str) -> bool:
    return any(text in str(element.value) for element in app.markdown)


def test_user_journey_opens_complete_application_shell() -> None:
    entrypoint = Path(__file__).parents[2] / "streamlit_app.py"
    app = AppTest.from_file(entrypoint, default_timeout=40).run()

    assert not app.exception
    assert contains_markdown(app, "SWARMGUARD")
    assert contains_markdown(app, "Dinamik İHA ağlarını")
    assert contains_markdown(app, "SİSTEM ÇEVRİMİÇİ")


def test_user_journey_builds_scenario_inspects_node_and_opens_events() -> None:
    app = AppTest.from_string(
        "from swarmguard.dashboard.pages.simulation import render_simulation_page\n"
        "render_simulation_page()",
        default_timeout=60,
    ).run()
    app.segmented_control[0].set_value("settings")
    app.run()
    next(item for item in app.number_input if item.label == "İHA sayısı").set_value(8)
    next(item for item in app.number_input if item.label == "Zaman adımı").set_value(3)
    next(item for item in app.button if item.label == "Senaryoyu doğrula ve çalıştır").click()
    app.run()

    assert not app.exception
    assert app.session_state["config"].node_count == 8
    assert len(app.session_state["frames"]) == 4

    app.segmented_control[0].set_value("live")
    app.run()
    next(item for item in app.selectbox if item.label == "İHA incele").set_value(3)
    app.run()

    assert not app.exception
    assert app.session_state["selected_uav"] == 3
    assert contains_markdown(app, "UAV-03")
    assert contains_markdown(app, "DÜĞÜM İNCELEME PANELİ")

    app.segmented_control[0].set_value("analysis")
    app.run()
    assert not app.exception
    assert contains_markdown(app, "OLAY VE SALDIRI MERKEZİ")
    assert not contains_markdown(app, "DÜĞÜM İNCELEME PANELİ")


def test_user_journey_runs_experiment_compares_and_builds_report() -> None:
    source = """
import streamlit as st
from swarmguard.config import SimulationConfig
from swarmguard.dashboard.pages.experiments import render_experiments_page
if "config" not in st.session_state:
    st.session_state.config = SimulationConfig(node_count=8, steps=2, speed=0)
render_experiments_page()
"""
    app = AppTest.from_string(source, default_timeout=90).run()
    next(item for item in app.text_input if item.label == "Seed kümesi").set_value("3, 5")
    next(item for item in app.button if item.label == "Deneyi çalıştır").click()
    app.run()

    assert not app.exception
    assert len(app.session_state["experiment_history"]) == 1
    assert app.session_state["experiment_history"][0]["run_count"] == 4
    assert contains_markdown(app, "DENEY TAMAMLANDI")

    app.segmented_control[0].set_value("comparison")
    app.run()
    assert not app.exception
    assert contains_markdown(app, "KARŞILAŞTIRMA EKRANI")
    assert len(app.get("plotly_chart")) == 2

    app.segmented_control[0].set_value("report")
    app.run()
    assert not app.exception
    assert contains_markdown(app, "RAPOR MERKEZİ")
    assert len(app.get("download_button")) == 2


def test_user_journey_exports_workspace_with_integrity_identity() -> None:
    source = """
import streamlit as st
from swarmguard.config import SimulationConfig
from swarmguard.dashboard.performance import cached_simulation
from swarmguard.dashboard.pages.workspace import render_workspace_page
if "config" not in st.session_state:
    st.session_state.config = SimulationConfig(node_count=8, steps=2, speed=0, seed=17)
    st.session_state.frames = cached_simulation(st.session_state.config)
render_workspace_page()
"""
    app = AppTest.from_string(source, default_timeout=40).run()

    assert not app.exception
    assert contains_markdown(app, "OTURUM VE VERİ PAYLAŞIMI")
    assert contains_markdown(app, "sha256:")
    assert len(app.get("download_button")) == 1
    assert len(app.get("file_uploader")) == 1


def test_user_journey_reads_methodology_and_product_scope() -> None:
    methodology = AppTest.from_string(
        "from swarmguard.dashboard.pages.methodology import render_methodology_page\n"
        "render_methodology_page()",
        default_timeout=40,
    ).run()
    about = AppTest.from_string(
        "from swarmguard.dashboard.pages.about import render_about_page\nrender_about_page()",
        default_timeout=40,
    ).run()

    assert not methodology.exception
    assert contains_markdown(methodology, "METODOLOJİ VE ALGORİTMALAR")
    assert len(methodology.latex) == 6
    assert not about.exception
    assert contains_markdown(about, "SWARMGUARD · v1.1.0")
    assert contains_markdown(about, "46 / 47 adım")
    assert any(expander.label == "Tasarım sistemi vitrini" for expander in about.expander)
