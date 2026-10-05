from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColorToken:
    name: str
    css_variable: str
    value: str
    role: str


COLOR_TOKENS = (
    ColorToken("Canvas", "--sg-bg", "#061014", "Ana uygulama zemini"),
    ColorToken("Surface", "--sg-surface", "#0b1c21", "Kart ve form yüzeyi"),
    ColorToken("Surface raised", "--sg-surface-raised", "#10262c", "Yükseltilmiş yüzey"),
    ColorToken("Text", "--sg-text", "#e9f8f6", "Birincil metin"),
    ColorToken("Text muted", "--sg-muted", "#789097", "İkincil metin"),
    ColorToken("Brand", "--sg-cyan", "#57e7d6", "Marka ve birincil eylem"),
    ColorToken("Info", "--sg-info", "#79b8ff", "Bilgilendirme"),
    ColorToken("Warning", "--sg-warning", "#fbbf24", "Uyarı"),
    ColorToken("Danger", "--sg-danger", "#fb7185", "Kritik ve enfekte"),
    ColorToken("Success", "--sg-success", "#6ee7b7", "Sağlıklı ve başarılı"),
)

SPACING_TOKENS = {
    "--sg-space-1": "0.25rem",
    "--sg-space-2": "0.5rem",
    "--sg-space-3": "0.75rem",
    "--sg-space-4": "1rem",
    "--sg-space-6": "1.5rem",
    "--sg-space-8": "2rem",
    "--sg-space-12": "3rem",
}

RADIUS_TOKENS = {
    "--sg-radius-sm": "0.55rem",
    "--sg-radius-md": "0.85rem",
    "--sg-radius-lg": "1.2rem",
    "--sg-radius-pill": "999px",
}

STATUS_TONES = {
    "success": ("Başarılı", "--sg-success"),
    "info": ("Bilgi", "--sg-info"),
    "warning": ("Uyarı", "--sg-warning"),
    "danger": ("Kritik", "--sg-danger"),
    "neutral": ("Nötr", "--sg-muted"),
}


def _hex_rgb(value: str) -> tuple[int, int, int]:
    normalized = value.removeprefix("#")
    if len(normalized) != 6:
        raise ValueError("Renk altı basamaklı hex biçiminde olmalıdır")
    try:
        return tuple(int(normalized[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as exc:
        raise ValueError("Geçersiz hex renk") from exc


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(value: str) -> float:
        channels = []
        for channel in _hex_rgb(value):
            normalized = channel / 255
            channels.append(
                normalized / 12.92
                if normalized <= 0.04045
                else ((normalized + 0.055) / 1.055) ** 2.4
            )
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def design_token_css() -> str:
    declarations = {
        **{token.css_variable: token.value for token in COLOR_TOKENS},
        **SPACING_TOKENS,
        **RADIUS_TOKENS,
        "--sg-border": "rgba(148, 197, 202, 0.12)",
        "--sg-border-strong": "rgba(148, 197, 202, 0.24)",
        "--sg-focus": "0 0 0 3px rgba(87, 231, 214, 0.28)",
        "--sg-shadow-sm": "0 10px 30px rgba(0, 0, 0, 0.16)",
        "--sg-shadow-lg": "0 28px 80px rgba(0, 0, 0, 0.28)",
        "--sg-font-sans": "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif",
        "--sg-font-mono": "'IBM Plex Mono', 'Cascadia Code', ui-monospace, monospace",
    }
    body = "\n".join(f"        {name}: {value};" for name, value in declarations.items())
    return f"<style>\n    :root {{\n{body}\n    }}\n</style>"


def render_design_system_showcase(st) -> None:
    st.markdown("#### Tasarım sistemi")
    st.caption(
        "Bütün sayfalar aynı renk, tipografi, boşluk, yüzey ve durum sözleşmesini kullanır. "
        "Bileşenler klavye odağı ve azaltılmış hareket tercihini destekler."
    )
    swatches = "".join(
        f"<article><i style='background:{token.value}'></i><div><b>{token.name}</b><code>{token.value}</code><small>{token.role}</small></div></article>"
        for token in COLOR_TOKENS
    )
    st.markdown(f"<section class='sg-token-grid'>{swatches}</section>", unsafe_allow_html=True)
    tones = "".join(
        f"<span class='sg-badge sg-badge-{tone}'>{label}</span>"
        for tone, (label, _) in STATUS_TONES.items()
    )
    st.markdown(f"<div class='sg-badge-showcase'>{tones}</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <section class="sg-type-specimen">
            <small>TYPOGRAPHY / DISPLAY</small><h3>Bilimsel veri, operasyonel netlik.</h3>
            <p>Arayüz metinleri sistem sans-serif ailesini; kimlikler, sayılar ve teknik değerler monospace ailesini kullanır.</p>
            <code>GTAD · λ₂ 0.482 · SEED 2025 · SHA-256</code>
        </section>
        """,
        unsafe_allow_html=True,
    )
