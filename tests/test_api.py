"""Tests for URL shortener API"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Database
import os


@pytest.fixture
def client():
    """Create test client"""
    # Use test database
    test_db = Database("test_shortener.db")
    app.state.db = test_db
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    if os.path.exists("test_shortener.db"):
        os.remove("test_shortener.db")


def test_root(client):
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_shorten_url(client):
    """Test URL shortening"""
    response = client.post(
        "/shorten",
        json={"url": "https://example.com"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "short_url" in data
    assert data["original_url"] == "https://example.com/"


def test_shorten_url_with_custom_code(client):
    """Test URL shortening with custom code"""
    response = client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_code": "mylink"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "mylink" in data["short_url"]


def test_duplicate_custom_code(client):
    """Test duplicate custom code returns error"""
    client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_code": "test123"
        }
    )
    
    response = client.post(
        "/shorten",
        json={
            "url": "https://another.com",
            "custom_code": "test123"
        }
    )
    
    assert response.status_code == 400


def test_redirect(client):
    """Test redirect to original URL"""
    # Create short URL
    shorten_response = client.post(
        "/shorten",
        json={"url": "https://example.com"}
    )
    
    short_url = shorten_response.json()["short_url"]
    short_code = short_url.split("/")[-1]
    
    # Test redirect
    response = client.get(f"/{short_code}", follow_redirects=False)
    
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"


def test_redirect_not_found(client):
    """Test redirect with non-existent code"""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_delete_url(client):
    """Test URL deletion"""
    # Create short URL
    shorten_response = client.post(
        "/shorten",
        json={"url": "https://example.com"}
    )
    
    short_url = shorten_response.json()["short_url"]
    short_code = short_url.split("/")[-1]
    
    # Delete it
    response = client.delete(f"/{short_code}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/{short_code}")
    assert response.status_code == 404


def test_get_stats(client):
    """Test getting URL statistics"""
    # Create short URL
    shorten_response = client.post(
        "/shorten",
        json={"url": "https://example.com"}
    )
    
    short_url = shorten_response.json()["short_url"]
    short_code = short_url.split("/")[-1]
    
    # Access it twice
    client.get(f"/{short_code}", follow_redirects=False)
    client.get(f"/{short_code}", follow_redirects=False)
    
    # Check stats
    response = client.get(f"/stats/{short_code}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["clicks"] == 2
    assert data["original_url"] == "https://example.com/"


def test_invalid_url(client):
    """Test invalid URL format"""
    response = client.post(
        "/shorten",
        json={"url": "not-a-valid-url"}
    )
    
    assert response.status_code == 422  # Validation error