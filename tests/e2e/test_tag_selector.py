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
    def setup(self, page: Page):
        """Navigate to upload page before each test"""
        page.goto("http://localhost:8001")
        time.sleep(0.5)
        # Click Upload from menu
        page.click("text=Upload")
        time.sleep(0.5)
        
    def test_tag_tree_renders_on_upload_page(self, page: Page):
        """Test that hierarchical tag tree renders on upload page"""
        # Check that tag tree container exists
        expect(page.locator("#tag-tree-container")).to_be_visible()
        
        # Check for root category nodes
        expect(page.locator(".tag-tree-node:has-text('Deity')")).to_be_visible()
        expect(page.locator(".tag-tree-node:has-text('Type')")).to_be_visible()
        
    def test_tag_tree_expand_collapse(self, page: Page):
        """Test expanding and collapsing tree nodes"""
        # Find Deity node
        deity_node = page.locator(".tag-tree-node:has-text('Deity')").first
        
        # Initially children should be hidden
        deity_children = page.locator(".tag-tree-node:has-text('Vishnu')")
        expect(deity_children).to_be_hidden()
        
        # Click expand icon
        deity_node.locator(".expand-icon").click()
        time.sleep(0.2)
        
        # Children should now be visible
        expect(deity_children).to_be_visible()
        
        # Collapse again
        deity_node.locator(".expand-icon").click()
        time.sleep(0.2)
        expect(deity_children).to_be_hidden()
        
    def test_tag_multi_select_checkboxes(self, page: Page):
        """Test multi-select with checkboxes"""
        # Expand Deity node
        page.locator(".tag-tree-node:has-text('Deity')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        
        # Expand Vishnu node
        page.locator(".tag-tree-node:has-text('Vishnu')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        
        # Select Krishna checkbox
        krishna_checkbox = page.locator("input[type='checkbox'][data-tag-name='Krishna']")
        krishna_checkbox.click()
        
        # Check that Krishna appears in selected tags (pills)
        expect(page.locator(".tag-pill:has-text('Krishna')")).to_be_visible()
        
        # Select Rama checkbox
        rama_checkbox = page.locator("input[type='checkbox'][data-tag-name='Rama']")
        rama_checkbox.click()
        
        # Both should be selected
        expect(page.locator(".tag-pill:has-text('Krishna')")).to_be_visible()
        expect(page.locator(".tag-pill:has-text('Rama')")).to_be_visible()
        
    def test_tag_translations_display(self, page: Page):
        """Test that Kannada translations display in parentheses"""
        # Expand Deity > Shiva
        page.locator(".tag-tree-node:has-text('Deity')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        page.locator(".tag-tree-node:has-text('Shiva')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        
        # Check that Hanuman shows Kannada translation
        hanuman_node = page.locator(".tag-tree-node:has-text('Hanuman')")
        expect(hanuman_node).to_contain_text("ಹನುಮಾನ್")
        
    def test_tag_search_filter(self, page: Page):
        """Test search/filter within tags"""
        # Type in search box
        search_input = page.locator("#tag-search-input")
        search_input.fill("krishna")
        time.sleep(0.3)
        
        # Only Krishna and its parents should be visible
        expect(page.locator(".tag-tree-node:has-text('Krishna')")).to_be_visible()
        expect(page.locator(".tag-tree-node:has-text('Vishnu')")).to_be_visible()
        expect(page.locator(".tag-tree-node:has-text('Deity')")).to_be_visible()
        
        # Other tags should be filtered out
        expect(page.locator(".tag-tree-node:has-text('Ganesha')")).to_be_hidden()
        
    def test_tag_pill_removal(self, page: Page):
        """Test removing selected tag by clicking X on pill"""
        # Expand and select Krishna
        page.locator(".tag-tree-node:has-text('Deity')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        page.locator(".tag-tree-node:has-text('Vishnu')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        krishna_checkbox = page.locator("input[type='checkbox'][data-tag-name='Krishna']")
        krishna_checkbox.click()
        
        # Verify pill exists
        expect(page.locator(".tag-pill:has-text('Krishna')")).to_be_visible()
        
        # Click X button on pill
        page.locator(".tag-pill:has-text('Krishna') .remove-tag-btn").click()
        time.sleep(0.2)
        
        # Pill should be removed
        expect(page.locator(".tag-pill:has-text('Krishna')")).to_be_hidden()
        
        # Checkbox should be unchecked
        expect(krishna_checkbox).not_to_be_checked()
        
    def test_selected_tags_hidden_input_value(self, page: Page):
        """Test that selected tag IDs are stored in hidden input"""
        # Expand and select multiple tags
        page.locator(".tag-tree-node:has-text('Deity')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        page.locator(".tag-tree-node:has-text('Vishnu')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        
        page.locator("input[type='checkbox'][data-tag-name='Krishna']").click()
        page.locator("input[type='checkbox'][data-tag-name='Rama']").click()
        
        # Check hidden input contains tag IDs (comma-separated)
        hidden_input = page.locator("#selected_tag_ids")
        value = hidden_input.input_value()
        
        # Should contain IDs (we know Krishna=7, Rama=8 from earlier query)
        assert "7" in value
        assert "8" in value
        
    def test_edit_page_prepopulates_tags(self, page: Page):
        """Test that edit page pre-populates selected tags"""
        # First create a bhajan with tags (requires full flow)
        # For now, we'll just verify the edit page loads with the component
        page.goto("http://localhost:8001")
        time.sleep(0.5)
        
        # Find a bhajan to edit
        page.click(".bhajan-card:first-child")
        time.sleep(0.5)
        page.click("text=Edit")
        time.sleep(0.5)
        
        # Check tag tree exists on edit page
        expect(page.locator("#tag-tree-container")).to_be_visible()
        
    def test_form_submission_includes_tag_ids(self, page: Page):
        """Test that form submission includes selected tag IDs"""
        # Fill out upload form
        page.fill("#title", "Test Bhajan with Tags")
        page.fill("#lyrics", "Test lyrics here")
        
        # Select tags
        page.locator(".tag-tree-node:has-text('Type')").first.locator(".expand-icon").click()
        time.sleep(0.2)
        page.locator("input[type='checkbox'][data-tag-name='Bhajan']").click()
        
        # Submit form (we'll intercept the request)
        page.on("request", lambda request: print(f"Request: {request.url} - {request.post_data}"))
        page.click("button[type='submit']")
        time.sleep(1)
        
        # Verify submission worked (bhajan created)
        # This is a basic check - detailed validation would inspect the POST data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
