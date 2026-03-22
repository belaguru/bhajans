"""
Test Suite: Tag Filter UI
Tests for the enhanced tag-based filtering and search UI
"""
import pytest
from playwright.sync_api import Page, expect


def test_tag_filter_sidebar_visible(page: Page):
    """Test that tag filter sidebar is visible on desktop"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Desktop sidebar should be visible
    sidebar = page.locator(".lg\\:col-span-1").first
    expect(sidebar).to_be_visible()
    
    # Should have "Tags" heading
    expect(page.get_by_text("📑 Tags")).to_be_visible()


def test_tag_filter_mobile_toggle(page: Page):
    """Test mobile tag filter toggle button"""
    page.set_viewport_size({"width": 375, "height": 667})  # Mobile size
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Mobile toggle button should be visible
    toggle_btn = page.get_by_text("▼ Filter by Tags")
    expect(toggle_btn).to_be_visible()
    
    # Mobile tags section should be hidden initially
    mobile_tags = page.locator("#mobile-tags-section")
    expect(mobile_tags).to_have_class(/hidden/)
    
    # Click toggle
    toggle_btn.click()
    
    # Mobile tags should now be visible
    expect(mobile_tags).not_to_have_class(/hidden/)


def test_tag_search_functionality(page: Page):
    """Test tag search box filters tags correctly"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Wait for tags to load
    page.wait_for_selector("button:has-text('Hanuman')", timeout=5000)
    
    # Get initial tag count
    tag_buttons = page.locator(".space-y-2 button")
    initial_count = tag_buttons.count()
    
    # Search for "Hanuman"
    search_input = page.locator("#tag-search-input")
    search_input.fill("Hanuman")
    
    # Should show fewer tags
    filtered_count = tag_buttons.count()
    assert filtered_count <= initial_count
    
    # Clear button should be visible
    clear_btn = page.locator("#tag-search-clear")
    expect(clear_btn).to_be_visible()
    
    # Click clear
    clear_btn.click()
    
    # Should show all tags again
    page.wait_for_timeout(300)
    final_count = tag_buttons.count()
    assert final_count == initial_count


def test_tag_filter_bhajans(page: Page):
    """Test clicking a tag filters bhajans"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Wait for content to load
    page.wait_for_selector(".card", timeout=5000)
    
    # Get initial bhajan count
    initial_bhajans = page.locator("#bhajans-grid .card").count()
    
    # Click first tag
    first_tag = page.locator(".space-y-2 button").first
    first_tag.click()
    
    # Wait for filtering
    page.wait_for_timeout(500)
    
    # Should show active filter display
    expect(page.get_by_text("Showing bhajans tagged:")).to_be_visible()
    
    # Should show filtered results
    filtered_bhajans = page.locator("#bhajans-grid .card").count()
    assert filtered_bhajans <= initial_bhajans


def test_active_filters_display(page: Page):
    """Test active filters display shows selected tags"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Wait for tags
    page.wait_for_selector("button:has-text('Hanuman')", timeout=5000)
    
    # Click a tag
    tag_btn = page.get_by_role("button", name="Hanuman")
    tag_btn.click()
    
    # Wait for filter status
    page.wait_for_selector("#search-status", timeout=2000)
    
    # Should show active filter
    status = page.locator("#search-status")
    expect(status).to_contain_text("🏷️ Tag: Hanuman")
    expect(status).to_contain_text("Found")
    
    # Should have "Clear All" button
    clear_btn = page.get_by_text("Clear All ✕")
    expect(clear_btn).to_be_visible()
    
    # Click clear
    clear_btn.click()
    
    # Status should disappear
    page.wait_for_timeout(300)
    expect(status).to_be_empty()


def test_search_with_tag_filter(page: Page):
    """Test combining search and tag filters"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Search for something
    search_input = page.locator("input[placeholder*='Search bhajans']")
    search_input.fill("Krishna")
    
    # Wait for search results
    page.wait_for_timeout(500)
    
    # Click a tag
    page.wait_for_selector("button:has-text('Bhajan')", timeout=5000)
    tag_btn = page.get_by_role("button", name="Bhajan")
    tag_btn.click()
    
    # Wait for combined filtering
    page.wait_for_timeout(500)
    
    # Should show both filters in status
    status = page.locator("#search-status")
    expect(status).to_contain_text("📝 Search:")
    expect(status).to_contain_text("🏷️ Tag:")
    expect(status).to_contain_text("Krishna")
    expect(status).to_contain_text("Bhajan")


def test_clear_all_filters_button(page: Page):
    """Test Clear All button removes all filters"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Apply search
    search_input = page.locator("input[placeholder*='Search bhajans']")
    search_input.fill("Hanuman")
    page.wait_for_timeout(500)
    
    # Apply tag filter
    page.wait_for_selector("button:has-text('Stotra')", timeout=5000)
    tag_btn = page.get_by_role("button", name="Stotra")
    tag_btn.click()
    page.wait_for_timeout(500)
    
    # Should show active filters
    expect(page.locator("#search-status")).to_be_visible()
    
    # Click Clear All
    clear_btn = page.get_by_text("Clear All ✕")
    clear_btn.click()
    
    # Search input should be empty
    expect(search_input).to_have_value("")
    
    # Filter status should be gone
    page.wait_for_timeout(300)
    expect(page.locator("#search-status")).to_be_empty()


