import pytest

from swarmguard.dashboard.components.about_center import calculate_progress, get_project_profile
from swarmguard.dashboard.navigation import PAGE_SPECS


def test_product_progress_is_bounded_and_rejects_invalid_values() -> None:
    assert calculate_progress(40, 47) == pytest.approx(40 / 47)
    assert calculate_progress(0, 47) == 0
    assert calculate_progress(47, 47) == 1

    with pytest.raises(ValueError, match="pozitif"):
        calculate_progress(0, 0)
    with pytest.raises(ValueError, match="geçerli aralık"):
        calculate_progress(48, 47)


def test_project_profile_has_complete_unique_architecture_and_capabilities() -> None:
    profile = get_project_profile()

    assert profile.name == "SwarmGuard"
    assert profile.version == "1.1.0"
    assert profile.completed_steps == 47
    assert profile.total_steps == 47
    assert len(profile.architecture) == 4
    assert len({layer.key for layer in profile.architecture}) == len(profile.architecture)
    assert len(profile.capabilities) == 6
    assert len(profile.principles) == 4


def test_about_page_is_registered_in_top_navigation() -> None:
    about = next(spec for spec in PAGE_SPECS if spec.path == "about")

    assert about.title == "Hakkında"
    assert about.icon == ":material/info:"
    assert about.default is False
