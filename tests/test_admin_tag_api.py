"""
Test Admin Tag Management API.

These tests verify tag CRUD operations work correctly.
Uses test fixtures to ensure isolation from production database.
"""
import pytest
import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from conftest import unique_name


class TestAdminTagAPI:
    """Test suite for admin tag management operations"""
    
    def test_create_tag_root_level(self, client, test_db):
        """Test creating a root-level tag"""
        tag_name = unique_name("TestDeity")
        response = client.post("/api/tags", json={
            "name": tag_name,
            "category": "deity",
            "translations": {
                "kannada": "ಟೆಸ್ಟ್",
                "hindi": "टेस्ट"
            },
            "synonyms": [unique_name("TestAlias")]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == tag_name
        assert "message" in data
    
    def test_create_tag_duplicate_name(self, client, sample_tag_taxonomy):
        """Test that duplicate tag names are rejected"""
        # Try to create tag with existing name (Hanuman from fixture)
        response = client.post("/api/tags", json={
            "name": "Hanuman",
            "category": "type"
        })
        
        assert response.status_code == 400
        detail = response.json().get("detail", response.json().get("error", ""))
        assert "already exists" in detail
    
    def test_create_tag_with_parent(self, client, sample_tag_taxonomy):
        """Test creating a child tag"""
        parent_id = sample_tag_taxonomy["vishnu"].id
        child_name = unique_name("ChildTag")
        
        response = client.post("/api/tags", json={
            "name": child_name,
            "category": "deity",
            "parent_id": parent_id
        })
        
        assert response.status_code == 200
        
        # Verify child has correct parent
        tag_id = response.json()["id"]
        detail_response = client.get(f"/api/tags/{tag_id}")
        assert detail_response.status_code == 200
        tag_data = detail_response.json()
        assert tag_data["parent_id"] == parent_id
        assert tag_data["level"] == 2  # Vishnu is level 1
    
    def test_create_tag_invalid_parent(self, client, test_db):
        """Test creating tag with non-existent parent returns 404"""
        response = client.post("/api/tags", json={
            "name": unique_name("OrphanTag"),
            "category": "deity",
            "parent_id": 99999
        })
        
        assert response.status_code == 404
        detail = response.json().get("detail", response.json().get("error", ""))
        assert "Parent tag not found" in detail
    
    def test_update_tag_name(self, client, test_db):
        """Test updating tag name"""
        old_name = unique_name("OldName")
        new_name = unique_name("NewName")
        
        # Create tag
        create_response = client.post("/api/tags", json={
            "name": old_name,
            "category": "type"
        })
        tag_id = create_response.json()["id"]
        
        # Update name
        response = client.put(f"/api/tags/{tag_id}", json={
            "name": new_name
        })
        
        assert response.status_code == 200
        
        # Verify update
        detail_response = client.get(f"/api/tags/{tag_id}")
        assert detail_response.json()["name"] == new_name
    
    def test_update_tag_translations(self, client, test_db):
        """Test updating tag translations"""
        # Create tag
        create_response = client.post("/api/tags", json={
            "name": unique_name("TranslationTest"),
            "category": "deity",
            "translations": {"kannada": "ಹಳೆಯ"}
        })
        tag_id = create_response.json()["id"]
        
        # Update translations
        response = client.put(f"/api/tags/{tag_id}", json={
            "translations": {
                "kannada": "ಹೊಸ",
                "hindi": "नया"
            }
        })
        
        assert response.status_code == 200
        
        # Verify update
        detail_response = client.get(f"/api/tags/{tag_id}")
        translations = detail_response.json()["translations"]
        assert translations["kannada"] == "ಹೊಸ"
        assert translations["hindi"] == "नया"
    
    def test_update_tag_synonyms(self, client, test_db):
        """Test updating tag synonyms"""
        # Create tag with unique synonyms
        old_syn = unique_name("OldSyn")
        new_syn1 = unique_name("NewSyn1")
        new_syn2 = unique_name("NewSyn2")
        
        create_response = client.post("/api/tags", json={
            "name": unique_name("SynonymTest"),
            "category": "deity",
            "synonyms": [old_syn]
        })
        tag_id = create_response.json()["id"]
        
        # Update synonyms
        response = client.put(f"/api/tags/{tag_id}", json={
            "synonyms": [new_syn1, new_syn2]
        })
        
        assert response.status_code == 200
        
        # Verify update
        detail_response = client.get(f"/api/tags/{tag_id}")
        synonyms = detail_response.json()["synonyms"]
        assert new_syn1 in synonyms
        assert new_syn2 in synonyms
        assert old_syn not in synonyms
    
    def test_update_tag_parent(self, client, test_db):
        """Test changing tag parent (reparenting)"""
        # Create parent tags
        parent1_response = client.post("/api/tags", json={
            "name": unique_name("Parent1"),
            "category": "deity"
        })
        parent1_id = parent1_response.json()["id"]
        
        parent2_response = client.post("/api/tags", json={
            "name": unique_name("Parent2"),
            "category": "deity"
        })
        parent2_id = parent2_response.json()["id"]
        
        # Create child under parent1
        child_response = client.post("/api/tags", json={
            "name": unique_name("MovingChild"),
            "category": "deity",
            "parent_id": parent1_id
        })
        child_id = child_response.json()["id"]
        
        # Move child to parent2
        response = client.put(f"/api/tags/{child_id}", json={
            "parent_id": parent2_id
        })
        
        assert response.status_code == 200
        
        # Verify new parent
        detail_response = client.get(f"/api/tags/{child_id}")
        assert detail_response.json()["parent_id"] == parent2_id
    
    def test_update_nonexistent_tag(self, client, test_db):
        """Test updating non-existent tag returns 404"""
        response = client.put("/api/tags/99999", json={
            "name": "DoesntMatter"
        })
        
        assert response.status_code == 404
    
    def test_delete_unused_tag(self, client, test_db):
        """Test deleting tag not used by any bhajans"""
        # Create tag
        create_response = client.post("/api/tags", json={
            "name": unique_name("DeleteMe"),
            "category": "type"
        })
        tag_id = create_response.json()["id"]
        
        # Delete tag
        response = client.delete(f"/api/tags/{tag_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify deletion
        detail_response = client.get(f"/api/tags/{tag_id}")
        assert detail_response.status_code == 404
    
    def test_delete_tag_with_children(self, client, test_db):
        """Test that tag with children cannot be deleted"""
        # Create parent
        parent_response = client.post("/api/tags", json={
            "name": unique_name("ParentWithChild"),
            "category": "deity"
        })
        parent_id = parent_response.json()["id"]
        
        # Create child
        client.post("/api/tags", json={
            "name": unique_name("ChildOfParent"),
            "category": "deity",
            "parent_id": parent_id
        })
        
        # Try to delete parent
        response = client.delete(f"/api/tags/{parent_id}")
        
        assert response.status_code == 400
        detail = response.json().get("detail", response.json().get("error", ""))
        assert "child tag" in detail.lower()
    
    def test_delete_nonexistent_tag(self, client, test_db):
        """Test deleting non-existent tag returns 404"""
        response = client.delete("/api/tags/99999")
        
        assert response.status_code == 404
    
    def test_tag_hierarchy_after_operations(self, client, test_db):
        """Test that tag hierarchy is maintained correctly after CRUD operations"""
        # Create hierarchy: Root -> Level1 -> Level2
        root_response = client.post("/api/tags", json={
            "name": unique_name("HierarchyRoot"),
            "category": "deity"
        })
        root_id = root_response.json()["id"]
        
        level1_response = client.post("/api/tags", json={
            "name": unique_name("HierarchyLevel1"),
            "category": "deity",
            "parent_id": root_id
        })
        level1_id = level1_response.json()["id"]
        
        level2_response = client.post("/api/tags", json={
            "name": unique_name("HierarchyLevel2"),
            "category": "deity",
            "parent_id": level1_id
        })
        level2_id = level2_response.json()["id"]
        
        # Verify levels
        root_data = client.get(f"/api/tags/{root_id}").json()
        level1_data = client.get(f"/api/tags/{level1_id}").json()
        level2_data = client.get(f"/api/tags/{level2_id}").json()
        
        assert root_data["level"] == 0
        assert level1_data["level"] == 1
        assert level2_data["level"] == 2
        
        # Verify parent-child relationships
        assert level1_data["parent"]["id"] == root_id
        assert level2_data["parent"]["id"] == level1_id
        assert any(c["id"] == level1_id for c in root_data["children"])
        assert any(c["id"] == level2_id for c in level1_data["children"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
