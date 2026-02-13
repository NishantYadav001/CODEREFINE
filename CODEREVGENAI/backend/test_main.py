from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_login_success():
    """Test successful login with demo credentials"""
    payload = {"username": "admin", "password": "password"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_failure():
    """Test login with invalid credentials"""
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_pwa_files():
    """Test PWA manifest and service worker availability"""
    # Test Manifest
    response = client.get("/manifest.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    # Test Service Worker
    response = client.get("/sw.js")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/javascript"

def test_ui_routes_exist():
    """Test that all UI routes return 200 and HTML"""
    routes = [
        "app", "dashboard", "login", "admin", "batch", 
        "collab", "profile", "reports", "settings",
        "help", "landing", "generate", "status", "signup"
    ]
    for route in routes:
        response = client.get(f"/{route}")
        assert response.status_code == 200, f"Route /{route} failed"
        assert "text/html" in response.headers["content-type"]

def test_root_route():
    """Test root route serves landing page"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]