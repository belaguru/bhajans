/**
 * Belaguru Bhajan Portal - Frontend App
 * Shree Kshetra Belaguru - Bhajana Maalika
 * Native Responsive UI, Mobile-First
 */

class BelaGuruApp {
    constructor() {
        console.log("🦁 BelaGuruApp constructor starting...");
        this.currentPage = "home";
        this.bhajans = [];
        this.filteredBhajans = [];
        this.allTags = [];
        this.tagTaxonomy = [];
        this.tagsByCategory = {};
        this.showAllTags = false;
        this.tagSearchQuery = "";
        this.selectedTag = null;
        this.searchQuery = "";
        this.appContainer = document.getElementById("app");
        this.searchTimeout = null;
        this.mobileTagsOpen = false; // Track mobile tags section state
        this.expandedCategories = {}; // Track which categories are expanded
        // Tag input state for upload/edit forms
        this._selectedTags = [];
        this._tagDropdownVisible = false;

        this.init();
    }

    async init() {
        await this.loadBhajans();
        await this.loadTags();
        await this.loadTagTree();
        this.loadFontSizePreference();
        this.initURLListener();
        this.loadFromURL();
    }

    async loadBhajans() {
        try {
            const response = await fetch("/api/bhajans");
            this.bhajans = await response.json();
            this.filteredBhajans = [...this.bhajans];
        } catch (error) {
            console.error("Error loading bhajans:", error);
        }
    }

    async loadTags() {
        try {
            // Load tag taxonomy (for categories) - this is the proper endpoint
            const taxonomyResponse = await fetch("/api/tags");
            this.tagTaxonomy = await taxonomyResponse.json();
            
            // Load tag counts - this will work once we fix the route
            try {
                const response = await fetch("/api/bhajans");
                const bhajans = await response.json();
                
                // Calculate counts from bhajans
                const tagCounts = {};
                bhajans.forEach(bhajan => {
                    if (bhajan.tags && Array.isArray(bhajan.tags)) {
                        bhajan.tags.forEach(tag => {
                            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                        });
                    }
                });
                
                this.allTags = Object.entries(tagCounts)
                    .map(([tag, count]) => ({ tag, count }))
                    .sort((a, b) => b.count - a.count);
            } catch (e) {
                console.error("Error calculating tag counts:", e);
                this.allTags = [];
            }
            
            // Organize tags by category
            this.tagsByCategory = this.organizeTagsByCategory();
        } catch (error) {
            console.error("Error loading tags:", error);
            this.tagTaxonomy = [];
            this.allTags = [];
            this.tagsByCategory = {};
        }
    }
    
    organizeTagsByCategory() {
        const categories = {};
        
        if (!this.tagTaxonomy || !Array.isArray(this.tagTaxonomy)) {
            return categories;
        }
        
        // Group tags by category
        this.tagTaxonomy.forEach(tag => {
            const category = tag.category || 'other';
            if (!categories[category]) {
                categories[category] = [];
            }
            
            // Find count for this tag
            const tagCount = this.allTags.find(t => t.tag === tag.name);
            if (tagCount && tagCount.count > 0) {
                categories[category].push({
                    name: tag.name,
                    count: tagCount.count,
                    id: tag.id
                });
            }
        });
        
        // Sort tags within each category by count
        Object.keys(categories).forEach(cat => {
            categories[cat].sort((a, b) => b.count - a.count);
        });
        
        return categories;
    }

    /**
     * Load hierarchical tag tree from API
     */
    async loadTagTree() {
        try {
            const response = await fetch("/api/tags/tree");
            this.tagTree = await response.json();
            console.log("Tag tree loaded:", this.tagTree);
        } catch (error) {
            console.error("Error loading tag tree:", error);
            this.tagTree = {};
        }
    }

    validateMp3File(file) {
        if (!file) return true; // Optional file
        
        const maxSize = 5 * 1024 * 1024; // 5MB
        
        if (!file.name.toLowerCase().endsWith('.mp3')) {
            alert('Only .mp3 files are allowed!');
            return false;
        }
        
        if (file.size > maxSize) {
            const sizeMB = (file.size / 1024 / 1024).toFixed(2);
            alert(`File too large (${sizeMB}MB)! Maximum size is 5MB.`);
            return false;
        }
        
        return true;
    }

    async createBhajan(data) {
        try {
            const formData = new FormData();
            formData.append("title", data.title);
            formData.append("lyrics", data.lyrics);
            
            // Support both old tag names and new tag IDs
            if (data.tagIds) {
                formData.append("tag_ids", data.tagIds.join(","));
            } else if (data.tags) {
                formData.append("tags", data.tags.join(","));
            }
            
            formData.append("uploader_name", data.uploader_name || "Anonymous");
            if (data.youtube_url) formData.append("youtube_url", data.youtube_url);
            if (data.mp3_file) formData.append("mp3_file", data.mp3_file);

            const response = await fetch("/api/bhajans", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Failed to create bhajan");
            }

            await this.loadBhajans();
            await this.loadTags();

            return true;
        } catch (error) {
            alert(`Error: ${error.message}`);
            return false;
        }
    }

    searchBhajans(query) {
        this.searchQuery = query.toLowerCase();

        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        this.searchTimeout = setTimeout(() => {
            this.applyFilters();
            this.renderResults();
            this.renderSearchStatus(); // NEW: Show search results feedback
        }, 300);
    }

    filterByTag(tag) {
        this.selectedTag = this.selectedTag === tag ? null : tag;
        this.applyFilters();
        this.renderResults();
        this.renderSearchStatus(); // NEW: Update status when filtering
    }

    toggleShowAllTags() {
        this.showAllTags = !this.showAllTags;
        this.renderHome();
    }
    
    toggleCategory(category) {
        this.expandedCategories[category] = !this.expandedCategories[category];
        this.renderHome();
    }

    clearFilters() {
        this.selectedTag = null;
        this.searchQuery = "";
        this.renderHome();
    }

    searchTags(query) {
        this.tagSearchQuery = query.toLowerCase();
        this.renderHome();
    }

    clearTagSearch() {
        this.tagSearchQuery = "";
        this.renderHome();
    }

    toggleMobileTags() {
        const section = document.getElementById('mobile-tags-section');
        if (section) {
            section.classList.toggle('hidden');
            this.mobileTagsOpen = !section.classList.contains('hidden');
        }
    }

    applyFilters() {
        this.filteredBhajans = this.bhajans.filter(bhajan => {
            const matchesSearch = !this.searchQuery ||
                bhajan.title.toLowerCase().includes(this.searchQuery) ||
                bhajan.lyrics.toLowerCase().includes(this.searchQuery);

            const matchesTag = !this.selectedTag ||
                bhajan.tags.includes(this.selectedTag);

            return matchesSearch && matchesTag;
        });
    }

    // NEW: Render search results status/feedback
    renderSearchStatus() {
        const statusContainer = document.getElementById('search-status');
        if (!statusContainer) return;

        let statusHTML = '';

        if (this.searchQuery || this.selectedTag) {
            // Show filters info
            let filterInfo = [];
            
            if (this.searchQuery) {
                filterInfo.push(`📝 Search: "<strong>${this.searchQuery}</strong>"`);
            }
            
            if (this.selectedTag) {
                filterInfo.push(`🏷️ Tag: <strong>${this.selectedTag}</strong>`);
            }

            const count = this.filteredBhajans.length;
            const resultText = count === 1 ? 'bhajan' : 'bhajans';

            if (count > 0) {
                statusHTML = `
                    <div class="card bg-green-50 border-l-4 border-green-500 mb-6">
                        <div class="flex items-center justify-between gap-3">
                            <div class="flex-1">
                                <p class="text-sm text-gray-700">
                                    ${filterInfo.join(' + ')}
                                </p>
                                <p class="font-semibold text-green-700 mt-1">
                                    ✅ Found <strong>${count}</strong> of ${this.bhajans.length} ${resultText}
                                </p>
                            </div>
                            <button onclick="app.clearFilters()" class="text-sm px-3 py-1 rounded bg-green-200 hover:bg-green-300 text-green-800 font-semibold transition-colors">
                                Clear Filters ✕
                            </button>
                        </div>
                    </div>
                `;
            } else {
                statusHTML = `
                    <div class="card bg-red-50 border-l-4 border-red-500 mb-6">
                        <div class="flex items-center justify-between gap-3">
                            <div class="flex-1">
                                <p class="text-sm text-gray-700">
                                    ${filterInfo.join(' + ')}
                                </p>
                                <p class="font-semibold text-red-700 mt-1">
                                    ❌ No bhajans found
                                </p>
                                <p class="text-xs text-red-600 mt-1">
                                    Try different search terms or filters
                                </p>
                            </div>
                            <button onclick="app.clearFilters()" class="text-sm px-3 py-1 rounded bg-red-200 hover:bg-red-300 text-red-800 font-semibold transition-colors flex-shrink-0">
                                Clear All ✕
                            </button>
                        </div>
                    </div>
                `;
            }
        }

        statusContainer.innerHTML = statusHTML;
    }

