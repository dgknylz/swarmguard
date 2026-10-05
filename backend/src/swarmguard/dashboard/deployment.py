from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DeploymentCheck:
    key: str
    status: str
    message: str


@dataclass(frozen=True, slots=True)
class DeploymentReport:
    checks: tuple[DeploymentCheck, ...]

    @property
    def blockers(self) -> tuple[DeploymentCheck, ...]:
        return tuple(check for check in self.checks if check.status == "block")

    @property
    def ready(self) -> bool:
        return not self.blockers


def _git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def run_cloud_preflight(
    root: Path,
    *,
    git_remote: str | None = None,
    tracked_files: set[str] | None = None,
    python_version: tuple[int, int] | None = None,
) -> DeploymentReport:
    root = root.resolve()
    required = (
        "streamlit_app.py",
        "requirements.txt",
        ".streamlit/config.toml",
        "backend/pyproject.toml",
    )
    checks: list[DeploymentCheck] = []
    missing = [path for path in required if not (root / path).is_file()]
    checks.append(
        DeploymentCheck(
            "required_files",
            "pass" if not missing else "block",
            "Cloud giriş ve yapılandırma dosyaları hazır."
            if not missing
            else f"Eksik dosyalar: {', '.join(missing)}",
        )
    )

    entrypoint = (root / "streamlit_app.py").read_text("utf-8") if not missing else ""
    checks.append(
        DeploymentCheck(
            "entrypoint",
            "pass" if "run_dashboard" in entrypoint else "block",
            "Streamlit giriş noktası dashboard uygulamasını başlatıyor."
            if "run_dashboard" in entrypoint
            else "streamlit_app.py beklenen dashboard girişini içermiyor.",
        )
    )
    requirements = (root / "requirements.txt").read_text("utf-8") if not missing else ""
    checks.append(
        DeploymentCheck(
            "dependencies",
            "pass" if "./backend[dashboard]" in requirements else "block",
            "Cloud bağımlılıkları dashboard paketi üzerinden kuruluyor."
            if "./backend[dashboard]" in requirements
            else "requirements.txt dashboard bağımlılık grubunu kurmuyor.",
        )
    )
    config = (root / ".streamlit/config.toml").read_text("utf-8") if not missing else ""
    config_ready = all(marker in config for marker in ("[theme]", "[server]", "headless = true"))
    checks.append(
        DeploymentCheck(
            "streamlit_config",
            "pass" if config_ready else "block",
            "Tema ve headless sunucu yapılandırması hazır."
            if config_ready
            else "Streamlit Cloud yapılandırması eksik veya uyumsuz.",
        )
    )
    version = python_version or (sys.version_info.major, sys.version_info.minor)
    supported = version[0] == 3 and 10 <= version[1] <= 13
    checks.append(
        DeploymentCheck(
            "python_version",
            "pass" if supported else "block",
            f"Python {version[0]}.{version[1]} desteklenen aralıkta."
            if supported
            else f"Python {version[0]}.{version[1]} yerine 3.10–3.13 kullanılmalı.",
        )
    )
    secrets_present = (root / ".streamlit/secrets.toml").exists()
    checks.append(
        DeploymentCheck(
            "secrets",
            "warn" if secrets_present else "pass",
            "Yerel secrets.toml bulundu; Git'e eklenmediğini doğrula."
            if secrets_present
            else "Uygulama yayın için gizli anahtar gerektirmiyor.",
        )
    )

    remote = (
        git_remote if git_remote is not None else _git_output(root, "remote", "get-url", "origin")
    )
    checks.append(
        DeploymentCheck(
            "git_remote",
            "pass" if remote else "block",
            f"Git teslim hedefi hazır: {remote}"
            if remote
            else "GitHub origin remote'u yapılandırılmamış.",
        )
    )
    tracked = (
        tracked_files
        if tracked_files is not None
        else set(_git_output(root, "ls-files").splitlines())
    )
    delivery_files = set(required)
    untracked = sorted(delivery_files - tracked)
    checks.append(
        DeploymentCheck(
            "tracked_delivery",
            "pass" if not untracked else "block",
            "Yayın dosyaları Git tarafından izleniyor."
            if not untracked
            else f"Commit edilmemiş yayın dosyaları: {', '.join(untracked)}",
        )
    )
    return DeploymentReport(tuple(checks))


def format_preflight(report: DeploymentReport) -> str:
    icons = {"pass": "PASS", "warn": "WARN", "block": "BLOCK"}
    lines = [f"[{icons[check.status]}] {check.key}: {check.message}" for check in report.checks]
    lines.append("READY" if report.ready else f"BLOCKED ({len(report.blockers)})")
    return "\n".join(lines)


if __name__ == "__main__":
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    report = run_cloud_preflight(project_root)
    print(format_preflight(report))
    raise SystemExit(0 if report.ready else 1)
