# Bug Fix: Edit Form Tag Selector

## Problem
**Error:** Line 1692 - Cannot read properties of null (reading 'value')  
**Location:** `handleEditSubmit()` method  
**Root Cause:** Edit form was trying to read from old 'edit_tags_value' input that doesn't exist after tag hierarchy was added.

## Changes Made

### 1. Fixed `editBhajan()` method (line ~1589)
**Before:**
```javascript
this._selectedTags = [...bhajan.tags];
${this.renderHierarchicalTagSelector('edit_tags', [])}  // Empty array!
```

**After:**
```javascript
// Convert tag names to tag IDs for the hierarchical selector
const existingTagIds = this.getTagIdsByNames(bhajan.tags || []);
${this.renderHierarchicalTagSelector('edit_tags', existingTagIds)}
```

### 2. Fixed `handleEditSubmit()` method (line ~1692)
**Before:**
```javascript
const tagsValue = document.getElementById("edit_tags_value").value;  // WRONG ID!
const tags = tagsValue ? tagsValue.split(",").map(t => t.trim()).filter(t => t) : [];
formData.append("tags", tags.join(","));  // Old format (tag names)
```

**After:**
```javascript
// Read from hierarchical tag selector (uses 'selected_tag_ids' hidden input)
const tagIdsValue = document.getElementById("selected_tag_ids").value;
const tagIds = tagIdsValue ? tagIdsValue.split(",").map(id => parseInt(id.trim())).filter(id => !isNaN(id)) : [];
formData.append("tag_ids", tagIds.join(","));  // New format (tag IDs)
```

### 3. Added helper method `getTagIdsByNames()` (line ~815)
```javascript
/**
 * Helper: Get tag IDs by tag names (for edit form pre-population)
 */
getTagIdsByNames(tagNames) {
    if (!tagNames || !Array.isArray(tagNames)) return [];
    
    const findIdByName = (tree, targetName) => {
        for (const [name, node] of Object.entries(tree)) {
            if (name === targetName) return node.id;
            if (node.children) {
                const found = findIdByName(node.children, targetName);
                if (found) return found;
            }
        }
        return null;
    };
    
    return tagNames
        .map(name => findIdByName(this.tagTree, name))
        .filter(id => id !== null);
}
```

## Result
✅ Edit form now uses hierarchical tag selector (same as upload form)  
✅ Pre-populates existing tags correctly  
✅ Reads selected tags from the correct hidden input (`selected_tag_ids`)  
✅ Sends tag IDs (not tag names) to the API

## Status
**Code fixed and saved.** Ready for testing.  
**NOT deployed yet** (as requested).
