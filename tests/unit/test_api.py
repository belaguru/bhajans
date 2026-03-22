"""
Unit tests for API endpoints.

These tests verify basic API endpoint functionality.
Uses test fixtures to ensure isolation from production database.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def test_health_check(client):
    """Test health check endpoint returns 200"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_api_bhajans_list_empty(client):
    """Test bhajans API returns empty list when no bhajans exist"""
    response = client.get("/api/bhajans")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_api_bhajans_list_with_data(client, sample_bhajans):
    """Test bhajans API returns bhajans when they exist"""
    response = client.get("/api/bhajans")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_api_search_no_results(client):
    """Test search API returns empty list for non-matching query"""
    response = client.get("/api/search?q=NonExistentBhajan")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_api_search_with_results(client, sample_bhajans):
    """Test search API returns results for matching query"""
    response = client.get("/api/search?q=Krishna")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any("Krishna" in b["title"] for b in data)


def test_api_stats_empty(client):
    """Test stats API returns zero count when no bhajans"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bhajans"] == 0
    assert data["status"] == "online"


def test_api_stats_with_data(client, sample_bhajans):
    """Test stats API returns correct count"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bhajans"] == 3


def test_api_get_bhajan_not_found(client):
    """Test getting non-existent bhajan returns 404"""
    response = client.get("/api/bhajans/99999")
    assert response.status_code == 404


def test_api_get_bhajan_exists(client, sample_bhajan):
    """Test getting existing bhajan returns it"""
    response = client.get(f"/api/bhajans/{sample_bhajan.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_bhajan.id
    assert data["title"] == sample_bhajan.title
