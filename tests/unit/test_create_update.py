"""
Test CREATE and UPDATE operations using Form data (actual API).

These tests verify CRUD operations work correctly.
Uses test fixtures to ensure isolation from production database.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCreateBhajan:
    """Test creating bhajans using Form data (multipart/form-data)"""
    
    def test_create_bhajan_minimal(self, client):
        """Test creating bhajan with minimal required fields"""
        form_data = {
            "title": "Test Bhajan Minimal",
            "lyrics": "Om Namah Shivaya Om Namah Shivaya"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Bhajan Minimal"
        assert "id" in data
    
    def test_create_bhajan_with_tags(self, client):
        """Test creating bhajan with tags"""
        form_data = {
            "title": "Tagged Bhajan Test",
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva",
            "tags": "devotional,rama"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "devotional" in data["tags"] or "rama" in data["tags"]
    
    def test_create_bhajan_with_youtube(self, client):
        """Test creating bhajan with YouTube URL"""
        form_data = {
            "title": "YouTube Bhajan Test",
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva",
            "youtube_url": "https://www.youtube.com/watch?v=test123"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["youtube_url"] == "https://www.youtube.com/watch?v=test123"
    
    def test_create_bhajan_with_uploader(self, client):
        """Test creating bhajan with uploader name"""
        form_data = {
            "title": "Named Uploader Test",
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva",
            "uploader_name": "Test User"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["uploader_name"] == "Test User"
    
    def test_create_bhajan_missing_title(self, client):
        """Test validation: missing title returns 422"""
        form_data = {
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_bhajan_missing_lyrics(self, client):
        """Test validation: missing lyrics returns 422"""
        form_data = {
            "title": "Test Bhajan"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 422  # Validation error


class TestUpdateBhajan:
    """Test updating bhajans"""
    
    def test_update_bhajan_title(self, client, sample_bhajan):
        """Test updating bhajan title"""
        form_data = {
            "title": "Updated Title Test"
        }
        
        response = client.put(f"/api/bhajans/{sample_bhajan.id}", data=form_data)
        assert response.status_code == 200
        
        # Verify update
        get_response = client.get(f"/api/bhajans/{sample_bhajan.id}")
        assert get_response.json()["title"] == "Updated Title Test"
    
    def test_update_bhajan_lyrics(self, client, sample_bhajan):
        """Test updating bhajan lyrics"""
        form_data = {
            "lyrics": "Updated lyrics with at least 20 characters"
        }
        
        response = client.put(f"/api/bhajans/{sample_bhajan.id}", data=form_data)
        assert response.status_code == 200
    
    def test_update_bhajan_youtube(self, client, sample_bhajan):
        """Test updating YouTube URL"""
        form_data = {
            "youtube_url": "https://www.youtube.com/watch?v=UPDATED"
        }
        
        response = client.put(f"/api/bhajans/{sample_bhajan.id}", data=form_data)
        assert response.status_code == 200
        
        # Verify
        get_response = client.get(f"/api/bhajans/{sample_bhajan.id}")
        assert get_response.json()["youtube_url"] == "https://www.youtube.com/watch?v=UPDATED"
    
    def test_update_nonexistent_bhajan(self, client):
        """Test updating bhajan that doesn't exist returns 404"""
        form_data = {
            "title": "Should Fail"
        }
        
        response = client.put("/api/bhajans/999999", data=form_data)
        assert response.status_code == 404


class TestDeleteBhajan:
    """Test deleting bhajans"""
    
    def test_delete_bhajan(self, client):
        """Test soft-deleting a bhajan"""
        # Create a bhajan first
        form_data = {
            "title": "To Delete Test",
            "lyrics": "Om Namah Shivaya Will be deleted soon"
        }
        create_response = client.post("/api/bhajans", data=form_data)
        bhajan_id = create_response.json()["id"]
        
        # Delete
        delete_response = client.delete(f"/api/bhajans/{bhajan_id}")
        assert delete_response.status_code == 200
        
        # Verify deleted (should 404)
        get_response = client.get(f"/api/bhajans/{bhajan_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_bhajan(self, client):
        """Test deleting bhajan that doesn't exist returns 404"""
        response = client.delete("/api/bhajans/999999")
        assert response.status_code == 404


class TestFormDataEdgeCases:
    """Test edge cases for Form data"""
    
    def test_empty_tags(self, client):
        """Test creating with empty tags string"""
        form_data = {
            "title": "No Tags Test",
            "lyrics": "Om Namah Shivaya Jai",
            "tags": ""
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        assert response.json()["tags"] == []
    
    def test_special_characters_in_title(self, client):
        """Test special characters in title"""
        form_data = {
            "title": "ಗುರುವೇ ಗತಿ - Guruve Gati Test",
            "lyrics": "Om Namah Shivaya Jai"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        assert "ಗುರುವೇ" in response.json()["title"]
    
    def test_very_long_lyrics(self, client):
        """Test creating bhajan with very long lyrics"""
        long_lyrics = "Om Namah Shivaya " * 1000  # 16,000 chars
        
        form_data = {
            "title": "Long Bhajan Test",
            "lyrics": long_lyrics
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
