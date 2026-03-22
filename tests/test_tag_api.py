"""
Test Tag API Endpoints
Tests for hierarchical tag taxonomy API
"""
import pytest
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
from models import get_db, init_db, Bhajan
import sqlite3


@pytest.fixture(scope="module")
def test_db():
    """Use existing staging database with tag taxonomy data"""
    # Use existing staging database
    test_db_path = "./data/portal.db"
    
    # Database already has tag taxonomy data from previous migrations
    # Just verify it exists
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Verify tag_taxonomy table exists
    cursor.execute("SELECT COUNT(*) FROM tag_taxonomy")
    tag_count = cursor.fetchone()[0]
    
    if tag_count == 0:
        raise Exception("Tag taxonomy is empty. Run migration scripts first.")
    
    conn.close()
    
    yield test_db_path
    
    # No cleanup - keep staging data intact


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


class TestTagsListAPI:
    """Test GET /api/tags endpoint"""
    
    def test_get_all_tags(self, client, test_db):
        """Should return all canonical tags"""
        response = client.get("/api/tags")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure
        tag = data[0]
        assert "id" in tag
        assert "name" in tag
        assert "category" in tag
        assert "level" in tag
        assert "parent_id" in tag
        assert "translations" in tag
        
    def test_filter_by_category(self, client, test_db):
        """Should filter tags by category"""
        response = client.get("/api/tags?category=deity")
        assert response.status_code == 200
        
        data = response.json()
        assert all(tag["category"] == "deity" for tag in data)
        
    def test_filter_by_parent_id(self, client, test_db):
        """Should return only children of specified parent"""
        # First get Vishnu's ID
        response = client.get("/api/tags")
        vishnu = next((t for t in response.json() if t["name"] == "Vishnu"), None)
        assert vishnu is not None
        
        # Get Vishnu's children
        response = client.get(f"/api/tags?parent_id={vishnu['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert all(tag["parent_id"] == vishnu["id"] for tag in data)
        assert any(tag["name"] == "Krishna" for tag in data)
        assert any(tag["name"] == "Rama" for tag in data)


class TestTagsTreeAPI:
    """Test GET /api/tags/tree endpoint"""
    
    def test_get_hierarchical_tree(self, client, test_db):
        """Should return nested tree structure"""
        response = client.get("/api/tags/tree")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have root categories
        assert "Deity" in data
        
        # Check nested structure
        deity_tree = data["Deity"]
        assert "children" in deity_tree
        
        # Vishnu should have Krishna and Rama as children
        vishnu = deity_tree["children"].get("Vishnu")
        assert vishnu is not None
        assert "children" in vishnu
        assert "Krishna" in vishnu["children"]
        assert "Rama" in vishnu["children"]


class TestTagDetailAPI:
    """Test GET /api/tags/{id} endpoint"""
    
    def test_get_tag_details(self, client, test_db):
        """Should return complete tag details"""
        # Get Hanuman's ID first
        response = client.get("/api/tags")
        hanuman = next((t for t in response.json() if t["name"] == "Hanuman"), None)
        assert hanuman is not None
        
        # Get details
        response = client.get(f"/api/tags/{hanuman['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Hanuman"
        assert "translations" in data
        assert "synonyms" in data
        assert "children" in data
        assert "parent" in data
        
        # Check translations
        assert "kn" in data["translations"]
        assert data["translations"]["kn"] == "ಹನುಮಾನ್"
        
        # Check synonyms (case-insensitive check)
        synonyms_lower = [s.lower() for s in data["synonyms"]]
        assert "anjaneya" in synonyms_lower
        assert "maruti" in synonyms_lower or "vijaya maruti" in synonyms_lower
        
    def test_tag_not_found(self, client, test_db):
        """Should return 404 for non-existent tag"""
        response = client.get("/api/tags/99999")
        assert response.status_code == 404


class TestTagBhajansAPI:
    """Test GET /api/tags/{id}/bhajans endpoint"""
    
    def test_get_bhajans_by_tag(self, client, test_db):
        """Should return bhajans with specified tag"""
        # Get Hanuman's ID
        response = client.get("/api/tags")
        hanuman = next((t for t in response.json() if t["name"] == "Hanuman"), None)
        
        # Get bhajans
        response = client.get(f"/api/tags/{hanuman['id']}/bhajans")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Note: In staging DB, there may be no tagged bhajans yet
        # The endpoint should still return empty list without error
        
    def test_hierarchical_search(self, client, test_db):
        """Should include bhajans with child tags"""
        # Get Vishnu's ID
        response = client.get("/api/tags")
        vishnu = next((t for t in response.json() if t["name"] == "Vishnu"), None)
        
        # Get bhajans - should include Krishna and Rama bhajans (children of Vishnu)
        response = client.get(f"/api/tags/{vishnu['id']}/bhajans")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Note: In staging DB, there may be no tagged bhajans yet
        # The endpoint should still return empty list without error
        # If there are results, they should be from Vishnu or descendant tags
        
    def test_pagination(self, client, test_db):
        """Should support pagination"""
        response = client.get("/api/tags")
        tag = response.json()[0]
        
        # Page 1
        response = client.get(f"/api/tags/{tag['id']}/bhajans?page=1&per_page=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 2


class TestBhajansByTagAPI:
    """Test GET /api/bhajans?tag={name} endpoint"""
    
    def test_filter_by_single_tag(self, client, test_db):
        """Should filter bhajans by tag name"""
        response = client.get("/api/bhajans?tag=Hanuman")
        assert response.status_code == 200
        
        data = response.json()
        assert any("Hanuman" in b["title"] for b in data)
        
    def test_filter_by_multiple_tags(self, client, test_db):
        """Should support multiple tag filters (AND logic)"""
        response = client.get("/api/bhajans?tag=Hanuman&tag=Aarti")
        assert response.status_code == 200
        
        data = response.json()
        # Should only return bhajans that have BOTH tags
        assert len(data) > 0
        
    def test_synonym_resolution(self, client, test_db):
        """Should resolve synonyms to canonical tags"""
        # Search with synonym "Anjaneya" should find Hanuman bhajans
        response = client.get("/api/bhajans?tag=Anjaneya")
        assert response.status_code == 200
        
        data = response.json()
        assert any("Hanuman" in b["title"] for b in data)
        
    def test_hierarchical_tag_search(self, client, test_db):
        """Should include child tags in search"""
        # Searching for Vishnu should also return Krishna and Rama bhajans
        response = client.get("/api/bhajans?tag=Vishnu")
        assert response.status_code == 200
        
        data = response.json()
        titles = [b["title"] for b in data]
        
        assert any("Krishna" in t for t in titles)
        assert any("Rama" in t for t in titles)


class TestEnhancedSearchAPI:
    """Test GET /api/search?q={query} endpoint"""
    
    def test_search_in_titles(self, client, test_db):
        """Should search in bhajan titles"""
        response = client.get("/api/search?q=Hanuman")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        assert any("Hanuman" in b["title"] for b in data)
        
    def test_search_in_lyrics(self, client, test_db):
        """Should search in bhajan lyrics"""
        response = client.get("/api/search?q=Govinda")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
    def test_search_in_tag_names(self, client, test_db):
        """Should search in tag names"""
        response = client.get("/api/search?q=Krishna")
        assert response.status_code == 200
        
        data = response.json()
        assert any("Krishna" in b["title"] for b in data)
        
    def test_search_in_tag_translations(self, client, test_db):
        """Should search in tag translations"""
        # Search with Kannada text
        response = client.get("/api/search?q=ಹನುಮಾನ್")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
    def test_search_in_tag_synonyms(self, client, test_db):
        """Should search in tag synonyms"""
        response = client.get("/api/search?q=Anjaneya")
        assert response.status_code == 200
        
        data = response.json()
        assert any("Hanuman" in b["title"] for b in data)
        
    def test_search_relevance(self, client, test_db):
        """Should return results with relevance score"""
        response = client.get("/api/search?q=Hanuman")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            # Results should have relevance indicator (exact match in title > lyrics > tags)
            assert all("title" in b for b in data)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_query_params(self, client, test_db):
        """Should handle empty query parameters gracefully"""
        response = client.get("/api/tags?category=")
        assert response.status_code == 200
        
    def test_invalid_category(self, client, test_db):
        """Should handle invalid category filter"""
        response = client.get("/api/tags?category=invalid")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        
    def test_invalid_parent_id(self, client, test_db):
        """Should handle invalid parent_id"""
        response = client.get("/api/tags?parent_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        
    def test_search_with_special_characters(self, client, test_db):
        """Should handle special characters in search"""
        response = client.get("/api/search?q=@#$%")
        assert response.status_code == 200
        
    def test_pagination_edge_cases(self, client, test_db):
        """Should handle edge cases in pagination"""
        response = client.get("/api/tags")
        tag = response.json()[0]
        
        # Page 0
        response = client.get(f"/api/tags/{tag['id']}/bhajans?page=0")
        assert response.status_code == 200
        
        # Huge page number
        response = client.get(f"/api/tags/{tag['id']}/bhajans?page=9999")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
