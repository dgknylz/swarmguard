from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Protocol

from .error_states import render_page_safely
from .pages.about import render_about_page
from .pages.experiments import render_experiments_page
from .pages.methodology import render_methodology_page
from .pages.overview import render_overview_page
from .pages.simulation import render_simulation_page
from .pages.workspace import render_workspace_page


class StreamlitNavigation(Protocol):
    def run(self) -> None: ...


@dataclass(frozen=True)
class PageSpec:
    title: str
    icon: str
    path: str
    section: str
    renderer: Callable[[], None]
    default: bool = False


PAGE_SPECS = (
    PageSpec("Genel Bakış", ":material/home:", "overview", "Platform", render_overview_page, True),
    PageSpec("Simülasyon", ":material/hub:", "simulation", "Platform", render_simulation_page),
    PageSpec(
        "Çalışma Alanı",
        ":material/folder_open:",
        "workspace",
        "Platform",
        render_workspace_page,
    ),
    PageSpec("Deneyler", ":material/science:", "experiments", "Araştırma", render_experiments_page),
    PageSpec(
        "Metodoloji",
        ":material/menu_book:",
        "methodology",
        "Araştırma",
        render_methodology_page,
    ),
    PageSpec("Hakkında", ":material/info:", "about", "Araştırma", render_about_page),
)


def build_navigation(st) -> StreamlitNavigation:
    pages: list[object] = []
    for spec in PAGE_SPECS:
        safe_renderer = partial(
            render_page_safely,
            st,
            spec.renderer,
            page_title=spec.title,
        )
        page = st.Page(
            safe_renderer,
            title=spec.title,
            icon=spec.icon,
            url_path=spec.path,
            default=spec.default,
        )
        pages.append(page)
    return st.navigation(pages, position="top")
