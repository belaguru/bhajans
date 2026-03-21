"""Test CREATE and UPDATE operations using Form data (actual API)"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app

client = TestClient(app)


class TestCreateBhajan:
    """Test creating bhajans using Form data (multipart/form-data)"""
    
    def test_create_bhajan_minimal(self):
        """Test creating bhajan with minimal required fields"""
        form_data = {
            "title": "Test Bhajan",
            "lyrics": "Om Namah Shivaya Om Namah Shivaya"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Bhajan"
        assert "id" in data
    
    def test_create_bhajan_with_tags(self):
        """Test creating bhajan with tags"""
        form_data = {
            "title": "Tagged Bhajan",
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva",
            "tags": "devotional,rama"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "devotional" in data["tags"]
        assert "rama" in data["tags"]
    
    def test_create_bhajan_with_youtube(self):
        """Test creating bhajan with YouTube URL"""
        form_data = {
            "title": "YouTube Bhajan",
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva",
            "youtube_url": "https://www.youtube.com/watch?v=123"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["youtube_url"] == "https://www.youtube.com/watch?v=123"
    
    def test_create_bhajan_with_uploader(self):
        """Test creating bhajan with uploader name"""
        form_data = {
            "title": "Named Uploader",
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva",
            "uploader_name": "Test User"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["uploader_name"] == "Test User"
    
    def test_create_bhajan_missing_title(self):
        """Test validation: missing title"""
        form_data = {
            "lyrics": "Om Namah Shivaya Hara Hara Mahadeva"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_bhajan_missing_lyrics(self):
        """Test validation: missing lyrics"""
        form_data = {
            "title": "Test Bhajan"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 422  # Validation error


class TestUpdateBhajan:
    """Test updating bhajans"""
    
    def setup_method(self):
        """Create a test bhajan before each test"""
        form_data = {
            "title": "Original Title",
            "lyrics": "Om Namah Shivaya Original Bhajan Lyrics Here"
        }
        response = client.post("/api/bhajans", data=form_data)
        self.bhajan_id = response.json()["id"]
    
    def test_update_bhajan_title(self):
        """Test updating bhajan title"""
        form_data = {
            "title": "Updated Title"
        }
        
        response = client.put(f"/api/bhajans/{self.bhajan_id}", data=form_data)
        assert response.status_code == 200
        
        # Verify update
        get_response = client.get(f"/api/bhajans/{self.bhajan_id}")
        assert get_response.json()["title"] == "Updated Title"
    
    def test_update_bhajan_lyrics(self):
        """Test updating bhajan lyrics"""
        form_data = {
            "lyrics": "Updated lyrics"
        }
        
        response = client.put(f"/api/bhajans/{self.bhajan_id}", data=form_data)
        assert response.status_code == 200
    
    def test_update_bhajan_youtube(self):
        """Test updating YouTube URL"""
        form_data = {
            "youtube_url": "https://www.youtube.com/watch?v=NEW"
        }
        
        response = client.put(f"/api/bhajans/{self.bhajan_id}", data=form_data)
        assert response.status_code == 200
        
        # Verify
        get_response = client.get(f"/api/bhajans/{self.bhajan_id}")
        assert get_response.json()["youtube_url"] == "https://www.youtube.com/watch?v=NEW"
    
    def test_update_nonexistent_bhajan(self):
        """Test updating bhajan that doesn't exist"""
        form_data = {
            "title": "Should Fail"
        }
        
        response = client.put("/api/bhajans/999999", data=form_data)
        assert response.status_code == 404


class TestDeleteBhajan:
    """Test deleting bhajans"""
    
    def test_delete_bhajan(self):
        """Test soft-deleting a bhajan"""
        # Create
        form_data = {
            "title": "To Delete",
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
    
    def test_delete_nonexistent_bhajan(self):
        """Test deleting bhajan that doesn't exist"""
        response = client.delete("/api/bhajans/999999")
        assert response.status_code == 404


class TestFormDataEdgeCases:
    """Test edge cases for Form data"""
    
    def test_empty_tags(self):
        """Test creating with empty tags string"""
        form_data = {
            "title": "No Tags",
            "lyrics": "Om Namah Shivaya Jai",
            "tags": ""
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        assert response.json()["tags"] == []
    
    def test_special_characters_in_title(self):
        """Test special characters in title"""
        form_data = {
            "title": "ಗುರುವೇ ಗತಿ - Guruve Gati",
            "lyrics": "Om Namah Shivaya Jai"
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
        assert "ಗುರುವೇ" in response.json()["title"]
    
    def test_very_long_lyrics(self):
        """Test creating bhajan with very long lyrics"""
        long_lyrics = "Om Namah Shivaya " * 1000  # 16,000 chars
        
        form_data = {
            "title": "Long Bhajan",
            "lyrics": long_lyrics
        }
        
        response = client.post("/api/bhajans", data=form_data)
        assert response.status_code == 200
    
    def test_invalid_youtube_url(self):
        """Test with malformed YouTube URL (should still accept)"""
        form_data = {
            "title": "Bad URL",
            "lyrics": "Om Namah Shivaya Jai",
            "youtube_url": "not-a-valid-url"
        }
        
        # API currently accepts any string
        response = client.post("/api/bhajans", data=form_data)
        # Depending on validation, could be 200 or 422
        assert response.status_code in [200, 422]
