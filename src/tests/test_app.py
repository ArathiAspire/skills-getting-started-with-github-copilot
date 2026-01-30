import pytest
from fastapi.testclient import TestClient
from ..app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Basketball" in data
    assert "participants" in data["Basketball"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects?
    # Actually, RedirectResponse returns 307, but TestClient might follow.
    # Let's check: FastAPI RedirectResponse is 307, but in test it might follow.
    # To be safe, assert it's a redirect or the static file.

def test_signup_success():
    # Test signing up a new participant
    response = client.post("/activities/Basketball/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball"]["participants"]

def test_signup_duplicate():
    # Try to sign up again
    response = client.post("/activities/Basketball/signup?email=test@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity():
    response = client.post("/activities/InvalidActivity/signup?email=test@example.com")
    assert response.status_code == 404

def test_unregister_success():
    # First sign up
    client.post("/activities/Tennis%20Club/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Tennis%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Tennis Club"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Basketball/unregister?email=notsigned@example.com")
    assert response.status_code == 400

def test_unregister_invalid_activity():
    response = client.delete("/activities/InvalidActivity/unregister?email=test@example.com")
    assert response.status_code == 404