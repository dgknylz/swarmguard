from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from ..experiment_exports import manifest_to_json, runs_to_csv, runs_to_parquet
from ..experiments import run_gtad_ablation, run_monte_carlo
from .schemas import (
    ControlResponse,
    ExperimentRequest,
    MonteCarloRequest,
    SimulationCreateRequest,
    SimulationCreateResponse,
    SimulationStatusResponse,
)
from .session import InvalidTransitionError, SessionManager


def create_app() -> FastAPI:
    manager = SessionManager()
    experiment_results: dict[str, dict[str, object]] = {}

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        await manager.shutdown()

    app = FastAPI(
        title="SwarmGuard API",
        version="0.3.0",
        description="Dynamic UAV cyber-resilience simulation API",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def require_session(simulation_id: str):
        session = manager.get(simulation_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Simülasyon bulunamadı")
        return session

    def require_experiment(experiment_id: str) -> dict[str, object]:
        result = experiment_results.get(experiment_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Deney bulunamadı")
        return result

    def store_experiment(result: dict[str, object]) -> dict[str, object]:
        experiment_results[str(result["experiment_id"])] = result
        return result

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "swarmguard-api"}

    @app.post(
        "/api/v1/simulations",
        response_model=SimulationCreateResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_simulation(request: SimulationCreateRequest) -> dict[str, object]:
        session = manager.create(request)
        return {
            "id": session.id,
            "status": session.status.value,
            "stream_url": f"/api/v1/simulations/{session.id}/stream",
            "config": session.serialized_config(),
        }

    @app.get("/api/v1/simulations/{simulation_id}", response_model=SimulationStatusResponse)
    async def get_simulation(simulation_id: str) -> dict[str, object]:
        return require_session(simulation_id).snapshot()

    async def apply_control(simulation_id: str, action: str) -> dict[str, str]:
        session = require_session(simulation_id)
        try:
            await getattr(session, action)()
        except InvalidTransitionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"id": session.id, "status": session.status.value}

    @app.post("/api/v1/simulations/{simulation_id}/pause", response_model=ControlResponse)
    async def pause_simulation(simulation_id: str) -> dict[str, str]:
        return await apply_control(simulation_id, "pause")

    @app.post("/api/v1/simulations/{simulation_id}/resume", response_model=ControlResponse)
    async def resume_simulation(simulation_id: str) -> dict[str, str]:
        return await apply_control(simulation_id, "resume")

    @app.post("/api/v1/simulations/{simulation_id}/stop", response_model=ControlResponse)
    async def stop_simulation(simulation_id: str) -> dict[str, str]:
        return await apply_control(simulation_id, "stop")

    @app.post("/api/v1/experiments/monte-carlo")
    async def create_monte_carlo_experiment(
        request: MonteCarloRequest,
    ) -> dict[str, object]:
        return store_experiment(
            await run_in_threadpool(
                run_monte_carlo,
                request.scenario.to_core_config(),
                request.strategies,
                request.seeds,
            )
        )

    @app.post("/api/v1/experiments/gtad-ablation")
    async def create_gtad_ablation_experiment(
        request: ExperimentRequest,
    ) -> dict[str, object]:
        return store_experiment(
            await run_in_threadpool(
                run_gtad_ablation,
                request.scenario.to_core_config(),
                request.seeds,
            )
        )

    @app.get("/api/v1/experiments/{experiment_id}/export.csv")
    async def export_experiment_csv(experiment_id: str) -> Response:
        return Response(
            runs_to_csv(require_experiment(experiment_id)),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="swarmguard-{experiment_id}-runs.csv"'
                )
            },
        )

    @app.get("/api/v1/experiments/{experiment_id}/export.parquet")
    async def export_experiment_parquet(experiment_id: str) -> Response:
        payload = await run_in_threadpool(runs_to_parquet, require_experiment(experiment_id))
        return Response(
            payload,
            media_type="application/vnd.apache.parquet",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="swarmguard-{experiment_id}-runs.parquet"'
                )
            },
        )

    @app.get("/api/v1/experiments/{experiment_id}/manifest.json")
    async def export_experiment_manifest(experiment_id: str) -> Response:
        return Response(
            manifest_to_json(require_experiment(experiment_id)),
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="swarmguard-{experiment_id}-manifest.json"'
                )
            },
        )

    @app.websocket("/api/v1/simulations/{simulation_id}/stream")
    async def simulation_stream(websocket: WebSocket, simulation_id: str) -> None:
        session = manager.get(simulation_id)
        if session is None:
            await websocket.close(code=4404, reason="Simülasyon bulunamadı")
            return

        await websocket.accept()
        try:
            async for message in session.stream_messages():
                await websocket.send_json(message)
        except WebSocketDisconnect:
            return

    return app


app = create_app()
