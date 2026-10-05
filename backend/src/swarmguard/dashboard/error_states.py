from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from html import escape

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ErrorPresentation:
    code: str
    title: str
    message: str
    recovery: str


def classify_error(error: Exception) -> ErrorPresentation:
    if isinstance(error, ValueError):
        return ErrorPresentation(
            "SG-INPUT",
            "Girdi doğrulanamadı",
            "Seçilen değerlerden biri beklenen biçim veya aralığın dışında.",
            "Parametreleri kontrol edip işlemi yeniden dene.",
        )
    if isinstance(error, MemoryError):
        return ErrorPresentation(
            "SG-CAPACITY",
            "İşlem kapasite sınırına ulaştı",
            "Bu çalışma mevcut oturum için fazla büyük.",
            "İHA, adım veya seed sayısını azaltıp yeniden dene.",
        )
    if isinstance(error, (TimeoutError, ConnectionError)):
        return ErrorPresentation(
            "SG-CONNECTION",
            "İşlem tamamlanamadı",
            "Bağlantı veya işlem süresi geçici olarak kesintiye uğradı.",
            "Bağlantını kontrol edip yeniden dene.",
        )
    return ErrorPresentation(
        "SG-UNEXPECTED",
        "Beklenmeyen bir sorun oluştu",
        "Bu bölüm güvenli biçimde durduruldu; oturumundaki diğer veriler korunuyor.",
        "Sayfayı yeniden dene. Sorun sürerse çalışma alanını indirip yeni oturum aç.",
    )


def render_empty_state(
    st,
    *,
    icon: str,
    title: str,
    message: str,
    action_label: str | None = None,
    action_href: str | None = None,
) -> None:
    action = (
        f'<a href="{escape(action_href)}" target="_self">{escape(action_label)} →</a>'
        if action_label and action_href
        else ""
    )
    st.markdown(
        f"""
        <section class="sg-state sg-state-empty">
            <div>{escape(icon)}</div><article><small>HAZIRLIK GEREKİYOR</small>
            <h3>{escape(title)}</h3><p>{escape(message)}</p>{action}</article>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_error_state(st, error: Exception, *, retry_key: str = "page-retry") -> None:
    presentation = classify_error(error)
    st.markdown(
        f"""
        <section class="sg-state sg-state-error" role="alert">
            <div>!</div><article><small>{presentation.code}</small>
            <h3>{presentation.title}</h3><p>{presentation.message}</p>
            <b>{presentation.recovery}</b></article>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Yeniden dene", key=retry_key, type="primary"):
        st.rerun()


def render_page_safely(st, renderer: Callable[[], None], *, page_title: str) -> None:
    try:
        renderer()
    except Exception as error:
        logger.exception("Dashboard page failed: %s", page_title)
        render_error_state(st, error, retry_key=f"retry-{page_title}")