    // NEW: Clear all filters
    clearFilters() {
        this.searchQuery = "";
        this.selectedTag = null;
        
        // Update search input
        const searchInput = document.querySelector('input[placeholder*="Search bhajans"]');
        if (searchInput) searchInput.value = "";
        
        this.applyFilters();
        this.renderResults();
        this.renderSearchStatus();
    }

    renderResults() {
        const gridContainer = document.getElementById('bhajans-grid');
        if (!gridContainer) return;

        const gridHTML = `
            ${this.filteredBhajans.length > 0 ? `
                ${this.filteredBhajans.map(bhajan => `
                    <div class="card cursor-pointer transform hover:scale-105 transition-transform"
                         onclick="app.setPage('bhajan', ${bhajan.id})">
                        <div class="flex items-start justify-between gap-4">
                            <div class="flex-1 min-w-0">
                                <h3 class="font-bold text-lg hanuman-text truncate">
                                    ${bhajan.title}
                                </h3>
                                <p class="text-gray-600 text-sm mt-1">
                                    By <span class="font-semibold">${bhajan.uploader_name}</span> •
                                    <time>${new Date(bhajan.created_at).toLocaleDateString()}</time>
                                </p>
                                <p class="text-gray-700 text-sm mt-3 line-clamp-2">
                                    ${bhajan.lyrics.substring(0, 150)}...
                                </p>
                                <div class="flex flex-wrap gap-2 mt-3">
                                    ${bhajan.tags.map(tag => `
                                        <span class="inline-block bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-medium">
                                            ${tag}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="text-2xl flex-shrink-0">🙏</div>
                        </div>
                    </div>
                `).join('')}
            ` : `
                <div class="card text-center py-12">
                    <p class="text-gray-500 text-lg">
                        No bhajans found. Be the first to upload! 🎵
                    </p>
                    <button onclick="app.setPage('upload')" class="btn-primary mt-4">
                        Upload Bhajan
                    </button>
                </div>
            `}
        `;

        gridContainer.innerHTML = gridHTML;
    }

    setPage(page) {
        this.currentPage = page;

        if (page === "home") {
            this.updateURL('home');
            this.renderHome();
        } else if (page === "upload") {
            this._selectedTags = [];
            this.renderUpload();
        } else if (page === "bhajan" && arguments[1]) {
            this.updateURL('bhajan', arguments[1]);
            this.renderBhajanDetail(arguments[1]);
        } else if (page === "settings") {
            this.renderSettings();
        } else if (page === "favorites") {
            this.renderFavorites();
        }
    }

    // ===== TAG DISPLAY HELPERS =====
    
    renderTagsByCategory() {
        const categoryNames = {
            'deity': '🕉️ Deities',
            'type': '📜 Types',
            'composer': '🎵 Composers',
            'language': '🌏 Languages',
            'occasion': '🎉 Occasions',
            'theme': '💡 Themes',
            'raga': '🎼 Ragas',
            'other': '📌 Other'
        };
        
        const categoryOrder = ['deity', 'type', 'composer', 'language', 'occasion', 'theme', 'raga', 'other'];
        
        let html = '';
        
        categoryOrder.forEach(category => {
            const tags = this.tagsByCategory[category] || [];
            if (tags.length === 0) return;
            
            const isExpanded = this.expandedCategories[category];
            const displayName = categoryNames[category] || category;
            const totalCount = tags.reduce((sum, t) => sum + t.count, 0);
            
            html += `
                <div class="mb-3">
                    <button 
                        onclick="app.toggleCategory('${category}')"
                        class="w-full flex items-center justify-between px-2 py-1 text-sm font-semibold text-gray-700 hover:bg-orange-50 rounded transition"
                    >
                        <span>${isExpanded ? '▼' : '▶'} ${displayName}</span>
                        <span class="text-xs text-gray-500">(${totalCount})</span>
                    </button>
                    ${isExpanded ? `
                        <div class="mt-1 ml-3 space-y-1">
                            ${tags.filter(t => !this.tagSearchQuery || t.name.toLowerCase().includes(this.tagSearchQuery)).slice(0, 10).map(tag => `
                                <button
                                    onclick="app.filterByTag('${tag.name}')"
                                    class="w-full text-left px-3 py-1.5 rounded text-sm transition-all flex items-center justify-between ${
                                        this.selectedTag === tag.name
                                            ? 'bg-orange-100 hanuman-accent font-semibold'
                                            : 'hover:bg-orange-50 text-gray-700'
                                    }"
                                >
                                    <span class="truncate">${tag.name}</span>
                                    <span class="text-xs ml-2 flex-shrink-0 ${this.selectedTag === tag.name ? 'text-orange-600' : 'text-gray-500'}">(${tag.count})</span>
                                </button>
                            `).join('')}
                            ${tags.length > 10 && !this.tagSearchQuery ? `
                                <p class="text-xs text-gray-500 px-3 py-1">+${tags.length - 10} more</p>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        return html;
    }
    
    renderPopularTags() {
        // Get top 10 most popular tags across all categories
        const allTagsFlat = [];
        
        if (this.tagsByCategory && typeof this.tagsByCategory === 'object') {
            Object.values(this.tagsByCategory).forEach(tags => {
                if (Array.isArray(tags)) {
                    allTagsFlat.push(...tags);
                }
            });
        }
        
        const topTags = allTagsFlat
            .filter(t => !this.tagSearchQuery || t.name.toLowerCase().includes(this.tagSearchQuery))
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);
        
        if (topTags.length === 0) {
            return '<p class="text-sm text-gray-500 px-2">No tags available</p>';
        }
        
        return topTags.map(tag => `
            <button
                onclick="app.filterByTag('${tag.name}')"
                class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-semibold transition-all ${
                    this.selectedTag === tag.name
                        ? 'bg-orange-500 text-white'
                        : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                }"
            >
                <span>${tag.name}</span>
                <span class="text-xs opacity-75">(${tag.count})</span>
            </button>
        `).join('');
    }

    // ===== TAG AUTOCOMPLETE COMPONENT =====

    /**
     * Load hierarchical tag tree from API
     */
    async loadTagTree() {
        try {
            const response = await fetch("/api/tags/tree");
            this.tagTree = await response.json();
            console.log("Tag tree loaded:", this.tagTree);
        } catch (error) {
            console.error("Error loading tag tree:", error);
            this.tagTree = {};
        }
    }

    /**
     * Render hierarchical tag selector component
     * @param {string} inputId - Unique ID for this tag selector instance
     * @param {Array} selectedTagIds - Array of tag IDs to pre-select
     */
    renderHierarchicalTagSelector(inputId, selectedTagIds = []) {
        this._selectedTagIds = selectedTagIds || [];
        this._tagFilterQuery = "";
        
        return `
            <div class="hierarchical-tag-selector" id="${inputId}_selector">
                <!-- Selected tags pills -->
                <div class="selected-tags-container" id="${inputId}_pills">
                    ${this.renderSelectedTagPills(inputId)}
                </div>
                
                <!-- Tag tree container -->
                <div class="tag-tree-container" id="tag-tree-container">
                    <!-- Search box -->
                    <div class="tag-search-box">
                        <input 
                            type="text" 
                            id="${inputId}_search" 
                            placeholder="Search tags..."
                            oninput="app.filterTagTree('${inputId}', this.value)"
                        >
                    </div>
                    
                    <!-- Tree structure -->
                    <ul class="tag-tree" id="${inputId}_tree">
                        ${this.renderTagTree(inputId, this.tagTree, selectedTagIds)}
                    </ul>
                </div>
                
                <!-- Hidden input for form submission -->
                <input type="hidden" id="selected_tag_ids" name="tag_ids" value="${selectedTagIds.join(',')}">
            </div>
        `;
    }

    /**
     * Recursively render tag tree structure
     */
    renderTagTree(inputId, treeData, selectedTagIds, level = 0) {
        if (!treeData || typeof treeData !== 'object') return '';
        
        let html = '';
        
        Object.keys(treeData).forEach(tagName => {
            const tagNode = treeData[tagName];
            const hasChildren = tagNode.children && Object.keys(tagNode.children).length > 0;
            const isSelected = selectedTagIds.includes(tagNode.id);
            const isExpanded = this._expandedNodes && this._expandedNodes.has(`${inputId}_${tagNode.id}`);
            
            html += `
                <li class="tag-tree-node" data-tag-id="${tagNode.id}" data-tag-name="${tagName}" data-level="${level}" style="margin-left: ${level * 20}px;">
                    <div style="display: flex; flex-direction: row; align-items: center; gap: 8px; padding: 6px 4px;">
                        <span class="expand-icon ${hasChildren ? (isExpanded ? 'expanded' : 'collapsed') : 'leaf'}" 
                              onclick="app.toggleTagNode('${inputId}', ${tagNode.id})"
                              style="width: 20px; flex-shrink: 0; cursor: pointer;">
                        </span>
                        <input 
                            type="checkbox" 
                            style="width: 18px; height: 18px; flex-shrink: 0; cursor: pointer;"
                            data-tag-id="${tagNode.id}"
                            data-tag-name="${tagName}"
                            ${isSelected ? 'checked' : ''}
                            onchange="app.toggleTagSelection('${inputId}', ${tagNode.id}, '${tagName}', this.checked)"
                        >
                        <span style="flex: 1;">
                            ${tagName}
                            ${tagNode.translations && tagNode.translations.kn ? `<span style="color: #888; margin-left: 4px;">(${tagNode.translations.kn})</span>` : ''}
                            <span style="background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 6px; color: #666;">${tagNode.category}</span>
                        </span>
                    </div>
                    
                    ${hasChildren ? `
                        <ul class="tag-tree-children" style="display: ${isExpanded ? 'block' : 'none'}; list-style: none; padding: 0; margin: 0;">
                            ${this.renderTagTree(inputId, tagNode.children, selectedTagIds, level + 1)}
                        </ul>
                    ` : ''}
                </li>
            `;
        });
        
        return html;
    }

