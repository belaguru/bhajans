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
        this.selectedTag = null;
        this.searchQuery = "";
        this.appContainer = document.getElementById("app");
        this.searchTimeout = null;
        // Tag input state for upload/edit forms
        this._selectedTags = [];
        this._tagDropdownVisible = false;

        this.init();
    }

    async init() {
        await this.loadBhajans();
        await this.loadTags();
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
            const response = await fetch("/api/tags");
            this.allTags = await response.json();
        } catch (error) {
            console.error("Error loading tags:", error);
        }
    }

    async createBhajan(data) {
        try {
            const formData = new FormData();
            formData.append("title", data.title);
            formData.append("lyrics", data.lyrics);
            formData.append("tags", data.tags.join(","));
            formData.append("uploader_name", data.uploader_name || "Anonymous");

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
                    <div class="card bg-green-50 border-l-4 border-green-500">
                        <div class="flex items-center justify-between gap-3">
                            <div class="flex-1">
                                <p class="text-sm text-gray-700">
                                    ${filterInfo.join(' + ')}
                                </p>
                                <p class="font-semibold text-green-700 mt-1">
                                    ✅ Found <strong>${count}</strong> ${resultText}
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
                    <div class="card bg-red-50 border-l-4 border-red-500">
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
            !this._selectedTags.includes(tag) &&
            tag.toLowerCase().includes(query)
        );

        if (filtered.length === 0 && !query) {
            dropdown.classList.add('hidden');
            return;
        }

        let items = filtered.map(tag => `
            <div class="tag-dropdown-item" onmousedown="app.selectTag('${inputId}', '${tag}')">
                ${tag}
            </div>
        `).join('');

        if (query && !this.allTags.some(t => t.toLowerCase() === query) && !this._selectedTags.some(t => t.toLowerCase() === query)) {
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
        const html = `
            <div class="min-h-screen bg-orange-50">
                <!-- Header -->
                <header class="hanuman-primary shadow-md sticky top-0 z-50">
                    <div class="max-w-6xl mx-auto px-4 py-4 sm:py-6">
                        <div class="flex items-center justify-between gap-2 sm:gap-4 flex-wrap">
                            <div class="flex items-center gap-3 flex-1 min-w-0">
                                <img src="/logo.png" alt="Belaguru Logo" class="w-12 h-12 sm:w-16 sm:h-16">
                                <!-- LOGO: Replace /logo.png with new Belaguru logo file -->
                                <div class="flex-1 min-w-0">
                                    <h1 class="text-lg sm:text-2xl font-bold text-white leading-tight">
                                        Shree Kshetra Belaguru
                                    </h1>
                                    <p class="text-orange-100 text-xs sm:text-sm mt-0.5 font-semibold">
                                        Bhajana Maalika
                                    </p>
                                </div>
                            </div>
                            <button onclick="app.setPage('upload')" style="background-color: white; color: #FF6B35; padding: 8px 16px; border: 2px solid white; border-radius: 6px; font-weight: 600; cursor: pointer; white-space: nowrap; flex-shrink: 0;">
                                + Upload
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
                <div class="max-w-6xl mx-auto px-4 py-6">
                    <!-- Search Status (NEW) -->
                    <div id="search-status" class="mb-6"></div>

                    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        <!-- Sidebar (Tags) -->
                        <div class="lg:col-span-1">
                            <div class="card sticky top-32">
                                <h3 class="font-bold text-lg mb-4 hanuman-accent">📑 Tags</h3>
                                <div class="space-y-2">
                                    ${this.allTags.map(tag => `
                                        <button
                                            onclick="app.filterByTag('${tag}')"
                                            class="w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                                                this.selectedTag === tag
                                                    ? 'bg-orange-100 hanuman-accent font-semibold'
                                                    : 'hover:bg-orange-50 text-gray-700'
                                            }"
                                        >
                                            ${tag}
                                        </button>
                                    `).join('')}
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
                            ${this.renderTagInputHTML('tags', [])}
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

    handleUploadSubmit(event) {
        event.preventDefault();

        const title = document.getElementById("title").value.trim();
        const lyrics = document.getElementById("lyrics").value.trim();
        const tagsValue = document.getElementById("tags_value").value;
        const tags = tagsValue ? tagsValue.split(",").map(t => t.trim()).filter(t => t) : [];
        const uploader_name = document.getElementById("uploader_name").value.trim();

        if (!title || !lyrics) {
            alert("Please fill in title and lyrics");
            return;
        }

        this.createBhajan({ title, lyrics, tags, uploader_name }).then(success => {
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
                            ${this.renderTagInputHTML('edit_tags', [...bhajan.tags])}
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

        const formData = new FormData();
        if (title) formData.append("title", title);
        if (lyrics) formData.append("lyrics", lyrics);
        formData.append("tags", tags.join(","));
        if (uploader_name) formData.append("uploader_name", uploader_name);

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
        return `<div class="share-button-group">
            <button class="icon-btn" onclick="app.downloadBhajan('${bhajan.title.replace(/'/g, "\"'")}', '${bhajan.lyrics.replace(/'/g, "\"'").substring(0,100)}...')">📥</button>
            <button class="icon-btn" onclick="app.shareWhatsApp('${bhajan.title.replace(/'/g, "\"'")}', '${bhajan.id}')"><img src="/whatsapp-logo.svg" alt=""></button>
            <button class="icon-btn" onclick="app.shareTelegram('${bhajan.title.replace(/'/g, "\"'")}', '${bhajan.id}')"><img src="/telegram-logo.svg" alt=""></button>
            <button class="icon-btn" onclick="app.copyLink('${bhajan.id}')">🔗</button>
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
        const html = `<div class="min-h-screen bg-orange-50">
            ${this.renderNavHeader({backLabel:'Back', backAction:"app.setPage('home')", title:'Favorites', subtitle:'Your saved bhajans'})}
            <div class="max-w-6xl mx-auto px-4 py-8">
                <div class="card text-center py-12">
                    <p class="text-gray-500">No favorites yet</p>
                    <p class="text-gray-400 text-sm mt-2">Click ❤️ on any bhajan to save it!</p>
                </div>
            </div>
        </div>`; 
        this.appContainer.innerHTML = html + this.renderFloatingMenu() + this.renderBottomTabBar('favorites'); 
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
