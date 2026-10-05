from pathlib import Path

from swarmguard.dashboard.deployment import format_preflight, run_cloud_preflight


def make_cloud_project(root: Path) -> set[str]:
    (root / ".streamlit").mkdir()
    (root / "backend").mkdir()
    (root / "streamlit_app.py").write_text(
        "from swarmguard.dashboard.app import run_dashboard\nrun_dashboard()\n",
        encoding="utf-8",
    )
    (root / "requirements.txt").write_text("-e ./backend[dashboard]\n", encoding="utf-8")
    (root / ".streamlit/config.toml").write_text(
        "[theme]\nbase='dark'\n[server]\nheadless = true\n",
        encoding="utf-8",
    )
    (root / "backend/pyproject.toml").write_text("[project]\n", encoding="utf-8")
    return {
        "streamlit_app.py",
        "requirements.txt",
        ".streamlit/config.toml",
        "backend/pyproject.toml",
    }


def test_cloud_preflight_passes_complete_delivery_contract(tmp_path: Path) -> None:
    tracked = make_cloud_project(tmp_path)
    report = run_cloud_preflight(
        tmp_path,
        git_remote="https://github.com/example/swarmguard.git",
        tracked_files=tracked,
        python_version=(3, 12),
    )

    assert report.ready is True
    assert not report.blockers
    assert all(check.status == "pass" for check in report.checks)
    assert format_preflight(report).endswith("READY")


def test_cloud_preflight_reports_delivery_blockers(tmp_path: Path) -> None:
    make_cloud_project(tmp_path)
    report = run_cloud_preflight(
        tmp_path,
        git_remote="",
        tracked_files=set(),
        python_version=(3, 10),
    )

    assert report.ready is False
    assert {check.key for check in report.blockers} == {"git_remote", "tracked_delivery"}
    assert format_preflight(report).endswith("BLOCKED (2)")


def test_cloud_preflight_rejects_missing_files_and_unsupported_python(tmp_path: Path) -> None:
    report = run_cloud_preflight(
        tmp_path,
        git_remote="https://github.com/example/swarmguard.git",
        tracked_files=set(),
        python_version=(3, 9),
    )

    blocker_keys = {check.key for check in report.blockers}
    assert "required_files" in blocker_keys
    assert "python_version" in blocker_keys
    assert "entrypoint" in blocker_keys
