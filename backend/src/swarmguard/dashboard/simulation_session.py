from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PlaybackStatus(str, Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"


@dataclass
class PlaybackState:
    status: PlaybackStatus = PlaybackStatus.READY
    index: int = 0
    speed: float = 1.0


def ensure_playback_state(session_state, frame_count: int) -> PlaybackState:
    playback = session_state.get("playback")
    if not isinstance(playback, PlaybackState):
        playback = PlaybackState()
        session_state["playback"] = playback
    playback.index = max(0, min(playback.index, max(0, frame_count - 1)))
    return playback


def reset_playback(session_state, frame_count: int, *, autoplay: bool = False) -> PlaybackState:
    playback = PlaybackState(
        status=PlaybackStatus.RUNNING if autoplay and frame_count > 1 else PlaybackStatus.READY,
        index=0,
    )
    session_state["playback"] = playback
    session_state["replay_cursor"] = 0
    return playback


def apply_playback_command(playback: PlaybackState, command: str, frame_count: int) -> None:
    last_index = max(0, frame_count - 1)
    if command == "play":
        if playback.index >= last_index:
            playback.index = 0
        playback.status = PlaybackStatus.RUNNING
    elif command == "pause" and playback.status is PlaybackStatus.RUNNING:
        playback.status = PlaybackStatus.PAUSED
    elif command == "stop":
        playback.status = PlaybackStatus.STOPPED
    elif command == "previous":
        playback.index = max(0, playback.index - 1)
        playback.status = PlaybackStatus.PAUSED
    elif command == "next":
        playback.index = min(last_index, playback.index + 1)
        playback.status = (
            PlaybackStatus.COMPLETED if playback.index >= last_index else PlaybackStatus.PAUSED
        )
    elif command == "restart":
        playback.index = 0
        playback.status = PlaybackStatus.READY
    else:
        raise ValueError(f"Bilinmeyen playback komutu: {command}")


def seek_playback(playback: PlaybackState, index: int, frame_count: int) -> None:
    last_index = max(0, frame_count - 1)
    playback.index = max(0, min(int(index), last_index))
    playback.status = (
        PlaybackStatus.COMPLETED if playback.index >= last_index else PlaybackStatus.PAUSED
    )


def advance_playback(playback: PlaybackState, frame_count: int) -> bool:
    if playback.status is not PlaybackStatus.RUNNING:
        return False
    last_index = max(0, frame_count - 1)
    if playback.index < last_index:
        playback.index += 1
    if playback.index >= last_index:
        playback.status = PlaybackStatus.COMPLETED
        return True
    return False