    /**
     * Render selected tag pills
     */
    renderSelectedTagPills(inputId) {
        if (!this._selectedTagIds || this._selectedTagIds.length === 0) {
            return '<p class="text-gray-500 text-sm">No tags selected</p>';
        }
        
        return this._selectedTagIds.map(tagId => {
            const tagName = this.getTagNameById(tagId);
            const translation = this.getTagTranslation(tagId, 'kn');
            
            return `
                <span class="tag-pill">
                    ${tagName}
                    ${translation ? `<span class="tag-translation">(${translation})</span>` : ''}
                    <button 
                        type="button" 
                        class="remove-tag-btn" 
                        onclick="app.removeTagSelection('${inputId}', ${tagId})"
                    >×</button>
                </span>
            `;
        }).join('');
    }

    /**
     * Toggle tag node expansion
     */
    toggleTagNode(inputId, tagId) {
        if (!this._expandedNodes) {
            this._expandedNodes = new Set();
        }
        
        const nodeKey = `${inputId}_${tagId}`;
        
        if (this._expandedNodes.has(nodeKey)) {
            this._expandedNodes.delete(nodeKey);
        } else {
            this._expandedNodes.add(nodeKey);
        }
        
        // Re-render the tree
        this.refreshTagTree(inputId);
    }

    /**
     * Toggle tag selection (checkbox)
     */
    toggleTagSelection(inputId, tagId, tagName, isChecked) {
        if (!this._selectedTagIds) {
            this._selectedTagIds = [];
        }
        
        if (isChecked && !this._selectedTagIds.includes(tagId)) {
            this._selectedTagIds.push(tagId);
        } else if (!isChecked && this._selectedTagIds.includes(tagId)) {
            this._selectedTagIds = this._selectedTagIds.filter(id => id !== tagId);
        }
        
        // Update pills and hidden input
        this.refreshSelectedTags(inputId);
    }

    /**
     * Remove tag from selection (via pill X button)
     */
    removeTagSelection(inputId, tagId) {
        if (!this._selectedTagIds) return;
        
        this._selectedTagIds = this._selectedTagIds.filter(id => id !== tagId);
        
        // Update checkbox state
        const checkbox = document.querySelector(`input[data-tag-id="${tagId}"]`);
        if (checkbox) {
            checkbox.checked = false;
        }
        
        // Update pills and hidden input
        this.refreshSelectedTags(inputId);
    }

    /**
     * Filter tag tree by search query
     */
    filterTagTree(inputId, query) {
        this._tagFilterQuery = query.toLowerCase().trim();
        
        const treeContainer = document.getElementById(`${inputId}_tree`);
        if (!treeContainer) return;
        
        const allNodes = treeContainer.querySelectorAll('.tag-tree-node');
        
        if (!this._tagFilterQuery) {
            // Show all nodes
            allNodes.forEach(node => {
                node.classList.remove('filtered-out', 'filtered-match', 'filtered-parent');
            });
            return;
        }
        
        // Filter nodes
        allNodes.forEach(node => {
            const tagName = node.getAttribute('data-tag-name').toLowerCase();
            const matches = tagName.includes(this._tagFilterQuery);
            
            if (matches) {
                node.classList.add('filtered-match');
                node.classList.remove('filtered-out');
                
                // Show all parent nodes
                let parent = node.parentElement.closest('.tag-tree-node');
                while (parent) {
                    parent.classList.add('filtered-parent');
                    parent.classList.remove('filtered-out');
                    
                    // Expand parent
                    const children = parent.querySelector('.tag-tree-children');
                    if (children) {
                        children.classList.remove('collapsed');
                        children.classList.add('expanded');
                    }
                    
                    const expandIcon = parent.querySelector('.expand-icon');
                    if (expandIcon) {
                        expandIcon.classList.remove('collapsed');
                        expandIcon.classList.add('expanded');
                    }
                    
                    parent = parent.parentElement.closest('.tag-tree-node');
                }
            } else if (!node.classList.contains('filtered-parent')) {
                node.classList.add('filtered-out');
                node.classList.remove('filtered-match');
            }
        });
    }

    /**
     * Refresh tag tree UI
     */
    refreshTagTree(inputId) {
        const treeContainer = document.getElementById(`${inputId}_tree`);
        if (!treeContainer) return;
        
        treeContainer.innerHTML = this.renderTagTree(inputId, this.tagTree, this._selectedTagIds);
    }

    /**
     * Refresh selected tags pills and hidden input
     */
    refreshSelectedTags(inputId) {
        // Update pills
        const pillsContainer = document.getElementById(`${inputId}_pills`);
        if (pillsContainer) {
            pillsContainer.innerHTML = this.renderSelectedTagPills(inputId);
        }
        
        // Update hidden input
        const hiddenInput = document.getElementById('selected_tag_ids');
        if (hiddenInput) {
            hiddenInput.value = this._selectedTagIds.join(',');
        }
    }

    /**
     * Helper: Get tag name by ID
     */
    getTagNameById(tagId) {
        const findInTree = (tree) => {
            for (const [name, node] of Object.entries(tree)) {
                if (node.id === tagId) return name;
                if (node.children) {
                    const found = findInTree(node.children);
                    if (found) return found;
                }
            }
            return null;
        };
        
        return findInTree(this.tagTree) || `Tag ${tagId}`;
    }

    /**
     * Helper: Get tag translation
     */
    getTagTranslation(tagId, language = 'kn') {
        const findInTree = (tree) => {
            for (const [name, node] of Object.entries(tree)) {
                if (node.id === tagId) {
                    return node.translations && node.translations[language] ? node.translations[language] : null;
                }
                if (node.children) {
                    const found = findInTree(node.children);
                    if (found) return found;
                }
            }
            return null;
        };
        
        return findInTree(this.tagTree);
    }

    // ===== TAG AUTOCOMPLETE COMPONENT =====

    renderTagInputHTML(inputId, existingTags) {
        this._selectedTags = existingTags || [];
        return `
            <div class="tag-input-wrapper" id="${inputId}_wrapper">
                <div class="flex flex-wrap gap-2 mb-2" id="${inputId}_chips">
                    ${this._selectedTags.map(tag => `
                        <span class="inline-flex items-center bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm font-semibold">
                            ${tag}
                            <button type="button" onclick="app.removeTag('${inputId}', '${tag}')" class="ml-1 text-orange-500 hover:text-orange-800 font-bold">&times;</button>
                        </span>
                    `).join('')}
                </div>
                <div class="relative">
                    <input
                        type="text"
                        id="${inputId}"
                        placeholder="Type to search tags or add new..."
                        autocomplete="off"
                        oninput="app.onTagInput('${inputId}', this.value)"
                        onkeydown="app.onTagKeydown(event, '${inputId}')"
                        onfocus="app.onTagInput('${inputId}', this.value)"
                    >
                    <div id="${inputId}_dropdown" class="tag-dropdown hidden">
                    </div>
                </div>
                <input type="hidden" id="${inputId}_value" value="${this._selectedTags.join(',')}">
                <p class="text-gray-500 text-sm mt-2">
                    Click a suggestion or press Enter/comma to add a tag
                </p>
            </div>
        `;
    }

    onTagInput(inputId, value) {
        const dropdown = document.getElementById(`${inputId}_dropdown`);
        if (!dropdown) return;

        const query = value.toLowerCase().trim();
        const filtered = this.allTags.filter(tag =>
            !this._selectedTags.includes(tag.tag) &&
            tag.tag.toLowerCase().includes(query)
        );

        if (filtered.length === 0 && !query) {
            dropdown.classList.add('hidden');
            return;
        }

        let items = filtered.map(tag => `
            <div class="tag-dropdown-item" onmousedown="app.selectTag('${inputId}', '${tag.tag}')">
                ${tag.tag}
            </div>
        `).join('');

        if (query && !this.allTags.some(t => t.tag.toLowerCase() === query) && !this._selectedTags.some(t => t.toLowerCase() === query)) {
            items += `
                <div class="tag-dropdown-item tag-dropdown-new" onmousedown="app.selectTag('${inputId}', '${value.trim()}')">
                    + Add "${value.trim()}"
                </div>
            `;
        }

        if (items) {
            dropdown.innerHTML = items;
            dropdown.classList.remove('hidden');
        } else {
            dropdown.classList.add('hidden');
        }
    }

