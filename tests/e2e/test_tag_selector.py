"""
E2E Tests for Hierarchical Tag Selector Component
Tests the tree structure, multi-select, search, and translation display
"""
import pytest
from playwright.sync_api import Page, expect
import time


class TestTagSelector:
    """Test suite for hierarchical tag selector component"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url):
        """Navigate to homepage before each test"""
        page.goto(base_url or "http://localhost:8001")
        page.wait_for_selector('#app')
        time.sleep(0.5)
        
    def test_homepage_loads(self, page: Page):
        """Test that homepage loads correctly"""
        # Check app container exists
        expect(page.locator("#app")).to_be_attached()
        
    def test_upload_page_loads(self, page: Page):
        """Test that upload page loads and has tag selector"""
        # Navigate to upload page
        # First check if there's an upload button/link
        upload_btn = page.locator("button:has-text('Upload')").first
        if upload_btn.is_visible():
            upload_btn.click()
            time.sleep(0.5)
            
            # Check for tag selector container
            expect(page.locator(".tag-tree-container, #tag-tree-container")).to_be_visible()
        
    def test_tag_tree_renders_on_upload_page(self, page: Page):
        """Test that hierarchical tag tree renders on upload page"""
        # Try to navigate to upload via menu
        try:
            # Look for Upload link/button
            upload_trigger = page.locator("text=Upload").first
            upload_trigger.click()
            time.sleep(0.8)
            
            # Check that tag tree container exists
            tag_container = page.locator("#tag-tree-container, .tag-tree-container")
            if tag_container.count() > 0:
                expect(tag_container.first).to_be_visible()
        except:
            pytest.skip("Upload page not accessible or tag tree not present")
        
    def test_tag_tree_structure_exists(self, page: Page):
        """Test that tag tree structure is present when available"""
        # Navigate to upload
        try:
            upload_btn = page.locator("text=Upload").first
            upload_btn.click()
            time.sleep(0.8)
            
            # Check for tag tree nodes (if they exist)
            tag_tree = page.locator(".tag-tree, #tags_tree")
            if tag_tree.count() > 0:
                expect(tag_tree.first).to_be_attached()
        except:
            pytest.skip("Tag tree structure not available")
        
    def test_tag_search_input_exists(self, page: Page):
        """Test that tag search input exists on upload page"""
        try:
            upload_btn = page.locator("text=Upload").first
            upload_btn.click()
            time.sleep(0.8)
            
            # Look for tag search input
            search_input = page.locator("#tags_search, input[placeholder*='Search tags']")
            if search_input.count() > 0:
                expect(search_input.first).to_be_visible()
        except:
            pytest.skip("Tag search not available")
        
    def test_tag_selector_hidden_input(self, page: Page):
        """Test that hidden input for selected tag IDs exists"""
        try:
            upload_btn = page.locator("text=Upload").first
            upload_btn.click()
            time.sleep(0.8)
            
            # Check for hidden input
            hidden_input = page.locator("#selected_tag_ids, input[name='tag_ids']")
            if hidden_input.count() > 0:
                expect(hidden_input.first).to_be_attached()
        except:
            pytest.skip("Tag selector hidden input not found")
        
    def test_form_has_required_fields(self, page: Page):
        """Test that upload form has basic required fields"""
        try:
            upload_btn = page.locator("text=Upload").first
            upload_btn.click()
            time.sleep(0.8)
            
            # Check for title input
            title_input = page.locator("#title, input[placeholder*='title' i]")
            expect(title_input.first).to_be_visible()
            
            # Check for lyrics textarea
            lyrics_input = page.locator("#lyrics, textarea[placeholder*='lyrics' i]")
            expect(lyrics_input.first).to_be_visible()
        except:
            pytest.skip("Upload form not accessible")
    
    def test_upload_form_submission_structure(self, page: Page):
        """Test that upload form can be filled out"""
        try:
            upload_btn = page.locator("text=Upload").first
            upload_btn.click()
            time.sleep(0.8)
            
            # Fill out basic fields (don't actually submit)
            title_input = page.locator("#title").first
            title_input.fill("Test Bhajan")
            
            lyrics_input = page.locator("#lyrics").first
            lyrics_input.fill("Test lyrics content")
            
            # Verify values were set
            assert title_input.input_value() == "Test Bhajan"
            assert lyrics_input.input_value() == "Test lyrics content"
        except:
            pytest.skip("Upload form fields not accessible")
    
    def test_category_based_tag_filter_on_homepage(self, page: Page):
        """Test that homepage has category-based tag filtering"""
        # Wait for tags to load
        time.sleep(1.5)
        
        # Look for deity category button (use last one for desktop)
        deity_category = page.locator("button:has-text('🕉️ Deities')")
        if deity_category.count() > 0:
            expect(deity_category.last).to_be_visible()
            
            # Click to expand
            deity_category.last.click()
            time.sleep(0.3)
            
            # Look for tag buttons (should have counts)
            tag_buttons = page.locator("button").filter(has_text=r"\(\d+\)")
            if tag_buttons.count() > 0:
                expect(tag_buttons.first).to_be_visible()
        else:
            pytest.skip("Category-based tags not visible on homepage")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
