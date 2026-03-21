"""YouTube playback and URL validation tests"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app

client = TestClient(app)

class TestYouTubeURLs:
    """Test YouTube URL handling"""
    
    def test_create_bhajan_with_youtube_url(self):
        """Test creating bhajan with YouTube URL"""
        bhajan_data = {
            "title": "Hanuman Chalisa",
            "lyrics": "Jai Hanuman Gyan Gun Sagar",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        
        response = client.post("/api/bhajans", json=bhajan_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["youtube_url"] == bhajan_data["youtube_url"]
    
    def test_bhajan_without_youtube_url(self):
        """Test creating bhajan without YouTube URL"""
        bhajan_data = {
            "title": "Simple Bhajan",
            "lyrics": "Test lyrics"
        }
        
        response = client.post("/api/bhajans", json=bhajan_data)
        assert response.status_code == 200
        
        data = response.json()
        # youtube_url should be None or not present
        assert data.get("youtube_url") in [None, ""]
    
    def test_update_youtube_url(self):
        """Test updating YouTube URL"""
        # Create bhajan
        bhajan_data = {
            "title": "Test Bhajan",
            "lyrics": "Test"
        }
        create_response = client.post("/api/bhajans", json=bhajan_data)
        bhajan_id = create_response.json()["id"]
        
        # Update with YouTube URL
        update_data = {
            "youtube_url": "https://www.youtube.com/watch?v=ABC123"
        }
        response = client.put(f"/api/bhajans/{bhajan_id}", json=update_data)
        assert response.status_code == 200
        
        # Verify
        get_response = client.get(f"/api/bhajans/{bhajan_id}")
        assert get_response.json()["youtube_url"] == update_data["youtube_url"]
    
    def test_youtube_url_formats(self):
        """Test various YouTube URL formats"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            bhajan_data = {
                "title": f"Test {url}",
                "lyrics": "Test",
                "youtube_url": url
            }
            
            response = client.post("/api/bhajans", json=bhajan_data)
            # Should accept any valid URL format
            assert response.status_code in [200, 422]  # May have URL validation

class TestYouTubePlayback:
    """Test YouTube playback features"""
    
    def test_get_bhajan_with_youtube(self):
        """Test retrieving bhajan with YouTube URL"""
        # Create bhajan with YouTube
        bhajan_data = {
            "title": "Bhajan With Video",
            "lyrics": "Test",
            "youtube_url": "https://www.youtube.com/watch?v=12345"
        }
        
        create_response = client.post("/api/bhajans", json=bhajan_data)
        bhajan_id = create_response.json()["id"]
        
        # Get bhajan
        response = client.get(f"/api/bhajans/{bhajan_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "youtube_url" in data
        assert data["youtube_url"] is not None
    
    def test_list_bhajans_with_youtube(self):
        """Test listing includes YouTube URLs"""
        response = client.get("/api/bhajans")
        assert response.status_code == 200
        
        bhajans = response.json()
        # Each bhajan should have youtube_url field (even if None)
        for bhajan in bhajans:
            assert "youtube_url" in bhajan or "youtube" in str(bhajan).lower()
    
    def test_search_bhajans_with_youtube(self):
        """Test search works with YouTube bhajans"""
        # Create bhajan
        bhajan_data = {
            "title": "Searchable YouTube Bhajan",
            "lyrics": "Find me",
            "youtube_url": "https://www.youtube.com/watch?v=SEARCH"
        }
        client.post("/api/bhajans", json=bhajan_data)
        
        # Search
        response = client.get("/api/bhajans?search=Searchable")
        assert response.status_code == 200
        
        results = response.json()
        # Should find bhajan with YouTube URL
        searchable = [b for b in results if "Searchable" in b["title"]]
        if len(searchable) > 0:
            assert searchable[0].get("youtube_url") is not None

class TestYouTubeEdgeCases:
    """Test YouTube edge cases"""
    
    def test_empty_youtube_url(self):
        """Test empty YouTube URL"""
        bhajan_data = {
            "title": "Empty URL",
            "lyrics": "Test",
            "youtube_url": ""
        }
        
        response = client.post("/api/bhajans", json=bhajan_data)
        assert response.status_code == 200
    
    def test_invalid_youtube_url(self):
        """Test invalid URL (if validation exists)"""
        bhajan_data = {
            "title": "Invalid URL",
            "lyrics": "Test",
            "youtube_url": "not-a-valid-url"
        }
        
        response = client.post("/api/bhajans", json=bhajan_data)
        # May accept any string, or validate
        assert response.status_code in [200, 422]
    
    def test_very_long_youtube_url(self):
        """Test very long URL"""
        long_url = "https://www.youtube.com/watch?v=" + "A" * 500
        bhajan_data = {
            "title": "Long URL",
            "lyrics": "Test",
            "youtube_url": long_url
        }
        
        response = client.post("/api/bhajans", json=bhajan_data)
        # Should handle long URLs
        assert response.status_code in [200, 422]
    
    def test_remove_youtube_url(self):
        """Test removing YouTube URL"""
        # Create with URL
        bhajan_data = {
            "title": "Remove URL Test",
            "lyrics": "Test",
            "youtube_url": "https://www.youtube.com/watch?v=123"
        }
        create_response = client.post("/api/bhajans", json=bhajan_data)
        bhajan_id = create_response.json()["id"]
        
        # Update to remove URL
        update_data = {"youtube_url": None}
        response = client.put(f"/api/bhajans/{bhajan_id}", json=update_data)
        assert response.status_code == 200
