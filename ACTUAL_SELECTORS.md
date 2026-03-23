# Belaguru Bhajans - Actual CSS Selectors & DOM Structure

**Generated:** 2026-03-23 21:08 IST  
**Base URL:** http://localhost:8001  
**Architecture:** SPA (Single Page App) - Content loaded via JavaScript

---

## 🏠 Homepage Selectors

### Bhajan Cards
**Class:** `.card` (NOT `.bhajan-card`)

**Full structure:**
```html
<div class="card cursor-pointer transform hover:scale-105 transition-transform"
     onclick="app.setPage('bhajan', {id})">
    <div class="flex items-start justify-between gap-4">
        <div class="flex-1 min-w-0">
            <h3 class="font-bold text-lg hanuman-text truncate">
                {title}
            </h3>
            <p class="text-gray-600 text-sm mt-1">
                By <span class="font-semibold">{uploader}</span> • <time>{date}</time>
            </p>
            <p class="text-gray-700 text-sm mt-3 line-clamp-2">
                {lyrics preview}...
            </p>
            <div class="flex flex-wrap gap-2 mt-3">
                <span class="inline-block bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-medium">
                    {tag}
                </span>
            </div>
        </div>
        <div class="text-2xl flex-shrink-0">🙏</div>
    </div>
</div>
```

**Key classes:**
- **Card container:** `.card` + `.cursor-pointer` + `.transform` + `.hover:scale-105`
- **Title:** `.font-bold` + `.text-lg` + `.hanuman-text` + `.truncate`
- **Metadata:** `.text-gray-600` + `.text-sm` + `.mt-1`
- **Lyrics preview:** `.text-gray-700` + `.text-sm` + `.mt-3` + `.line-clamp-2`
- **Tag:** `.inline-block` + `.bg-orange-100` + `.text-orange-700` + `.px-2` + `.py-1` + `.rounded` + `.text-xs` + `.font-medium`

**Selector for testing:**
```javascript
// All bhajan cards
document.querySelectorAll('.card.cursor-pointer')

// Card titles
document.querySelectorAll('.card .font-bold.text-lg.hanuman-text')

// Tags within cards
document.querySelectorAll('.card .inline-block.bg-orange-100')
```

---

## 📝 Upload Page Selectors

### Page Heading
**Text:** "Upload Bhajan" (NOT "Upload New Bhajan")  
**Location:** Navigation header via `renderNavHeader()` function

**Structure:**
```javascript
renderNavHeader({
    backLabel: 'Back to Bhajans',
    backAction: "app.setPage('home')",
    title: 'Upload Bhajan',  // ← Actual heading text
    subtitle: 'Share your favorite bhajan with the community'
})
```

**Expected DOM:**
```html
<div class="hanuman-primary">  <!-- Header background -->
    <button class="nav-back-btn">Back to Bhajans</button>
    <h1>{title}</h1>  <!-- "Upload Bhajan" -->
    <p>{subtitle}</p>
</div>
```

**Note:** Heading is dynamically rendered. Not a static `<h1>Upload New Bhajan</h1>`.

---

## ⚙️ Floating Menu Selectors

### Menu Button
**ID:** `#floating-menu-button`  
**Class:** `.floating-menu-button`

**CSS:**
```css
.floating-menu-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 999;
    background: linear-gradient(135deg, #FF6B35, #E67E22);
    border: none;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    /* ... */
}
```

**States:**
- Default: `.floating-menu-button`
- Open: `.floating-menu-button.open` (rotates 45deg)

**Animation:**
```css
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
```

### Menu Dropdown
**ID:** `#floating-menu`  
**Class:** `.floating-menu`

**CSS:**
```css
.floating-menu {
    position: fixed;
    bottom: 85px;
    right: 90px;
    z-index: 998;
    background: white;
    border-radius: 12px;
    /* ... */
}
```

**States:**
- Hidden: `.floating-menu` (max-height: 0, opacity: 0)
- Visible: `.floating-menu.visible` (max-height: 500px, opacity: 1)

### Menu Items
**Class:** `.floating-menu-item`

**Structure:**
```html
<div id="floating-menu" class="floating-menu">
    <div class="floating-menu-item" onclick="app.setPage('home')">
        <span class="floating-menu-item-icon">🏠</span>
        <span>Home</span>
    </div>
    <div class="floating-menu-item" onclick="app.openSearch()">
        <span class="floating-menu-item-icon">🔍</span>
        <span>Search</span>
    </div>
    <div class="floating-menu-item" onclick="app.setPage('upload')">
        <span class="floating-menu-item-icon">📝</span>
        <span>Upload</span>
    </div>
    <!-- ... more items ... -->
</div>
```

**Key classes:**
- **Menu item:** `.floating-menu-item`
- **Item icon:** `.floating-menu-item-icon`
- **Divider:** `.floating-menu-divider`

**Hover effect:**
```css
.floating-menu-item:hover {
    background-color: #fff5f0;
    color: #FF6B35;
    padding-left: 20px;  /* Slides right on hover */
}
```

---

## 🏷️ Tag Selector Structure

### Tag Categories
**Organization:** Tags are grouped by category (deity, type, composer, etc.)

