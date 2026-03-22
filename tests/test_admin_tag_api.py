"""
Test Admin Tag Management API
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
from models import init_db

client = TestClient(app)


class TestAdminTagAPI:
    """Test suite for admin tag management operations"""
    
    @classmethod
    def setup_class(cls):
        """Initialize test database"""
        init_db()
    
    def test_create_tag_root_level(self):
        """Test creating a root-level tag"""
        response = client.post("/api/tags", json={
            "name": "TestDeity",
            "category": "deity",
            "translations": {
                "kannada": "ಟೆಸ್ಟ್",
                "hindi": "टेस्ट"
            },
            "synonyms": ["TestAlias"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "TestDeity"
        assert "message" in data
    
    def test_create_tag_duplicate_name(self):
        """Test that duplicate tag names are rejected"""
        # First create
        client.post("/api/tags", json={
            "name": "UniqueTag",
            "category": "type"
        })
        
        # Try duplicate
        response = client.post("/api/tags", json={
            "name": "UniqueTag",
            "category": "type"
        })
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_create_tag_with_parent(self):
        """Test creating a child tag"""
        # Create parent
        parent_response = client.post("/api/tags", json={
            "name": "ParentTag",
            "category": "deity"
        })
        parent_id = parent_response.json()["id"]
        
        # Create child
        response = client.post("/api/tags", json={
            "name": "ChildTag",
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
        assert tag_data["level"] == 1
    
    def test_create_tag_invalid_parent(self):
        """Test creating tag with non-existent parent"""
        response = client.post("/api/tags", json={
            "name": "OrphanTag",
            "category": "deity",
            "parent_id": 99999
        })
        
        assert response.status_code == 404
        assert "Parent tag not found" in response.json()["detail"]
    
    def test_update_tag_name(self):
        """Test updating tag name"""
        # Create tag
        create_response = client.post("/api/tags", json={
            "name": "OldName",
            "category": "type"
        })
        tag_id = create_response.json()["id"]
        
        # Update name
        response = client.put(f"/api/tags/{tag_id}", json={
            "name": "NewName"
        })
        
        assert response.status_code == 200
        
        # Verify update
        detail_response = client.get(f"/api/tags/{tag_id}")
        assert detail_response.json()["name"] == "NewName"
    
    def test_update_tag_translations(self):
        """Test updating tag translations"""
        # Create tag
        create_response = client.post("/api/tags", json={
            "name": "TranslationTest",
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
    
    def test_update_tag_synonyms(self):
        """Test updating tag synonyms"""
        # Create tag
        create_response = client.post("/api/tags", json={
            "name": "SynonymTest",
            "category": "deity",
            "synonyms": ["OldSyn"]
        })
        tag_id = create_response.json()["id"]
        
        # Update synonyms
        response = client.put(f"/api/tags/{tag_id}", json={
            "synonyms": ["NewSyn1", "NewSyn2"]
        })
        
        assert response.status_code == 200
        
        # Verify update
        detail_response = client.get(f"/api/tags/{tag_id}")
        synonyms = detail_response.json()["synonyms"]
        assert "NewSyn1" in synonyms
        assert "NewSyn2" in synonyms
        assert "OldSyn" not in synonyms
    
    def test_update_tag_parent(self):
        """Test changing tag parent (reparenting)"""
        # Create tags
        parent1_response = client.post("/api/tags", json={
            "name": "Parent1",
            "category": "deity"
        })
        parent1_id = parent1_response.json()["id"]
        
        parent2_response = client.post("/api/tags", json={
            "name": "Parent2",
            "category": "deity"
        })
        parent2_id = parent2_response.json()["id"]
        
        child_response = client.post("/api/tags", json={
            "name": "MovingChild",
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
    
    def test_update_nonexistent_tag(self):
        """Test updating tag that doesn't exist"""
        response = client.put("/api/tags/99999", json={
            "name": "DoesntMatter"
        })
        
        assert response.status_code == 404
    
    def test_delete_unused_tag(self):
        """Test deleting tag not used by any bhajans"""
        # Create tag
        create_response = client.post("/api/tags", json={
            "name": "DeleteMe",
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
    
    def test_delete_tag_with_children(self):
        """Test that tag with children cannot be deleted"""
        # Create parent and child
        parent_response = client.post("/api/tags", json={
            "name": "ParentWithChild",
            "category": "deity"
        })
        parent_id = parent_response.json()["id"]
        
        client.post("/api/tags", json={
            "name": "ChildOfParent",
            "category": "deity",
            "parent_id": parent_id
        })
        
        # Try to delete parent
        response = client.delete(f"/api/tags/{parent_id}")
        
        assert response.status_code == 400
        assert "child tag" in response.json()["detail"].lower()
    
    def test_delete_tag_in_use(self):
        """Test that tag in use by bhajans cannot be deleted"""
        # This would require creating a bhajan with the tag
        # For now, we'll skip this test or mock it
        # TODO: Implement when bhajan-tag association API is ready
        pass
    
    def test_delete_nonexistent_tag(self):
        """Test deleting tag that doesn't exist"""
        response = client.delete("/api/tags/99999")
        
        assert response.status_code == 404
    
    def test_admin_page_accessible(self):
        """Test that admin page is accessible"""
        response = client.get("/admin/tags")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
    
    def test_tag_hierarchy_after_operations(self):
        """Test that tag hierarchy is maintained correctly after CRUD operations"""
        # Create hierarchy: Root -> Level1 -> Level2
        root_response = client.post("/api/tags", json={
            "name": "HierarchyRoot",
            "category": "deity"
        })
        root_id = root_response.json()["id"]
        
        level1_response = client.post("/api/tags", json={
            "name": "HierarchyLevel1",
            "category": "deity",
            "parent_id": root_id
        })
        level1_id = level1_response.json()["id"]
        
        level2_response = client.post("/api/tags", json={
            "name": "HierarchyLevel2",
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