    onTagKeydown(event, inputId) {
        if (event.key === 'Enter' || event.key === ',') {
            event.preventDefault();
            const input = document.getElementById(inputId);
            const value = input.value.trim().replace(/,$/, '');
            if (value && !this._selectedTags.includes(value)) {
                this._selectedTags.push(value);
                this.refreshTagChips(inputId);
            }
            input.value = '';
            const dropdown = document.getElementById(`${inputId}_dropdown`);
            if (dropdown) dropdown.classList.add('hidden');
        }
    }

    selectTag(inputId, tag) {
        if (!this._selectedTags.includes(tag)) {
            this._selectedTags.push(tag);
            this.refreshTagChips(inputId);
        }
        const input = document.getElementById(inputId);
        if (input) {
            input.value = '';
        }
        const dropdown = document.getElementById(`${inputId}_dropdown`);
        if (dropdown) dropdown.classList.add('hidden');
    }

    removeTag(inputId, tag) {
        this._selectedTags = this._selectedTags.filter(t => t !== tag);
        this.refreshTagChips(inputId);
    }

    refreshTagChips(inputId) {
        const chipsContainer = document.getElementById(`${inputId}_chips`);
        const hiddenInput = document.getElementById(`${inputId}_value`);
        if (chipsContainer) {
            chipsContainer.innerHTML = this._selectedTags.map(tag => `
                <span class="inline-flex items-center bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm font-semibold">
                    ${tag}
                    <button type="button" onclick="app.removeTag('${inputId}', '${tag}')" class="ml-1 text-orange-500 hover:text-orange-800 font-bold">&times;</button>
                </span>
            `).join('');
        }
        if (hiddenInput) {
            hiddenInput.value = this._selectedTags.join(',');
        }
    }

    // ===== NAVIGATION HEADER HELPER =====

    renderNavHeader(options) {
        const { backLabel, backAction, title, subtitle, rightButtons } = options;
        return `
            <header class="hanuman-primary shadow-md">
                <div class="max-w-4xl mx-auto px-4 py-4 sm:py-6">
                    <div class="flex items-center gap-3 mb-3">
                        <button onclick="${backAction}" class="nav-back-btn">
                            <span class="text-lg">&#8592;</span> ${backLabel}
                        </button>
                    </div>
                    <div class="flex items-start justify-between gap-4">
                        <div class="flex-1">
                            <h1 class="text-2xl sm:text-3xl font-bold text-white">
                                ${title}
                            </h1>
                            ${subtitle ? `<p class="text-orange-100 mt-2">${subtitle}</p>` : ''}
                        </div>
                        ${rightButtons ? `<div class="flex gap-2">${rightButtons}</div>` : ''}
                    </div>
                </div>
            </header>
        `;
    }

    // ===== RENDER METHODS =====

