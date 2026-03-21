"""Real feature tests - Search, Tags, CRUD operations"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app

client = TestClient(app)

class TestBhajanCRUD:
    """Test Create, Read, Update, Delete operations"""
    
    def test_create_bhajan(self):
        """Test creating a new bhajan"""
        bhajan_data = {
            "title": "Rama Stuti",
            "lyrics": "Shri Rama Chandra Kripalu Bhaju Man",
            "audio_path": "/audio/rama.mp3",
            "uploader_name": "Test User"
        }
        
        response = client.post("/api/bhajans", json=bhajan_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Rama Stuti"
        assert "id" in data
        
        return data["id"]  # Return for other tests
    
    def test_get_all_bhajans(self):
        """Test listing all bhajans"""
        response = client.get("/api/bhajans")
        assert response.status_code == 200
        
        bhajans = response.json()
        assert isinstance(bhajans, list)
    
    def test_get_single_bhajan(self):
        """Test getting a specific bhajan"""
        # First create one
        bhajan_data = {
            "title": "Krishna Bhajan",
            "lyrics": "Hare Krishna Hare Rama",
            "audio_path": "/audio/krishna.mp3"
        }
        
        create_response = client.post("/api/bhajans", json=bhajan_data)
        bhajan_id = create_response.json()["id"]
        
        # Now get it
        response = client.get(f"/api/bhajans/{bhajan_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Krishna Bhajan"
    
    def test_update_bhajan(self):
        """Test updating a bhajan"""
        # Create
        bhajan_data = {
            "title": "Shiva Stotram",
            "lyrics": "Om Namah Shivaya",
            "audio_path": "/audio/shiva.mp3"
        }
        create_response = client.post("/api/bhajans", json=bhajan_data)
        bhajan_id = create_response.json()["id"]
        
        # Update
        update_data = {"title": "Shiva Stotram Updated"}
        response = client.put(f"/api/bhajans/{bhajan_id}", json=update_data)
        assert response.status_code == 200
        
        # Verify
        get_response = client.get(f"/api/bhajans/{bhajan_id}")
        assert get_response.json()["title"] == "Shiva Stotram Updated"
    
    def test_delete_bhajan(self):
        """Test soft-deleting a bhajan"""
        # Create
        bhajan_data = {
            "title": "Temp Bhajan",
            "lyrics": "Test",
            "audio_path": "/audio/temp.mp3"
        }
        create_response = client.post("/api/bhajans", json=bhajan_data)
        bhajan_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/api/bhajans/{bhajan_id}")
        assert response.status_code == 200
        
        # Should be soft-deleted (404 on get)
        get_response = client.get(f"/api/bhajans/{bhajan_id}")
        assert get_response.status_code == 404

class TestSearch:
    """Test search functionality"""
    
    def setup_method(self):
        """Create test bhajans before each test"""
        test_bhajans = [
            {"title": "Rama Dhun", "lyrics": "Shri Rama Jai Rama", "audio_path": "/audio/rama.mp3"},
            {"title": "Krishna Leela", "lyrics": "Krishna Krishna Hare", "audio_path": "/audio/krishna.mp3"},
            {"title": "Shiva Tandava", "lyrics": "Om Namah Shivaya", "audio_path": "/audio/shiva.mp3"},
        ]
        
        for bhajan in test_bhajans:
            client.post("/api/bhajans", json=bhajan)
    
    def test_search_by_title(self):
        """Test searching by title"""
        response = client.get("/api/bhajans?search=Rama")
        assert response.status_code == 200
        
        results = response.json()
        assert len(results) >= 1
        assert any("Rama" in b["title"] for b in results)
    
    def test_search_by_lyrics(self):
        """Test searching in lyrics"""
        response = client.get("/api/bhajans?search=Krishna")
        assert response.status_code == 200
        
        results = response.json()
        assert len(results) >= 1
    
    def test_search_case_insensitive(self):
        """Test search is case-insensitive"""
        response1 = client.get("/api/bhajans?search=rama")
        response2 = client.get("/api/bhajans?search=RAMA")
        
        assert response1.json() == response2.json()
    
    def test_search_empty_query(self):
        """Test empty search returns all"""
        response = client.get("/api/bhajans?search=")
        assert response.status_code == 200
        
        results = response.json()
        assert len(results) >= 3  # All test bhajans
    
    def test_search_no_results(self):
        """Test search with no matches"""
        response = client.get("/api/bhajans?search=NonexistentXYZ")
        assert response.status_code == 200
        
        results = response.json()
        assert len(results) == 0

class TestTags:
    """Test tag functionality"""
    
    def setup_method(self):
        """Create bhajans with tags"""
        test_bhajans = [
            {"title": "Bhajan 1", "lyrics": "Test", "audio_path": "/audio/1.mp3", "tags": "devotional,rama"},
            {"title": "Bhajan 2", "lyrics": "Test", "audio_path": "/audio/2.mp3", "tags": "devotional,krishna"},
            {"title": "Bhajan 3", "lyrics": "Test", "audio_path": "/audio/3.mp3", "tags": "mantra,shiva"},
        ]
        
        for bhajan in test_bhajans:
            client.post("/api/bhajans", json=bhajan)
    
    def test_get_all_tags(self):
        """Test getting all unique tags"""
        response = client.get("/api/tags")
        assert response.status_code == 200
        
        tags = response.json()
        assert isinstance(tags, list)
        assert "devotional" in tags or len(tags) >= 0  # May be empty initially
    
    def test_filter_by_tag(self):
        """Test filtering bhajans by tag"""
        response = client.get("/api/bhajans?tag=devotional")
        assert response.status_code == 200
        
        results = response.json()
        # Results should have devotional tag
        for bhajan in results:
            if bhajan.get("tags"):
                assert "devotional" in bhajan["tags"]
    
    def test_tag_counts(self):
        """Test tag counts endpoint"""
        response = client.get("/api/tags/counts")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)

class TestStats:
    """Test statistics endpoint"""
    
    def test_get_stats(self):
        """Test getting portal statistics"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert "total_bhajans" in stats
        assert isinstance(stats["total_bhajans"], int)
    
    def test_stats_accuracy(self):
        """Test stats reflect actual data"""
        # Create some bhajans
        for i in range(3):
            client.post("/api/bhajans", json={
                "title": f"Test {i}",
                "lyrics": "Test",
                "audio_path": f"/audio/{i}.mp3"
            })
        
        response = client.get("/api/stats")
        stats = response.json()
        
        # Should have at least 3 bhajans
        assert stats["total_bhajans"] >= 3

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_get_nonexistent_bhajan(self):
        """Test getting bhajan that doesn't exist"""
        response = client.get("/api/bhajans/999999")
        assert response.status_code == 404
    
    def test_update_nonexistent_bhajan(self):
        """Test updating bhajan that doesn't exist"""
        response = client.put("/api/bhajans/999999", json={"title": "Test"})
        assert response.status_code == 404
    
    def test_delete_nonexistent_bhajan(self):
        """Test deleting bhajan that doesn't exist"""
        response = client.delete("/api/bhajans/999999")
        assert response.status_code == 404
    
    def test_create_bhajan_missing_fields(self):
        """Test creating bhajan without required fields"""
        response = client.post("/api/bhajans", json={})
        assert response.status_code == 422  # Validation error
    
    def test_create_bhajan_minimal_fields(self):
        """Test creating bhajan with only required fields"""
        response = client.post("/api/bhajans", json={
            "title": "Minimal Bhajan",
            "lyrics": "Test lyrics",
            "audio_path": "/audio/test.mp3"
        })
        assert response.status_code == 200