def test_tag_counts_display(page: Page):
    """Test that tag counts are displayed correctly"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Wait for tags to load
    page.wait_for_selector(".space-y-2 button", timeout=5000)
    
    # Each tag button should show count in parentheses
    first_tag = page.locator(".space-y-2 button").first
    text_content = first_tag.text_content()
    
    # Should have format like "Hanuman (78)"
    assert "(" in text_content
    assert ")" in text_content


def test_tag_highlight_on_select(page: Page):
    """Test that selected tag is visually highlighted"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Wait for tags
    page.wait_for_selector("button:has-text('Hanuman')", timeout=5000)
    
    # Click a tag
    tag_btn = page.get_by_role("button", name="Hanuman").first
    tag_btn.click()
    
    # Wait for state update
    page.wait_for_timeout(300)
    
    # Tag should have highlighted class
    expect(tag_btn).to_have_class(/bg-orange-100/)
    expect(tag_btn).to_have_class(/hanuman-accent/)


def test_no_results_message(page: Page):
    """Test no results message when no bhajans match filters"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Search for something unlikely to exist
    search_input = page.locator("input[placeholder*='Search bhajans']")
    search_input.fill("xyzabc123nonexistent")
    
    # Wait for search
    page.wait_for_timeout(500)
    
    # Should show "No bhajans found" in status
    status = page.locator("#search-status")
    expect(status).to_contain_text("❌ No bhajans found")
    expect(status).to_contain_text("Try different search terms")


def test_mobile_tag_filter_closes_on_select(page: Page):
    """Test that mobile tag section closes after selecting a tag"""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Open mobile tags
    toggle_btn = page.get_by_text("▼ Filter by Tags")
    toggle_btn.click()
    
    # Wait for tags section
    mobile_tags = page.locator("#mobile-tags-section")
    expect(mobile_tags).not_to_have_class(/hidden/)
    
    # Click a tag
    page.wait_for_selector("button:has-text('Hanuman')", timeout=5000)
    tag_btn = page.get_by_role("button", name="Hanuman").first
    tag_btn.click()
    
    # Wait for state update
    page.wait_for_timeout(300)
    
    # Mobile tags should auto-close
    expect(mobile_tags).to_have_class(/hidden/)


def test_tag_search_preserves_focus(page: Page):
    """Test that tag search input maintains focus after filtering"""
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Click tag search input
    search_input = page.locator("#tag-search-input")
    search_input.click()
    
    # Type something
    search_input.fill("Ha")
    
    # Wait for re-render
    page.wait_for_timeout(500)
    
    # Input should still be focused
    expect(search_input).to_be_focused()
    
    # Continue typing
    search_input.fill("Hanuman")
    page.wait_for_timeout(300)
    
    # Should still be focused
    expect(search_input).to_be_focused()


@pytest.mark.skip(reason="API integration test - requires tag hierarchy data")
def test_hierarchical_tag_filtering(page: Page):
    """Test that selecting parent tag shows child tag bhajans"""
    # This test requires tag hierarchy data to be present
    page.goto("http://localhost:8001")
    page.wait_for_selector("#app")
    
    # Click parent tag (e.g., "Deity")
    parent_tag = page.get_by_role("button", name="Deity")
    parent_tag.click()
    
    # Should show bhajans tagged with child tags (Vishnu, Shiva, etc.)
    # Implementation depends on API support for hierarchical queries
    pass


@pytest.mark.skip(reason="Future feature - tag suggestions")
def test_tag_suggestions_in_search(page: Page):
    """Test tag suggestions appear in search box"""
    # Future enhancement: autocomplete suggestions
    page.goto("http://localhost:8001")
    search_input = page.locator("input[placeholder*='Search bhajans']")
    search_input.fill("Anjan")
    
    # Should show suggestion: "Did you mean: Hanuman?"
    # Implementation TBD
    pass