    renderHome() {
        // Save mobile tags section state before render
        const mobileTagsSection = document.getElementById('mobile-tags-section');
        if (mobileTagsSection) {
            this.mobileTagsOpen = !mobileTagsSection.classList.contains('hidden');
        }
        
        const html = `
            <div class="min-h-screen bg-orange-50">
                <!-- Header -->
                <header class="hanuman-primary shadow-md sticky top-0 z-50">
                    <div class="max-w-6xl mx-auto px-4 py-4 sm:py-6">
                        <div class="flex items-center justify-between gap-2 sm:gap-4 flex-wrap">
                            <div class="flex items-center gap-3 flex-1 min-w-0">
                                <img src="/logo-hanuman.png" alt="Belaguru Logo" class="w-12 h-12 sm:w-16 sm:h-16">
                                <!-- LOGO: Using Hanuman logo -->
                                <div class="flex-1 min-w-0">
                                    <h1 class="text-lg sm:text-2xl font-bold text-white leading-tight">
                                        ಶ್ರೀ ಕ್ಷೇತ್ರ ಬೆಲಗೂರು - ಭಜನ ಮಾಲಿಕೆ
                                    </h1>
                                </div>
                            </div>
                            <button onclick="app.setPage('upload')" style="background-color: white; color: #FF6B35; padding: 8px 16px; border: 2px solid white; border-radius: 6px; font-weight: 600; cursor: pointer; white-space: nowrap; flex-shrink: 0;">
                                + Upload
                            </button>
                            <button onclick="window.triggerInstall && window.triggerInstall()" id="install-btn-header" style="background-color: #FF6B35; color: white; padding: 8px 16px; border: 2px solid #FF6B35; border-radius: 6px; font-weight: 600; cursor: pointer; white-space: nowrap; flex-shrink: 0; display: none;">
                                📱 Manual Install
                            </button>
                        </div>
                    </div>
                </header>

                <!-- Saints Banner -->
                <div class="bg-white border-b border-orange-100">
                    <div class="max-w-6xl mx-auto px-4 py-4">
                        <div class="flex items-center justify-center">
                            <img src="/saints/three-gurus.jpg" alt="Shree Kshetra Belaguru - Bindumadhava, Maruti Gurugalu, Veerapratapa" class="w-full max-w-2xl h-auto rounded-lg shadow-md">
                        </div>
                    </div>
                </div>

                <!-- Search Section -->
                <div class="bg-white shadow-sm sticky top-16 z-40 sm:sticky">
                    <div class="max-w-6xl mx-auto px-4 py-4">
                        <input
                            type="text"
                            placeholder="🔍 Search bhajans by title or lyrics..."
                            value="${this.searchQuery}"
                            oninput="app.searchBhajans(this.value)"
                            class="w-full px-4 py-2 border border-orange-200 rounded-lg focus:border-hanuman-orange focus:outline-none focus:ring-2 focus:ring-orange-300"
                        >
                    </div>
                </div>

                <!-- Daily Bhajan Banner -->
                <div class="max-w-6xl mx-auto px-4 py-4">
                    ${this.renderDailyBhajanBanner()}
                </div>

                <!-- Main Content -->

                <div class="max-w-6xl mx-auto px-4 pb-6">
                    <!-- Search Status (NEW) -->
                    <div id="search-status"></div>

                    <!-- Mobile Tag Toggle Button -->
                    <div class="lg:hidden mb-4">
                        <button onclick="app.toggleMobileTags()" 
                                class="w-full px-4 py-3 bg-white border-2 border-orange-200 rounded-lg font-semibold hanuman-accent hover:bg-orange-50 transition">
                            ▼ Filter by Tags
                        </button>
                    </div>
                    
                    <!-- Mobile Tags (Hidden by default) -->
                    <div id="mobile-tags-section" class="hidden lg:hidden mb-4 card">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-bold text-lg hanuman-accent">📑 Tags</h3>
                            ${this.allTags.filter(t => t.count < 5).length > 0 ? `
                                <button onclick="app.toggleShowAllTags()" class="text-xs text-blue-600 hover:underline">
                                    ${this.showAllTags ? 'Hide sparse' : 'Show all'}
                                </button>
                            ` : ""}
                        </div>
                        <!-- Mobile Tag Search Box -->
                        <div class="relative mb-3">
                            <input 
                                id="tag-search-input-mobile"
                                type="text" 
                                placeholder="Search tags..." 
                                value="${this.tagSearchQuery}"
                                class="w-full px-3 py-2 pl-8 pr-8 text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                            />
                            <span class="absolute left-2 top-2.5 text-gray-400">🔍</span>
                            ${this.tagSearchQuery ? `
                                <button 
                                    id="tag-search-clear-mobile"
                                    class="absolute right-2 top-2 text-gray-400 hover:text-gray-600 text-lg leading-none"
                                >×</button>
                            ` : ""}
                        </div>
                        <div class="overflow-y-auto" style="max-height: calc(60vh - 80px);">
                            ${!this.tagSearchQuery && Object.keys(this.tagsByCategory).length > 0 ? `
                                <!-- Popular Tags -->
                                <div class="mb-4">
                                    <h4 class="text-xs font-semibold text-gray-600 mb-2">⭐ POPULAR</h4>
                                    <div class="flex flex-wrap gap-2">
                                        ${this.renderPopularTags().replace(/onclick="app\.filterByTag/g, 'onclick="app.filterByTag').replace(/">/g, '"); document.getElementById(\'mobile-tags-section\').classList.add(\'hidden\'); app.mobileTagsOpen = false;">')}
                                    </div>
                                </div>
                                <div class="border-t border-gray-200 my-3"></div>
                                <!-- By Category -->
                                <h4 class="text-xs font-semibold text-gray-600 mb-2">📂 BY CATEGORY</h4>
                                ${this.renderTagsByCategory().replace(/onclick="app\.filterByTag/g, 'onclick="app.filterByTag').replace(/"\)/g, '"); document.getElementById(\'mobile-tags-section\').classList.add(\'hidden\'); app.mobileTagsOpen = false;"')}
                            ` : `
                                <!-- Search Results -->
                                <div class="space-y-1">
                                    ${(() => {
                                        const filteredTags = this.allTags
                                            .filter(t => this.showAllTags || t.count >= 5)
                                            .filter(t => !this.tagSearchQuery || t.tag.toLowerCase().includes(this.tagSearchQuery));
                                        
                                        if (filteredTags.length === 0) {
                                            return `
                                                <div class="text-center py-8 text-gray-500">
                                                    <p class="text-sm">No tags found</p>
                                                    ${this.tagSearchQuery ? `<p class="text-xs mt-1">Try different keywords</p>` : ''}
                                                </div>
                                            `;
                                        }
                                        
                                        return filteredTags.map(tagObj => `
                                            <button
                                                onclick="app.filterByTag('${tagObj.tag}'); document.getElementById('mobile-tags-section').classList.add('hidden'); app.mobileTagsOpen = false;"
                                                class="w-full text-left px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between ${
                                                    this.selectedTag === tagObj.tag
                                                        ? 'bg-orange-100 hanuman-accent font-semibold'
                                                        : 'hover:bg-orange-50 text-gray-700'
                                                }"
                                            >
                                                <span>${tagObj.tag}</span>
                                                <span class="text-xs ${this.selectedTag === tagObj.tag ? 'text-orange-600' : 'text-gray-500'}">(${tagObj.count})</span>
                                            </button>
                                        `).join('');
                                    })()}
                                </div>
                            `}
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        <!-- Sidebar (Tags) - Desktop Only -->
                        <div class="hidden lg:block lg:col-span-1">
                            <div class="card sticky top-32">
                                <div class="flex items-center justify-between mb-3">
                                    <h3 class="font-bold text-lg hanuman-accent">📑 Tags</h3>
                                    ${this.allTags.filter(t => t.count < 5).length > 0 ? `
                                        <button onclick="app.toggleShowAllTags()" class="text-xs text-blue-600 hover:underline">
                                            ${this.showAllTags ? 'Hide sparse' : 'Show all'}
                                        </button>
                                    ` : ""}
                                </div>
                                <!-- Tag Search Box -->
                                <div class="relative mb-3">
                                    <input 
                                        id="tag-search-input"
                                        type="text" 
                                        placeholder="Search tags..." 
                                        value="${this.tagSearchQuery}"
                                        class="w-full px-3 py-2 pl-8 pr-8 text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                                    />
                                    <span class="absolute left-2 top-2.5 text-gray-400">🔍</span>
                                    ${this.tagSearchQuery ? `
                                        <button 
                                            id="tag-search-clear"
                                            class="absolute right-2 top-2 text-gray-400 hover:text-gray-600 text-lg leading-none"
                                        >×</button>
                                    ` : ""}
                                </div>
                                <div class="overflow-y-auto" style="max-height: calc(100vh - 290px);">
                                    ${!this.tagSearchQuery && Object.keys(this.tagsByCategory).length > 0 ? `
                                        <!-- Popular Tags -->
                                        <div class="mb-4">
                                            <h4 class="text-xs font-semibold text-gray-600 mb-2 px-2">⭐ POPULAR</h4>
                                            <div class="flex flex-wrap gap-2">
                                                ${this.renderPopularTags()}
                                            </div>
                                        </div>
                                        <div class="border-t border-gray-200 my-3"></div>
                                        <!-- By Category -->
                                        <h4 class="text-xs font-semibold text-gray-600 mb-2 px-2">📂 BY CATEGORY</h4>
                                        ${this.renderTagsByCategory()}
                                    ` : `
                                        <!-- Search Results -->
                                        <div class="space-y-1">
                                            ${(() => {
                                                const filteredTags = this.allTags
                                                    .filter(t => this.showAllTags || t.count >= 5)
                                                    .filter(t => !this.tagSearchQuery || t.tag.toLowerCase().includes(this.tagSearchQuery));
                                                
                                                if (filteredTags.length === 0) {
                                                    return `
                                                        <div class="text-center py-8 text-gray-500">
                                                            <p class="text-sm">No tags found</p>
                                                            ${this.tagSearchQuery ? `<p class="text-xs mt-1">Try different keywords</p>` : ''}
                                                        </div>
                                                    `;
                                                }
                                                
                                                return filteredTags.map(tagObj => `
                                                    <button
                                                        onclick="app.filterByTag('${tagObj.tag}')"
                                                        class="w-full text-left px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between ${
                                                            this.selectedTag === tagObj.tag
                                                                ? 'bg-orange-100 hanuman-accent font-semibold'
                                                                : 'hover:bg-orange-50 text-gray-700'
                                                        }"
                                                    >
                                                        <span>${tagObj.tag}</span>
                                                        <span class="text-xs ${this.selectedTag === tagObj.tag ? 'text-orange-600' : 'text-gray-500'}">(${tagObj.count})</span>
                                                    </button>
                                                `).join('');
                                            })()}
                                        </div>
                                    `}
                                </div>
                            </div>
                        </div>

                        <!-- Bhajans Grid -->
                        <div class="lg:col-span-3" id="bhajans-grid-container">
                            <div class="space-y-4" id="bhajans-grid">
                                ${this.filteredBhajans.length > 0 ? `
                                    ${this.filteredBhajans.map(bhajan => `
                                        <div class="card cursor-pointer transform hover:scale-105 transition-transform"
                                             onclick="app.setPage('bhajan', ${bhajan.id})">
                                            <div class="flex items-start justify-between gap-4">
                                                <div class="flex-1 min-w-0">
                                                    <h3 class="font-bold text-lg hanuman-text truncate">
                                                        ${bhajan.title}
                                                    </h3>
                                                    <p class="text-gray-600 text-sm mt-1">
                                                        By <span class="font-semibold">${bhajan.uploader_name}</span> •
                                                        <time>${new Date(bhajan.created_at).toLocaleDateString()}</time>
                                                    </p>
                                                    <p class="text-gray-700 text-sm mt-3 line-clamp-2">
                                                        ${bhajan.lyrics.substring(0, 150)}...
                                                    </p>
                                                    <div class="flex flex-wrap gap-2 mt-3">
                                                        ${bhajan.tags.map(tag => `
                                                            <span class="inline-block bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-medium">
                                                                ${tag}
                                                            </span>
                                                        `).join('')}
                                                    </div>
                                                </div>
                                                <div class="text-2xl flex-shrink-0">🙏</div>
                                            </div>
                                        </div>
                                    `).join('')}
                                ` : `
                                    <div class="card text-center py-12">
                                        <p class="text-gray-500 text-lg">
                                            No bhajans found. Be the first to upload! 🎵
                                        </p>
                                        <button onclick="app.setPage('upload')" class="btn-primary mt-4">
                                            Upload Bhajan
                                        </button>
                                    </div>
                                `}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.appContainer.innerHTML = html + this.renderFloatingMenu();
        this.renderSearchStatus(); // Initialize search status on load
        
        // Attach tag search event listeners using window.app reference
        setTimeout(() => {
            const tagSearchInput = document.getElementById('tag-search-input');
            const tagSearchInputMobile = document.getElementById('tag-search-input-mobile');
            const tagSearchClear = document.getElementById('tag-search-clear');
            const tagSearchClearMobile = document.getElementById('tag-search-clear-mobile');
            
            if (tagSearchInput) {
                tagSearchInput.oninput = function(e) {
                    if (window.app) {
                        window.app.tagSearchQuery = e.target.value.toLowerCase();
                        window.app.renderHome();
                        // Restore focus after render
                        setTimeout(() => {
                            const input = document.getElementById('tag-search-input');
                            if (input) {
                                input.focus();
                                input.setSelectionRange(input.value.length, input.value.length);
                            }
                        }, 0);
                    }
                };
            }
            
            if (tagSearchInputMobile) {
                tagSearchInputMobile.oninput = function(e) {
                    if (window.app) {
                        window.app.tagSearchQuery = e.target.value.toLowerCase();
                        window.app.renderHome();
                        // Restore focus after render (longer delay for mobile browsers)
                        setTimeout(() => {
                            const input = document.getElementById('tag-search-input-mobile');
                            if (input) {
                                input.focus();
                                // Force focus on mobile
                                input.click();
                                input.setSelectionRange(input.value.length, input.value.length);
                            }
                        }, 50);
                    }
                };
            }
            
            if (tagSearchClear) {
                tagSearchClear.onclick = function() {
                    if (window.app) {
                        window.app.tagSearchQuery = "";
                        window.app.renderHome();
                    }
                };
            }
            
            if (tagSearchClearMobile) {
                tagSearchClearMobile.onclick = function() {
                    if (window.app) {
                        window.app.tagSearchQuery = "";
                        window.app.renderHome();
                    }
                };
            }
            
            // Restore mobile tags section state after render
            if (window.app && window.app.mobileTagsOpen) {
                const mobileTagsSection = document.getElementById('mobile-tags-section');
                if (mobileTagsSection) {
                    mobileTagsSection.classList.remove('hidden');
                }
            }
        }, 0);
    }

    renderUpload() {
        const html = `
            <div class="min-h-screen bg-orange-50">
                ${this.renderNavHeader({
                    backLabel: 'Back to Bhajans',
                    backAction: "app.setPage('home')",
                    title: 'Upload Bhajan',
                    subtitle: 'Share your favorite bhajan with the community'
                })}

                <!-- Upload Form -->
                <div class="max-w-2xl mx-auto px-4 py-8">
                    <form onsubmit="app.handleUploadSubmit(event)" class="space-y-6">
                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Bhajan Title *
                            </label>
                            <input
                                type="text"
                                id="title"
                                placeholder="E.g., Hanuman Chalisa"
                                required
                            >
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Lyrics *
                            </label>
                            <textarea
                                id="lyrics"
                                placeholder="Paste the full bhajan lyrics here..."
                                rows="12"
                                required
                                style="resize: vertical;"
                            ></textarea>
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Tags
                            </label>
                            ${this.renderHierarchicalTagSelector('tags', [])}
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Your Name (optional)
                            </label>
                            <input
                                type="text"
                                id="uploader_name"
                                placeholder="Leave blank for Anonymous"
                            >
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                YouTube Video URL (optional)
                            </label>
                            <input
                                type="url"
                                id="youtube_url"
                                placeholder="https://youtube.com/watch?v=..."
                            >
                            <small style="color:#666;margin-top:4px;display:block;">Paste full YouTube URL or video ID</small>
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                MP3 Audio File (optional)
                            </label>
                            <input
                                type="file"
                                id="mp3_file"
                                name="mp3_file"
                                accept=".mp3"
                                onchange="app.handleMp3FileChange(this)"
                                class="mp3-file-input"
                            >
                            <small id="mp3-file-info" style="color:#666;margin-top:4px;display:block;">Max 5MB • MP3 format only</small>
                        </div>

                        <div class="card bg-orange-50 border-l-4 border-orange-400">
                            <p class="text-sm text-gray-700">
                                ✨ <span class="font-semibold">Community Upload:</span> Your bhajan will be visible to everyone. Please ensure you have the rights to share it.
                            </p>
                        </div>

                        <button type="submit" class="btn-primary w-full py-3 text-lg font-bold">
                            Upload Bhajan 🎵
                        </button>
                    </form>
                </div>
            </div>
        `;

        this.appContainer.innerHTML = html + this.renderFloatingMenu();
    }

    handleMp3FileChange(input, mode = 'create') {
        const fileInfoId = mode === 'edit' ? 'edit-mp3-file-info' : 'mp3-file-info';
        const fileInfo = document.getElementById(fileInfoId);
        
        if (input.files && input.files[0]) {
            const file = input.files[0];
            const sizeMB = (file.size / 1024 / 1024).toFixed(2);
            
            if (this.validateMp3File(file)) {
                fileInfo.textContent = `✅ ${file.name} (${sizeMB}MB)`;
                fileInfo.style.color = '#059669';
            } else {
                input.value = ''; // Clear invalid file
                fileInfo.textContent = mode === 'edit' ? 'Max 5MB • MP3 format only' : 'Max 5MB • MP3 format only';
                fileInfo.style.color = '#666';
            }
        } else {
            fileInfo.textContent = mode === 'edit' ? 'Max 5MB • MP3 format only' : 'Max 5MB • MP3 format only';
            fileInfo.style.color = '#666';
        }
    }

    handleUploadSubmit(event) {
        event.preventDefault();

        const title = document.getElementById("title").value.trim();
        const lyrics = document.getElementById("lyrics").value.trim();
        const tagIdsValue = document.getElementById("selected_tag_ids").value;
        const tagIds = tagIdsValue ? tagIdsValue.split(",").map(id => parseInt(id.trim())).filter(id => !isNaN(id)) : [];
        const uploader_name = document.getElementById("uploader_name").value.trim();
        const youtube_url = document.getElementById("youtube_url").value.trim();
        const mp3Input = document.getElementById("mp3_file");
        const mp3_file = mp3Input && mp3Input.files[0] ? mp3Input.files[0] : null;

        if (!title || !lyrics) {
            alert("Please fill in title and lyrics");
            return;
        }

        // Validate MP3 file if provided
        if (mp3_file && !this.validateMp3File(mp3_file)) {
            return;
        }

        this.createBhajan({ title, lyrics, tagIds, uploader_name, youtube_url, mp3_file }).then(success => {
            if (success) {
                alert("Bhajan uploaded successfully! 🎉");
                this.setPage("home");
            }
        });
    }

    renderBhajanDetail(bhajanId) {
        const bhajan = this.bhajans.find(b => b.id === bhajanId);

        if (!bhajan) {
            this.setPage("home");
            return;
        }

        // Store current bhajan for copy
        this._currentBhajan = bhajan;

        const html = `
            <div class="min-h-screen bg-orange-50">
                ${this.renderNavHeader({
                    backLabel: 'Back to Bhajans',
                    backAction: "app.setPage('home')",
                    title: bhajan.title,
                    subtitle: `By <span class="font-semibold">${bhajan.uploader_name}</span> • <time>${new Date(bhajan.created_at).toLocaleDateString()}</time>`,
                    rightButtons: `
                        <button onclick="app.editBhajan(${bhajan.id})" style="background-color: white; color: #FF6B35; padding: 8px 12px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                            ✏️ Edit
                        </button>
                        <button onclick="app.deleteBhajan(${bhajan.id})" style="background-color: #dc2626; color: white; padding: 8px 12px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                            🗑️ Delete
                        </button>
                    `
                })}

                <!-- Content -->
                <div class="max-w-4xl mx-auto px-4 py-8">
                    <!-- Tags -->
                    ${bhajan.tags.length > 0 ? `
                    <div class="card mb-6">
                        <div class="flex flex-wrap gap-2">
                            ${bhajan.tags.map(tag => `
                                <span class="inline-block bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm font-semibold">
                                    ${tag}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}

                    <!-- YouTube Video Player -->
                    ${bhajan.youtube_url ? (function() {
                        let vidId = bhajan.youtube_url;
                        if (bhajan.youtube_url.includes('youtu.be/')) {
                            vidId = bhajan.youtube_url.split('youtu.be/')[1].split('?')[0];
                        } else if (bhajan.youtube_url.includes('v=')) {
                            vidId = bhajan.youtube_url.split('v=')[1].split('&')[0];
                        }
                        return `<div style="margin-bottom:24px;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);"><iframe width="100%" height="400" src="https://www.youtube.com/embed/${vidId}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>`;
                    })() : ''}

                    <!-- MP3 Audio Player -->
                    ${bhajan.mp3_file ? `
                    <div class="card mb-6 audio-player-container">
                        <h3 class="text-lg font-bold hanuman-text mb-3">🎵 Audio Recording</h3>
                        <audio controls class="audio-player">
                            <source src="/static/audio/${bhajan.mp3_file}" type="audio/mpeg">
                            Your browser doesn't support audio playback.
                        </audio>
                    </div>
                    ` : ''}

                    <!-- Lyrics -->
                    <div class="card">
                        <div class="flex items-center justify-between mb-4">
                            <h2 class="text-2xl font-bold hanuman-text">Lyrics</h2>
                            <button onclick="app.copyLyrics()" class="copy-btn" id="copy-btn">
                                📋 Copy Lyrics
                            </button>
                        </div>
                        <div id="lyrics-content" style="white-space: pre-wrap; color: #374151; line-height: 1.625; font-weight: 500; font-size: 0.875rem;">
${bhajan.lyrics.split('\n').map(line => line.trimStart()).join('\n')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.appContainer.innerHTML = html + this.renderShareButtons(bhajan) + this.renderFloatingMenu();
    }

    copyLyrics() {
        const lyricsEl = document.getElementById('lyrics-content');
        if (!lyricsEl) return;

        const text = lyricsEl.innerText;
        navigator.clipboard.writeText(text).then(() => {
            const btn = document.getElementById('copy-btn');
            if (btn) {
                btn.textContent = '✅ Copied!';
                btn.classList.add('copy-btn-success');
                setTimeout(() => {
                    btn.textContent = '📋 Copy Lyrics';
                    btn.classList.remove('copy-btn-success');
                }, 2000);
            }
        }).catch(() => {
            // Fallback for older browsers
            const range = document.createRange();
            range.selectNodeContents(lyricsEl);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
            try {
                document.execCommand('copy');
                sel.removeAllRanges();
                const btn = document.getElementById('copy-btn');
                if (btn) {
                    btn.textContent = '✅ Copied!';
                    setTimeout(() => { btn.textContent = '📋 Copy Lyrics'; }, 2000);
                }
            } catch (e) {
                alert("Failed to copy. Please select text manually.");
            }
        });
    }

    editBhajan(bhajanId) {
        const bhajan = this.bhajans.find(b => b.id === bhajanId);
        if (!bhajan) return;

        this._selectedTags = [...bhajan.tags];

        const html = `
            <div class="min-h-screen bg-orange-50">
                ${this.renderNavHeader({
                    backLabel: 'Back to Bhajan',
                    backAction: `app.setPage('bhajan', ${bhajanId})`,
                    title: 'Edit Bhajan'
                })}

                <div class="max-w-2xl mx-auto px-4 py-8">
                    <form onsubmit="app.handleEditSubmit(event, ${bhajanId})" class="space-y-6">
                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Bhajan Title
                            </label>
                            <input
                                type="text"
                                id="edit_title"
                                value="${bhajan.title.replace(/"/g, '&quot;')}"
                                placeholder="Bhajan title"
                            >
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Lyrics
                            </label>
                            <textarea
                                id="edit_lyrics"
                                rows="12"
                                style="resize: vertical;"
                                placeholder="Bhajan lyrics..."
                            >${bhajan.lyrics}</textarea>
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Tags
                            </label>
                            ${this.renderHierarchicalTagSelector('edit_tags', [])}
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                Uploader Name
                            </label>
                            <input
                                type="text"
                                id="edit_uploader_name"
                                value="${(bhajan.uploader_name || '').replace(/"/g, '&quot;')}"
                                placeholder="Uploader name"
                            >
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                YouTube Video URL
                            </label>
                            <input
                                type="url"
                                id="edit_youtube_url"
                                value="${(bhajan.youtube_url || '').replace(/"/g, '&quot;')}"
                                placeholder="https://youtube.com/watch?v=..."
                            >
                            <small style="color:#666;margin-top:4px;display:block;">Leave blank if no video</small>
                        </div>

                        <div class="card">
                            <label class="block font-semibold hanuman-text mb-2">
                                MP3 Audio File
                            </label>
                            ${bhajan.mp3_file ? `
                                <div class="mb-3 p-3 bg-green-50 rounded border border-green-200">
                                    <p class="text-sm text-green-700 font-semibold">✅ Current MP3: ${bhajan.mp3_file}</p>
                                </div>
                            ` : ''}
                            <input
                                type="file"
                                id="edit_mp3_file"
                                name="mp3_file"
                                accept=".mp3"
                                onchange="app.handleMp3FileChange(this, 'edit')"
                                class="mp3-file-input"
                            >
                            <small id="edit-mp3-file-info" style="color:#666;margin-top:4px;display:block;">${bhajan.mp3_file ? 'Upload new MP3 to replace current one' : 'Max 5MB • MP3 format only'}</small>
                        </div>

                        <button type="submit" class="btn-primary w-full py-3 text-lg font-bold">
                            Save Changes ✅
                        </button>
                    </form>
                </div>
            </div>
        `;

        this.appContainer.innerHTML = html + this.renderShareButtons(bhajan) + this.renderFloatingMenu();
    }

    handleEditSubmit(event, bhajanId) {
        event.preventDefault();

        const title = document.getElementById("edit_title").value.trim();
        const lyrics = document.getElementById("edit_lyrics").value.trim();
        const tagsValue = document.getElementById("edit_tags_value").value;
        const tags = tagsValue ? tagsValue.split(",").map(t => t.trim()).filter(t => t) : [];
        const uploader_name = document.getElementById("edit_uploader_name").value.trim();
        const youtube_url = document.getElementById("edit_youtube_url").value.trim();
        const mp3Input = document.getElementById("edit_mp3_file");
        const mp3_file = mp3Input && mp3Input.files[0] ? mp3Input.files[0] : null;

        // Validate MP3 file if provided
        if (mp3_file && !this.validateMp3File(mp3_file)) {
            return;
        }

        const formData = new FormData();
        if (title) formData.append("title", title);
        if (lyrics) formData.append("lyrics", lyrics);
        formData.append("tags", tags.join(","));
        if (uploader_name) formData.append("uploader_name", uploader_name);
        if (youtube_url) formData.append("youtube_url", youtube_url);
        if (mp3_file) formData.append("mp3_file", mp3_file);

        fetch(`/api/bhajans/${bhajanId}`, {
            method: "PUT",
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error("Update failed");
            return response.json();
        })
        .then(data => {
            alert("Bhajan updated! ✅");
            this.loadBhajans().then(() => {
                this.loadTags();
                this.setPage("bhajan", bhajanId);
            });
        })
        .catch(error => alert(`Error: ${error.message}`));
    }

    deleteBhajan(bhajanId) {
        if (!confirm("Are you sure you want to delete this bhajan? This cannot be undone.")) {
            return;
        }

        fetch(`/api/bhajans/${bhajanId}`, {
            method: "DELETE"
        })
        .then(response => response.json())
        .then(data => {
            alert("Bhajan deleted! 🗑️");
            this.loadBhajans();
            this.setPage("home");
        })
        .catch(error => alert(`Error: ${error.message}`));
    }

    // ===== FLOATING MENU & DAILY BHAJAN =====
    
    toggleFloatingMenu() {
        const menu = document.getElementById('floating-menu');
        if (menu) menu.classList.toggle('visible');
        const btn = document.getElementById('floating-menu-button');
        if (btn) btn.classList.toggle('open');
    }

    closeFloatingMenu() {
        const menu = document.getElementById('floating-menu');
        const btn = document.getElementById('floating-menu-button');
        if (menu) menu.classList.remove('visible');
        if (btn) btn.classList.remove('open');
    }

    getDailyBhajan() {
        if (this.bhajans.length === 0) return null;
        const today = new Date();
        const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 86400000);
        const index = dayOfYear % this.bhajans.length;
        return this.bhajans[index];
    }

    showDailyBhajan() {
        const daily = this.getDailyBhajan();
        if (!daily) {
            alert("No bhajans available yet!");
            return;
        }
        this.closeFloatingMenu();
        this.setPage('bhajan', daily.id);
    }

    changeFontSize(size) {
        const body = document.body;
        body.classList.remove('font-size-small', 'font-size-normal', 'font-size-large');
        body.classList.add(`font-size-${size}`);
        localStorage.setItem('bhajan-font-size', size);
        const buttons = document.querySelectorAll('.font-size-controls button');
        buttons.forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
        this.closeFloatingMenu();
    }

    // Easter egg: Tap version 5 times to access admin
    easterEggTap() {
        this.easterEggCount = (this.easterEggCount || 0) + 1;
        clearTimeout(this.easterEggTimeout);
        
        if (this.easterEggCount >= 5) {
            this.easterEggCount = 0;
            this.closeFloatingMenu();
            window.location.href = '/admin/tags';
        } else {
            // Reset count after 2 seconds of no taps
            this.easterEggTimeout = setTimeout(() => {
                this.easterEggCount = 0;
            }, 2000);
        }
    }

    loadFontSizePreference() {
        const saved = localStorage.getItem('bhajan-font-size') || 'normal';
        document.body.classList.add(`font-size-${saved}`);
    }

    renderFloatingMenu() {
        const daily = this.getDailyBhajan();
        const savedFontSize = localStorage.getItem('bhajan-font-size') || 'normal';
        return `
            <button id="floating-menu-button" class="floating-menu-button" onclick="app.toggleFloatingMenu()" title="Menu">
                ⚙️
            </button>
            <div id="floating-menu" class="floating-menu">
                <!-- Navigation -->
                <div class="floating-menu-item" onclick="app.setPage('home'); app.closeFloatingMenu();">
                    <span class="floating-menu-item-icon">🏠</span>
                    <span>Home</span>
                </div>
                <div class="floating-menu-item" onclick="app.openSearch(); app.closeFloatingMenu();">
                    <span class="floating-menu-item-icon">🔍</span>
                    <span>Search</span>
                </div>
                <div class="floating-menu-item" onclick="app.setPage('upload'); app.closeFloatingMenu();">
                    <span class="floating-menu-item-icon">📝</span>
                    <span>Upload</span>
                </div>
                <div class="floating-menu-item" onclick="app.setPage('favorites'); app.closeFloatingMenu();">
                    <span class="floating-menu-item-icon">❤️</span>
                    <span>Favorites</span>
                </div>
                
                <div class="floating-menu-divider"></div>
                
                <!-- Daily Bhajan -->
                ${this.bhajans.length > 0 ? `
                    <div class="floating-menu-item" onclick="app.showDailyBhajan()">
                        <span class="floating-menu-item-icon">🎵</span>
                        <span>Daily Bhajan</span>
                    </div>
                ` : ''}
                
                <!-- Font Size -->
                <div class="floating-menu-divider"></div>
                <div class="font-size-controls">
                    <span style="font-size: 11px; font-weight: 700; color: #666; display: block; margin-bottom: 6px;">Font Size</span>
                    <button onclick="app.changeFontSize('small')" class="${savedFontSize === 'small' ? 'active' : ''}">A</button>
                    <button onclick="app.changeFontSize('normal')" class="${savedFontSize === 'normal' ? 'active' : ''}"><strong>A</strong></button>
                    <button onclick="app.changeFontSize('large')" class="${savedFontSize === 'large' ? 'active' : ''}"><strong style="font-size: 18px;">A</strong></button>
                </div>
                
                <!-- Easter Egg: Tap 5 times to reveal admin -->
                <div class="floating-menu-divider" style="margin-top: 8px;"></div>
                <div class="easter-egg-trigger" onclick="app.easterEggTap()" style="padding: 8px; text-align: center; cursor: pointer; user-select: none;">
                    <span style="font-size: 10px; color: #999;">🕉️ v1.0</span>
                </div>
            </div>
        `;
    }

    renderDailyBhajanBanner() {
        const daily = this.getDailyBhajan();
        if (!daily) return '';
        const today = new Date();
        const options = { weekday: 'long', month: 'short', day: 'numeric' };
        const dateStr = today.toLocaleDateString('en-US', options);
        return `
            <div class="daily-bhajan-banner" onclick="app.setPage('bhajan', ${daily.id})">
                <h3>🎵 TODAY'S BHAJAN - ${dateStr}</h3>
                <p>${daily.title}</p>
            </div>
        `;
    }


    
    openSearch() { 
        this.setPage('home'); 
        setTimeout(() => { 
            const input = document.querySelector('input[placeholder*="Search"]'); 
            if(input) input.focus(); 
        }, 100); 
    }

    renderShareButtons(bhajan) { 
        const isFav = this.isFavorited(bhajan.id);
        const heartIcon = isFav ? '❤️' : '🤍';
        const heartTitle = isFav ? 'Remove from favorites' : 'Add to favorites';
        return `<div class="share-button-group">
            <button class="icon-btn" onclick="app.shareWhatsApp('${bhajan.title.replace(/'/g, "\"'")}', '${bhajan.id}')"><img src="/whatsapp-logo.svg" alt=""></button>
            <button class="icon-btn" onclick="app.shareTelegram('${bhajan.title.replace(/'/g, "\"'")}', '${bhajan.id}')"><img src="/telegram-logo.svg" alt=""></button>
            <button class="icon-btn" onclick="app.copyLink('${bhajan.id}')">🔗</button>
            <button class="icon-btn" onclick="app.toggleFavorite('${bhajan.id}', '${bhajan.title.replace(/'/g, "\'")}' )" title="${heartTitle}">${heartIcon}</button>
        </div>`; 
    }


    downloadBhajan(title, preview) {
        const text = title + '\n\n' + preview;
        const a = document.createElement('a');
        a.href = 'data:text/plain,' + encodeURIComponent(text);
        a.download = title + '.txt';
        a.click();
    }

    shareWhatsApp(title, bhajanId) {
        const url = bhajanId ? `https://bhajans.s365.in?bhajan=${bhajanId}` : 'https://bhajans.s365.in'; const msg = encodeURIComponent('Check out this bhajan: ' + title + '\n' + url);
        window.open('https://wa.me/?text=' + msg, '_blank');
    }

    shareTelegram(title, bhajanId) {
        const url = bhajanId ? `https://bhajans.s365.in?bhajan=${bhajanId}` : 'https://bhajans.s365.in';
        const msg = encodeURIComponent('Check out: ' + title);
        window.open('https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + msg, '_blank');
    }

    copyLink(id) {
        const link = `https://bhajans.s365.in?bhajan=${id}`;
        navigator.clipboard.writeText(link).then(() => {
            const feedback = document.createElement('div');
            feedback.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#FF6B35;color:white;padding:12px 20px;border-radius:8px;z-index:1000;font-weight:bold;';
            feedback.textContent = '✅ Link copied!';
            document.body.appendChild(feedback);
            setTimeout(() => feedback.remove(), 2000);
        });
    }

    renderSettings() { 
        const html = `<div class="min-h-screen bg-orange-50">
            ${this.renderNavHeader({backLabel:'Back', backAction:"app.setPage('home')", title:'Settings', subtitle:'Customize your experience'})}
            <div class="max-w-2xl mx-auto px-4 py-8">
                <div class="card">
                    <h3 class="font-semibold hanuman-text mb-4">Font Size</h3>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button onclick="app.changeFontSize('small')" class="py-2 px-4 bg-white border-2 border-orange-200 rounded hover:bg-orange-50">Small</button>
                        <button onclick="app.changeFontSize('normal')" class="py-2 px-4 bg-white border-2 border-orange-200 rounded hover:bg-orange-50">Normal</button>
                        <button onclick="app.changeFontSize('large')" class="py-2 px-4 bg-white border-2 border-orange-200 rounded hover:bg-orange-50">Large</button>
                    </div>
                </div>
            </div>
        </div>`; 
        this.appContainer.innerHTML = html + this.renderFloatingMenu() + this.renderBottomTabBar('settings'); 
    }
    
    renderFavorites() { 
        const favIds = this.getFavorites();
        const favorites = this.bhajans.filter(b => favIds.includes(b.id));

        const html = `<div class="min-h-screen bg-orange-50">
            ${this.renderNavHeader({backLabel:'Back', backAction:"app.setPage('home')", title:'Favorites', subtitle:'Your saved bhajans'})}
            <div class="max-w-6xl mx-auto px-4 py-8">
                ${favorites.length > 0 ? `
                    <div class="grid gap-4">
                        ${favorites.map(b => `
                            <div class="card cursor-pointer hover:shadow-lg" onclick="app.setPage('bhajan', ${b.id})">
                                <div class="flex justify-between items-start gap-3">
                                    <div class="flex-1">
                                        <h3 class="font-semibold hanuman-text">${b.title}</h3>
                                        <p class="text-sm text-gray-600 mt-1">${b.uploader_name || 'Community'}</p>
                                    </div>
                                    <button class="text-2xl hover:scale-110" onclick="event.stopPropagation(); app.toggleFavorite(${b.id}, '${b.title.replace(/'/g, "\'")}')">❤️</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div class="card text-center py-12">
                        <p class="text-gray-500">No favorites yet</p>
                        <p class="text-gray-400 text-sm mt-2">Click ❤️ on any bhajan to save it!</p>
                    </div>
                `}
            </div>
        </div>`; 
        this.appContainer.innerHTML = html + this.renderFloatingMenu(); 
    }



    // ===== FAVORITES =====
    getFavorites() {
        const saved = localStorage.getItem('bhajan_favorites');
        if (!saved) return [];
        const parsed = JSON.parse(saved);
        return parsed.map(id => parseInt(id));
    }

    saveFavorites(favs) {
        const numericFavs = favs.map(id => parseInt(id));
        localStorage.setItem('bhajan_favorites', JSON.stringify(numericFavs));
    }

    isFavorited(bhajanId) {
        return this.getFavorites().includes(bhajanId);
    }

    toggleFavorite(bhajanId, bhajanTitle) {
        try {
            bhajanId = parseInt(bhajanId);
            const favs = this.getFavorites();
            const idx = favs.indexOf(bhajanId);
            let message = '';
            
            if (idx > -1) {
                favs.splice(idx, 1);
                message = '❌ Removed from favorites';
            } else {
                favs.push(bhajanId);
                message = '❤️ Added to favorites!';
            }
            
            this.saveFavorites(favs);
            this.showFavoriteFeedback(message);
            
            // Refresh to update heart icon
            setTimeout(() => {
                this.setPage('bhajan', bhajanId);
            }, 800);
        } catch(err) {
            console.error('Favorite error:', err);
            alert('Error saving favorite: ' + err.message);
        }
    }

    showFavoriteFeedback(message) {
        const el = document.createElement('div');
        el.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#FF6B35;color:white;padding:16px 32px;border-radius:12px;z-index:1001;font-weight:bold;font-size:18px;box-shadow:0 4px 12px rgba(0,0,0,0.2);';
        el.textContent = message;
        document.body.appendChild(el);
        
        // Animate in
        el.style.animation = 'slideIn 0.4s ease';
        
        setTimeout(() => {
            el.style.animation = 'slideOut 0.4s ease';
            setTimeout(() => el.remove(), 400);
        }, 1200);
    }

    // ===== URL ROUTING =====
    updateURL(page, id) {
        let url = window.location.pathname;
        if (page === 'bhajan' && id) {
            url += `?bhajan=${id}`;
        }
        window.history.pushState({ page, id }, '', url);
    }

    loadFromURL() {
        const params = new URLSearchParams(window.location.search);
        const bhajanId = parseInt(params.get('bhajan'));
        if (bhajanId) {
            const bhajan = this.bhajans.find(b => b.id === bhajanId);
            if (bhajan) {
                this.setPage('bhajan', bhajanId);
                return;
            }
        }
        this.renderHome();
    }

    initURLListener() {
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.page === 'bhajan') {
                this.setPage('bhajan', event.state.id);
            } else {
                this.setPage('home');
            }
        });
    }

}

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    try {
        console.log("🦁 Simba: Starting app initialization...");
        window.app = new BelaGuruApp();
        console.log("🦁 Simba: App initialized successfully!");
    } catch (error) {
        console.error("🦁 SIMBA ERROR:", error);
        document.getElementById("app").innerHTML = `
            <div style="padding: 20px; color: red; font-family: Arial;">
                <h2>⚠️ App Error</h2>
                <p>${error.message}</p>
                <p>${error.stack}</p>
            </div>
        `;
    }
});
