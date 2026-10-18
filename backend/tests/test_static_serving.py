import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fastapi_serves_frontend_spa():
    # Calling root "/" should serve the built React index.html
    response = client.get("/")
    assert response.status_code == 200
    assert "ResumeIQ" in response.text
    assert 'id="root"' in response.text

def test_fastapi_serves_api_health():
    # Calling /api/health still hits the API correctly
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
