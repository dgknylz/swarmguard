import pytest

from swarmguard.dashboard.simulation_session import (
    PlaybackStatus,
    advance_playback,
    apply_playback_command,
    ensure_playback_state,
    reset_playback,
    seek_playback,
)


def test_playback_lifecycle_controls_status_and_cursor() -> None:
    session: dict[str, object] = {}
    playback = ensure_playback_state(session, 5)

    assert playback.status is PlaybackStatus.READY
    assert playback.index == 0

    apply_playback_command(playback, "play", 5)
    assert playback.status is PlaybackStatus.RUNNING
    assert advance_playback(playback, 5) is False
    assert playback.index == 1

    apply_playback_command(playback, "pause", 5)
    apply_playback_command(playback, "next", 5)
    assert playback.status is PlaybackStatus.PAUSED
    assert playback.index == 2

    apply_playback_command(playback, "stop", 5)
    assert playback.status is PlaybackStatus.STOPPED
    apply_playback_command(playback, "restart", 5)
    assert playback.status is PlaybackStatus.READY
    assert playback.index == 0


def test_playback_seek_and_advance_respect_frame_boundaries() -> None:
    playback = reset_playback({}, 3, autoplay=True)

    seek_playback(playback, 99, 3)
    assert playback.index == 2
    assert playback.status is PlaybackStatus.COMPLETED

    apply_playback_command(playback, "play", 3)
    assert playback.index == 0
    assert advance_playback(playback, 3) is False
    assert advance_playback(playback, 3) is True
    assert playback.status is PlaybackStatus.COMPLETED

    seek_playback(playback, -20, 3)
    assert playback.index == 0
    assert playback.status is PlaybackStatus.PAUSED


def test_playback_reset_and_unknown_command() -> None:
    session: dict[str, object] = {}
    playback = reset_playback(session, 4, autoplay=True)
    playback.speed = 4.0

    assert playback.status is PlaybackStatus.RUNNING
    assert session["replay_cursor"] == 0
    assert ensure_playback_state(session, 2) is playback

    with pytest.raises(ValueError, match="Bilinmeyen playback komutu"):
        apply_playback_command(playback, "launch", 2)
