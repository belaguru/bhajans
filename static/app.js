/**
 * Belaguru Bhajan Portal - Frontend App
 * Shree Kshetra Belaguru - Bhajana Maalika
 * Native Responsive UI, Mobile-First
 */

class BelaGuruApp {
    constructor() {
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
        this.renderHome();
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
        }, 300);
    }

    filterByTag(tag) {
        this.selectedTag = this.selectedTag === tag ? null : tag;
        this.applyFilters();
        this.renderResults();
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
            this.renderHome();
        } else if (page === "upload") {
            this._selectedTags = [];
            this.renderUpload();
        } else if (page === "bhajan" && arguments[1]) {
            this.renderBhajanDetail(arguments[1]);
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
                        <button onclick="app.setPage('home')" class="nav-home-btn" title="Home">
                            <span class="text-lg">&#8962;</span> Home
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

                <!-- Main Content -->
                <div class="max-w-6xl mx-auto px-4 py-6">
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

        this.appContainer.innerHTML = html;
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

        this.appContainer.innerHTML = html;
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

        this.appContainer.innerHTML = html;
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

        this.appContainer.innerHTML = html;
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
}

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    window.app = new BelaGuruApp();
});
