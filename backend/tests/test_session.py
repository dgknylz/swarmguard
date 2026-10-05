import asyncio

from swarmguard.api.schemas import SimulationCreateRequest
from swarmguard.api.session import SessionManager, SessionStatus


def test_session_can_pause_resume_and_complete() -> None:
    async def scenario() -> None:
        manager = SessionManager()
        session = manager.create(
            SimulationCreateRequest(
                node_count=12,
                steps=12,
                seed=9,
                step_interval_ms=15,
            )
        )

        await asyncio.sleep(0.04)
        await session.pause()
        paused_step = session.snapshot()["latest_step"]
        await asyncio.sleep(0.04)

        assert session.status is SessionStatus.PAUSED
        assert session.snapshot()["latest_step"] == paused_step

        await session.resume()
        await session.wait()

        assert session.status is SessionStatus.COMPLETED
        assert len(session.frames) == 13
        await manager.shutdown()

    asyncio.run(scenario())
