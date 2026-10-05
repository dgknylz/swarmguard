from fastapi.testclient import TestClient

from swarmguard.api.app import create_app


def test_health_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "swarmguard-api"}


def test_local_frontend_origin_is_allowed() -> None:
    with TestClient(create_app()) as client:
        response = client.get(
            "/health",
            headers={"Origin": "http://127.0.0.1:3000"},
        )

    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_create_rejects_invalid_configuration() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/simulations",
            json={"node_count": 5, "initial_infected_count": 6},
        )

    assert response.status_code == 422


def test_websocket_streams_all_frames_in_order() -> None:
    with TestClient(create_app()) as client:
        created = client.post(
            "/api/v1/simulations",
            json={"node_count": 10, "steps": 3, "seed": 17, "step_interval_ms": 0},
        )
        assert created.status_code == 201
        payload = created.json()

        frames = []
        with client.websocket_connect(payload["stream_url"]) as websocket:
            while True:
                message = websocket.receive_json()
                if message["type"] == "frame":
                    frames.append(message["frame"])
                else:
                    terminal = message
                    break

        status_response = client.get(f"/api/v1/simulations/{payload['id']}")

    assert [frame["step"] for frame in frames] == [0, 1, 2, 3]
    assert terminal["status"] == "completed"
    assert status_response.json()["frame_count"] == 4


def test_missing_simulation_returns_not_found() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/simulations/does-not-exist")

    assert response.status_code == 404


def test_gtad_configuration_and_decision_metadata_stream_through_api() -> None:
    with TestClient(create_app()) as client:
        created = client.post(
            "/api/v1/simulations",
            json={
                "node_count": 10,
                "steps": 1,
                "seed": 7,
                "defense_strategy": "gtad_risk",
                "defense_budget": 1,
                "defense_range_multiplier": 2,
                "defense_max_degree": 4,
                "step_interval_ms": 0,
            },
        )
        payload = created.json()
        frames = []
        with client.websocket_connect(payload["stream_url"]) as websocket:
            while True:
                message = websocket.receive_json()
                if message["type"] == "frame":
                    frames.append(message["frame"])
                else:
                    break

    assert created.status_code == 201
    assert payload["config"]["defense_max_degree"] == 4
    metadata = frames[-1]["defense_report"]["metadata"]
    assert "candidate_count" in metadata
    assert metadata["constraints"]["budget"] == 1


def test_monte_carlo_endpoint_returns_paired_results() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/experiments/monte-carlo",
            json={
                "scenario": {"node_count": 8, "steps": 2, "speed": 0},
                "seeds": [2, 3],
                "strategies": ["none", "gtad_risk"],
            },
        )
        experiment_id = response.json()["experiment_id"]
        csv_export = client.get(f"/api/v1/experiments/{experiment_id}/export.csv")
        parquet_export = client.get(f"/api/v1/experiments/{experiment_id}/export.parquet")
        manifest_export = client.get(f"/api/v1/experiments/{experiment_id}/manifest.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_count"] == 4
    assert payload["paired_comparisons"][0]["pair_count"] == 2
    assert csv_export.status_code == 200
    assert "method,seed" in csv_export.text
    assert parquet_export.status_code == 200
    assert parquet_export.content[:4] == b"PAR1"
    assert parquet_export.content[-4:] == b"PAR1"
    assert manifest_export.json()["fingerprint"] == payload["manifest"]["fingerprint"]


def test_ablation_endpoint_rejects_duplicate_seeds() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/experiments/gtad-ablation",
            json={"scenario": {"node_count": 8, "steps": 1}, "seeds": [4, 4]},
        )

    assert response.status_code == 422
