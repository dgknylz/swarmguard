from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def get_or_create(session_state, key: str, factory: Callable[[], T]) -> T:
    if key not in session_state:
        session_state[key] = factory()
    return session_state[key]
