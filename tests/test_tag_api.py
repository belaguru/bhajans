"""
Test Tag API Endpoints.

Tests for hierarchical tag taxonomy API.
Uses test fixtures for isolated database testing.
"""
import pytest
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTagsListAPI:
    """Test GET /api/tags endpoint"""
    
    def test_get_all_tags_empty(self, client, test_db):
        """Should return empty list when no tags exist"""
        response = client.get("/api/tags")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_all_tags_with_data(self, client, sample_tag_taxonomy):
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
    
    def test_filter_by_category(self, client, sample_tag_taxonomy):
        """Should filter tags by category"""
        response = client.get("/api/tags?category=deity")
        assert response.status_code == 200
        
        data = response.json()
        assert all(tag["category"] == "deity" for tag in data)
    
    def test_filter_by_parent_id(self, client, sample_tag_taxonomy):
        """Should return only children of specified parent"""
        vishnu_id = sample_tag_taxonomy["vishnu"].id
        
        # Get Vishnu's children
        response = client.get(f"/api/tags?parent_id={vishnu_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert all(tag["parent_id"] == vishnu_id for tag in data)
        assert any(tag["name"] == "Krishna" for tag in data)
        assert any(tag["name"] == "Rama" for tag in data)


class TestTagsTreeAPI:
    """Test GET /api/tags/tree endpoint"""
    
    def test_get_hierarchical_tree(self, client, sample_tag_taxonomy):
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
    
    def test_get_tag_details(self, client, sample_tag_taxonomy):
        """Should return complete tag details"""
        hanuman_id = sample_tag_taxonomy["hanuman"].id
        
        # Get details
        response = client.get(f"/api/tags/{hanuman_id}")
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
        
        # Check synonyms
        synonyms_lower = [s.lower() for s in data["synonyms"]]
        assert "anjaneya" in synonyms_lower
        assert "maruti" in synonyms_lower
    
    def test_tag_not_found(self, client, test_db):
        """Should return 404 for non-existent tag"""
        response = client.get("/api/tags/99999")
        assert response.status_code == 404


class TestTagBhajansAPI:
    """Test GET /api/tags/{id}/bhajans endpoint"""
    
    def test_get_bhajans_by_tag_empty(self, client, sample_tag_taxonomy):
        """Should return empty list when no bhajans have tag"""
        hanuman_id = sample_tag_taxonomy["hanuman"].id
        
        response = client.get(f"/api/tags/{hanuman_id}/bhajans")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_bhajans_by_tag_with_data(self, client, sample_bhajan_with_tags, sample_tag_taxonomy):
        """Should return bhajans with specified tag"""
        hanuman_id = sample_tag_taxonomy["hanuman"].id
        
        response = client.get(f"/api/tags/{hanuman_id}/bhajans")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_pagination(self, client, sample_tag_taxonomy):
        """Should support pagination"""
        hanuman_id = sample_tag_taxonomy["hanuman"].id
        
        # Page 1
        response = client.get(f"/api/tags/{hanuman_id}/bhajans?page=1&per_page=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 2


class TestEnhancedSearchAPI:
    """Test GET /api/search?q={query} endpoint"""
    
    def test_search_no_results(self, client, test_db):
        """Should return empty list for no matches"""
        response = client.get("/api/search?q=NonExistentTerm")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0
    
    def test_search_in_titles(self, client, sample_bhajans):
        """Should search in bhajan titles"""
        response = client.get("/api/search?q=Hanuman")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        assert any("Hanuman" in b["title"] for b in data)
    
    def test_search_in_lyrics(self, client, sample_bhajans):
        """Should search in bhajan lyrics"""
        response = client.get("/api/search?q=Krishna")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
    
    def test_search_with_relevance(self, client, sample_bhajans):
        """Should return results with relevance score when present"""
        response = client.get("/api/search?q=Hanuman")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            # Results should have title
            assert all("title" in b for b in data)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_query_params(self, client, test_db):
        """Should handle empty query parameters gracefully"""
        response = client.get("/api/tags?category=")
        assert response.status_code == 200
    
    def test_invalid_category(self, client, sample_tag_taxonomy):
        """Should handle invalid category filter"""
        response = client.get("/api/tags?category=invalid")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_invalid_parent_id(self, client, sample_tag_taxonomy):
        """Should handle invalid parent_id"""
        response = client.get("/api/tags?parent_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_search_with_special_characters(self, client, test_db):
        """Should handle special characters in search"""
        response = client.get("/api/search?q=@#$%")
        assert response.status_code == 200
    
    def test_pagination_edge_cases(self, client, sample_tag_taxonomy):
        """Should handle edge cases in pagination"""
        hanuman_id = sample_tag_taxonomy["hanuman"].id
        
        # Page 0
        response = client.get(f"/api/tags/{hanuman_id}/bhajans?page=0")
        assert response.status_code == 200
        
        # Huge page number
        response = client.get(f"/api/tags/{hanuman_id}/bhajans?page=9999")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_short_search_query(self, client, test_db):
        """Should handle very short search queries"""
        response = client.get("/api/search?q=a")
        # May return empty or error depending on implementation
        assert response.status_code in [200, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
