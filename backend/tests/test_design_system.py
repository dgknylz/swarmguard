import pytest

from swarmguard.dashboard.design_system import (
    COLOR_TOKENS,
    RADIUS_TOKENS,
    SPACING_TOKENS,
    STATUS_TONES,
    contrast_ratio,
    design_token_css,
)


def test_design_tokens_have_unique_names_variables_and_valid_hex_colors() -> None:
    assert len({token.name for token in COLOR_TOKENS}) == len(COLOR_TOKENS)
    assert len({token.css_variable for token in COLOR_TOKENS}) == len(COLOR_TOKENS)
    assert all(token.value.startswith("#") and len(token.value) == 7 for token in COLOR_TOKENS)
    assert len(SPACING_TOKENS) == 7
    assert len(RADIUS_TOKENS) == 4
    assert set(STATUS_TONES) == {"success", "info", "warning", "danger", "neutral"}


def test_primary_text_and_brand_meet_accessible_contrast_on_canvas() -> None:
    colors = {token.name: token.value for token in COLOR_TOKENS}

    assert contrast_ratio(colors["Text"], colors["Canvas"]) >= 7
    assert contrast_ratio(colors["Brand"], colors["Canvas"]) >= 4.5
    assert contrast_ratio(colors["Text muted"], colors["Canvas"]) >= 4.5


def test_contrast_ratio_is_symmetric_and_rejects_invalid_hex() -> None:
    assert contrast_ratio("#ffffff", "#000000") == pytest.approx(21)
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21)
    with pytest.raises(ValueError, match="altı basamaklı"):
        contrast_ratio("#fff", "#000000")


def test_generated_css_contains_every_public_token_and_foundation() -> None:
    css = design_token_css()

    assert all(f"{token.css_variable}: {token.value};" in css for token in COLOR_TOKENS)
    assert all(f"{name}: {value};" in css for name, value in SPACING_TOKENS.items())
    assert all(f"{name}: {value};" in css for name, value in RADIUS_TOKENS.items())
    assert "--sg-focus:" in css
    assert "--sg-font-sans:" in css
