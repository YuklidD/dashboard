from fastapi.testclient import TestClient
from app.core.config import settings

def test_login_access_token(client: TestClient):
    # Create initial admin user is handled by startup event, 
    # but in tests we might need to seed it or rely on the override.
    # Since we use a fresh in-memory DB, the startup event might not have run 
    # or we need to trigger it. 
    # For simplicity in this test setup, we will create a user manually in the test or fixture.
    # However, app.main:create_initial_data runs on startup. 
    # TestClient triggers startup events.
    
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

def test_deploy_honeypot(client: TestClient):
    # 1. Login to get token
    login_data = {"username": "admin", "password": "admin"}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Deploy Honeypot
    honeypot_data = {
        "name": "test-honeypot",
        "image": "shellm-honeypot:test"
    }
    r = client.post(f"{settings.API_V1_STR}/honeypots/", json=honeypot_data, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "test-honeypot"
    assert data["status"] == "Running" # Mock orchestrator returns Running immediately
    assert "id" in data
    
    honeypot_id = data["id"]

    # 3. List Honeypots
    r = client.get(f"{settings.API_V1_STR}/honeypots/", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    assert any(h["id"] == honeypot_id for h in items)

    # 4. Terminate Honeypot
    r = client.delete(f"{settings.API_V1_STR}/honeypots/{honeypot_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["message"] == "Honeypot terminated successfully"
