from fastapi.testclient import TestClient
from src.service import app

client = TestClient(app)

def test_create_and_evaluate():
    payload = {
        "name": "new_ui",
        "description": "The new dashboard UI",
        "rule": {
            "enabled": True,
            "percentage": 0,
            "user_ids": ["user123"]
        }
    }
    r = client.post("/flags", json=payload)
    assert r.status_code == 201
    
    # Should be enabled for allowlisted user
    r = client.get("/evaluate/new_ui/user123")
    assert r.json()["enabled"] is True
    
    # Should be disabled for others (0%)
    r = client.get("/evaluate/new_ui/user999")
    assert r.json()["enabled"] is False
