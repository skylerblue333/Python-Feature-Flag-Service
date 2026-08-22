from fastapi.testclient import TestClient

from src.service import app, flags_db

client = TestClient(app)


def setup_function() -> None:
    flags_db.clear()


def test_create_and_evaluate() -> None:
    payload = {
        "name": "new_ui",
        "description": "The new dashboard UI",
        "rule": {"enabled": True, "percentage": 0, "user_ids": ["user123"]},
    }
    response = client.post("/flags", json=payload)
    assert response.status_code == 201
    assert client.get("/evaluate/new_ui/user123").json() == {"enabled": True, "reason": "user_allowlist"}
    assert client.get("/evaluate/new_ui/user999").json()["enabled"] is False


def test_rejects_duplicate_and_invalid_flags() -> None:
    payload = {"name": "new_ui", "description": "A flag", "rule": {"enabled": True}}
    assert client.post("/flags", json=payload).status_code == 201
    assert client.post("/flags", json=payload).status_code == 409
    invalid = {"name": "bad flag", "description": "A flag", "rule": {"enabled": True, "percentage": 101}}
    assert client.post("/flags", json=invalid).status_code == 422


def test_percentage_rollout_is_stable_across_repeated_reads() -> None:
    payload = {"name": "rollout", "description": "A flag", "rule": {"enabled": True, "percentage": 50}}
    assert client.post("/flags", json=payload).status_code == 201
    first = client.get("/evaluate/rollout/user999").json()
    assert client.get("/evaluate/rollout/user999").json() == first