**Category mapping:**
```javascript
const categoryNames = {
    'deity': '🕉️ Deities',
    'type': '📜 Types',
    'composer': '🎵 Composers',
    'language': '🌏 Languages',
    'occasion': '🎉 Occasions',
    'theme': '💡 Themes',
    'day': '📅 Day of Week',
    'raga': '🎼 Ragas',
    'other': '📌 Other'
};

const categoryOrder = ['deity', 'type', 'composer', 'language', 'occasion', 'theme', 'day', 'raga', 'other'];
```

### Tag Display (Homepage Sidebar)
**Function:** `renderTagsByCategory()`

**Structure:**
```html
<div class="tag-category">
    <div class="tag-category-header" onclick="app.toggleCategory('{category}')">
        <span>{emoji} {categoryName}</span>
        <span>{arrow}</span>
    </div>
    <div class="tag-list">
        <div class="tag-item" onclick="app.selectTag('{tag}')">
            <span class="tag-name">{tagName}</span>
            <span class="tag-count">{count}</span>
        </div>
    </div>
</div>
```

**State management:**
```javascript
this.expandedCategories = {};  // Track which categories are expanded
this.tagsByCategory = {};      // Tags organized by category
this.selectedTag = null;       // Currently selected tag filter
```

### Tag Input (Upload/Edit Forms)
**Wrapper class:** `.tag-input-wrapper`  
**Dropdown class:** `.tag-dropdown`

**CSS:**
```css
.tag-input-wrapper {
    position: relative;
}

.tag-dropdown {
    position: absolute;
    top: 100%;
    /* ... */
}
```

**State:**
```javascript
this._selectedTags = [];           // Selected tags for form
this._tagDropdownVisible = false;  // Dropdown open/closed
```

---

## 🎨 Common Styling Classes

### Buttons
- **Primary:** `.btn-primary` (orange background, white text)
- **Secondary:** `.btn-secondary` (white background, orange text)
- **Nav back:** `.nav-back-btn` (translucent white with border)

### Cards
- **Base:** `.card` (white background, rounded, shadow)
- **Hover:** `.card:hover` (lifts up, increased shadow)

### Theme Colors
```css
:root {
    --hanuman-orange: #FF6B35;
    --deep-orange: #E67E22;
    --golden: #FFD700;
    --saffron: #FF9933;
    --cream: #F8F6F1;
    --dark-text: #2C2416;
    --light-text: #6B6B6B;
}
```

### Text Styles
- **Hanuman text:** `.hanuman-text` (color: var(--dark-text))
- **Hanuman accent:** `.hanuman-accent` (color: var(--hanuman-orange))

---

## 🧪 Test Selectors Summary

**For Playwright/Selenium tests:**

```javascript
// Homepage
const bhajanCards = await page.locator('.card.cursor-pointer');
const cardTitles = await page.locator('.card .font-bold.text-lg.hanuman-text');
const cardTags = await page.locator('.card .inline-block.bg-orange-100');

// Upload page
await page.goto('/upload');
const heading = await page.locator('h1, h2, h3').filter({ hasText: 'Upload Bhajan' });

// Floating menu
const menuButton = await page.locator('#floating-menu-button');
await menuButton.click();
const menu = await page.locator('#floating-menu.visible');
const menuItems = await page.locator('.floating-menu-item');

// Tags
const tagCategories = await page.locator('.tag-category');
const selectedTags = await page.locator('.selected-tag');
```

---

## 📸 Screenshots

Screenshots saved to:
- `/tmp/belaguru-homepage.png` - Homepage with bhajan cards
- `/tmp/belaguru-upload.png` - Upload page form

**Note:** Screenshots require Playwright/Puppeteer (not installed in current environment).

---

## 🔍 Key Findings

1. **Bhajan cards use `.card` class** - NOT `.bhajan-card`
2. **Upload heading is "Upload Bhajan"** - NOT "Upload New Bhajan"
3. **Floating menu uses IDs** - `#floating-menu-button` and `#floating-menu`
4. **Tags organized by category** - Not a flat tree structure
5. **SPA architecture** - Content loaded dynamically via `app.js`
6. **Tailwind CSS + Custom CSS** - Mix of utility classes and custom `.card`, `.btn-primary`, etc.

---

## 🛠️ How to Inspect Live

**Option 1: Browser DevTools**
```bash
# Start server
cd ~/Projects/belaguru-bhajans
python main.py

# Open in browser: http://localhost:8001
# Press F12 → Elements tab → Inspect elements
```

**Option 2: Playwright (if installed)**
```bash
# Install Playwright
pip install playwright
playwright install chromium

# Run inspection script
python /tmp/inspect_belaguru_ui.py
```

**Option 3: curl + grep**
```bash
# Get page HTML
curl -s http://localhost:8001/ > page.html

# Get JavaScript app
curl -s http://localhost:8001/app.js > app.js

# Get CSS
curl -s http://localhost:8001/style.css > style.css

# Search for classes
grep -o 'class="[^"]*"' page.html | sort | uniq
```

---

**Last Updated:** 2026-03-23 21:08 IST  
**Server Status:** Running on http://localhost:8001  
**Version:** v1.0 (from app.js)
