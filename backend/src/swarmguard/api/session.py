from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import asdict
from enum import Enum
from uuid import uuid4

from ..engine import SimulationEngine, SimulationFrame
from .schemas import SimulationCreateRequest


class SessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


TERMINAL_STATUSES = {
    SessionStatus.COMPLETED,
    SessionStatus.STOPPED,
    SessionStatus.FAILED,
}


class InvalidTransitionError(RuntimeError):
    pass


class SimulationSession:
    def __init__(self, request: SimulationCreateRequest):
        self.id = str(uuid4())
        self.request = request
        self.engine = SimulationEngine(request.to_core_config())
        self.status = SessionStatus.CREATED
        self.frames: list[SimulationFrame] = []
        self.error: str | None = None
        self._condition = asyncio.Condition()
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._stop_requested = False
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is not None:
            raise InvalidTransitionError("Simülasyon daha önce başlatılmış")
        self._task = asyncio.create_task(self._run(), name=f"simulation-{self.id}")

    async def _notify(self) -> None:
        async with self._condition:
            self._condition.notify_all()

    async def _publish(self, frame: SimulationFrame) -> None:
        async with self._condition:
            self.frames.append(frame)
            self._condition.notify_all()

    async def _run(self) -> None:
        try:
            self.status = SessionStatus.RUNNING
            await self._publish(self.engine.initial_frame())

            for _ in range(self.request.steps):
                await self._pause_event.wait()
                if self._stop_requested:
                    break

                if self.request.step_interval_ms:
                    await asyncio.sleep(self.request.step_interval_ms / 1_000)
                    await self._pause_event.wait()
                    if self._stop_requested:
                        break

                await self._publish(self.engine.step())

            self.status = SessionStatus.STOPPED if self._stop_requested else SessionStatus.COMPLETED
        except asyncio.CancelledError:
            self.status = SessionStatus.STOPPED
            raise
        except Exception as exc:  # noqa: BLE001  # pragma: no cover
            # A background task must expose unexpected failures through its
            # session status instead of silently disappearing from the API.
            self.error = str(exc)
            self.status = SessionStatus.FAILED
        finally:
            await self._notify()

    async def pause(self) -> None:
        if self.status is not SessionStatus.RUNNING:
            raise InvalidTransitionError("Yalnızca çalışan simülasyon duraklatılabilir")
        self._pause_event.clear()
        self.status = SessionStatus.PAUSED
        await self._notify()

    async def resume(self) -> None:
        if self.status is not SessionStatus.PAUSED:
            raise InvalidTransitionError("Yalnızca duraklatılmış simülasyon sürdürülebilir")
        self.status = SessionStatus.RUNNING
        self._pause_event.set()
        await self._notify()

    async def stop(self) -> None:
        if self.status in TERMINAL_STATUSES:
            raise InvalidTransitionError("Tamamlanmış simülasyon durdurulamaz")
        self._stop_requested = True
        self._pause_event.set()
        await self._notify()

    async def cancel(self) -> None:
        if self._task is None or self._task.done():
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    async def wait(self) -> None:
        if self._task is not None:
            await self._task

    def snapshot(self) -> dict[str, object]:
        return {
            "id": self.id,
            "status": self.status.value,
            "latest_step": self.frames[-1].step if self.frames else -1,
            "frame_count": len(self.frames),
            "error": self.error,
        }

    async def stream_messages(self) -> AsyncIterator[dict[str, object]]:
        cursor = 0
        while True:
            async with self._condition:
                await self._condition.wait_for(
                    lambda cursor=cursor: (
                        cursor < len(self.frames) or self.status in TERMINAL_STATUSES
                    )
                )
                pending_frames = self.frames[cursor:]
                cursor = len(self.frames)
                terminal = self.status in TERMINAL_STATUSES

            for frame in pending_frames:
                yield {
                    "type": "frame",
                    "simulation_id": self.id,
                    "frame": frame.to_dict(),
                }

            if terminal and cursor == len(self.frames):
                yield {
                    "type": "status",
                    "simulation_id": self.id,
                    "status": self.status.value,
                    "error": self.error,
                }
                return

    def serialized_config(self) -> dict[str, object]:
        config = asdict(self.engine.config)
        config["attack_strategy"] = self.engine.config.attack_strategy.value
        config["defense_strategy"] = self.engine.config.defense_strategy.value
        config["step_interval_ms"] = self.request.step_interval_ms
        return config


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, SimulationSession] = {}

    def create(self, request: SimulationCreateRequest) -> SimulationSession:
        session = SimulationSession(request)
        self._sessions[session.id] = session
        session.start()
        return session

    def get(self, simulation_id: str) -> SimulationSession | None:
        return self._sessions.get(simulation_id)

    async def shutdown(self) -> None:
        await asyncio.gather(*(session.cancel() for session in self._sessions.values()))
