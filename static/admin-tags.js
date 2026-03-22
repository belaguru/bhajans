/**
 * Belaguru Bhajan Portal - Admin Tag Management
 */

class TagAdmin {
    constructor() {
        this.tags = [];
        this.selectedTag = null;
        this.editingTagId = null;
        this.tagCounts = {};
        this.init();
    }

    async init() {
        await this.loadTree();
        await this.loadStats();
    }

    async loadTree() {
        try {
            const response = await fetch('/api/tags/tree');
            const tree = await response.json();
            
            // Also load tag counts
            const countsResponse = await fetch('/api/tags/counts');
            const counts = await countsResponse.json();
            this.tagCounts = {};
            counts.forEach(tag => {
                this.tagCounts[tag.name] = tag.count;
            });

            this.renderTree(tree);
        } catch (error) {
            console.error('Error loading tag tree:', error);
            this.showError('Failed to load tags');
        }
    }

    renderTree(tree) {
        const container = document.getElementById('treeContainer');
        const html = this.buildTreeHTML(tree);
        container.innerHTML = `<ul class="tag-tree">${html}</ul>`;
    }

    buildTreeHTML(tree, level = 0) {
        let html = '';
        
        for (const [name, data] of Object.entries(tree)) {
            const hasChildren = Object.keys(data.children || {}).length > 0;
            const count = this.tagCounts[name] || 0;
            const expandIcon = hasChildren ? '▶' : '•';
            
            html += `
                <li class="tag-item" data-tag-id="${data.id}">
                    <div class="tag-node" onclick="tagAdmin.selectTag(${data.id}, '${name.replace(/'/g, "\\'")}')">
                        <span class="expand-icon" onclick="event.stopPropagation(); tagAdmin.toggleExpand(event)">${expandIcon}</span>
                        <div class="tag-label">
                            <span class="tag-name">${name}</span>
                            <span class="tag-category">${data.category}</span>
                            ${count > 0 ? `<span class="tag-count">${count} bhajans</span>` : ''}
                        </div>
                    </div>
            `;
            
            if (hasChildren) {
                html += `<ul class="tag-children">${this.buildTreeHTML(data.children, level + 1)}</ul>`;
            }
            
            html += '</li>';
        }
        
        return html;
    }

    toggleExpand(event) {
        const tagNode = event.target.closest('.tag-item');
        const children = tagNode.querySelector('.tag-children');
        const icon = tagNode.querySelector('.expand-icon');
        
        if (children) {
            children.classList.toggle('expanded');
            icon.textContent = children.classList.contains('expanded') ? '▼' : '▶';
        }
    }

    async selectTag(tagId, tagName) {
        // Update selection UI
        document.querySelectorAll('.tag-node').forEach(node => {
            node.classList.remove('selected');
        });
        event.currentTarget.classList.add('selected');

        this.selectedTag = { id: tagId, name: tagName };
        await this.loadTagDetails(tagId);
    }

    async loadTagDetails(tagId) {
        try {
            const response = await fetch(`/api/tags/${tagId}`);
            const tag = await response.json();
            
            this.renderEditor(tag);
        } catch (error) {
            console.error('Error loading tag details:', error);
            this.showError('Failed to load tag details');
        }
    }

    renderEditor(tag) {
        const container = document.getElementById('editorContainer');
        
        const translations = Object.entries(tag.translations || {})
            .map(([lang, trans]) => `
                <div class="translation-item">
                    <input type="text" class="form-input" value="${lang}" readonly>
                    <input type="text" class="form-input" value="${trans}" readonly>
                </div>
            `).join('');

        const synonyms = (tag.synonyms || [])
            .map(syn => `
                <div class="synonym-item">
                    <span class="tag-count">${syn}</span>
                </div>
            `).join('');

        const bhajanCount = this.tagCounts[tag.name] || 0;

        container.innerHTML = `
            <div class="form-group">
                <label class="form-label">Tag Name</label>
                <input type="text" class="form-input" value="${tag.name}" readonly>
            </div>

            <div class="form-group">
                <label class="form-label">Category</label>
                <input type="text" class="form-input" value="${tag.category}" readonly>
            </div>

            <div class="form-group">
                <label class="form-label">Parent</label>
                <input type="text" class="form-input" value="${tag.parent ? tag.parent.name : 'None (Root)'}" readonly>
            </div>

            <div class="form-group">
                <label class="form-label">Usage</label>
                <div class="stat-card">
                    <div class="stat-value">${bhajanCount}</div>
                    <div class="stat-label">Bhajans tagged</div>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Translations</label>
                ${translations || '<p style="color: #6b7280; font-size: 14px;">No translations</p>'}
            </div>

            <div class="form-group">
                <label class="form-label">Synonyms</label>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    ${synonyms || '<p style="color: #6b7280; font-size: 14px;">No synonyms</p>'}
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Children Tags</label>
                ${tag.children.length > 0 
                    ? '<ul>' + tag.children.map(c => `<li style="padding: 4px 0;">${c.name}</li>`).join('') + '</ul>'
                    : '<p style="color: #6b7280; font-size: 14px;">No child tags</p>'}
            </div>

            <div class="form-actions">
                <button class="btn btn-primary" onclick="tagAdmin.editTag(${tag.id})">Edit Tag</button>
                ${bhajanCount === 0 ? `<button class="btn btn-danger" onclick="tagAdmin.deleteTag(${tag.id}, '${tag.name.replace(/'/g, "\\'")}')">Delete Tag</button>` : ''}
            </div>
        `;
    }

    showAddTagModal() {
        this.editingTagId = null;
        document.getElementById('modalTitle').textContent = 'Add New Tag';
        document.getElementById('tagForm').reset();
        document.getElementById('modalAlert').innerHTML = '';
        
        // Load parent options
        this.loadParentOptions();
        
        // Reset translation and synonym lists
        document.getElementById('translationList').innerHTML = '';
        document.getElementById('synonymList').innerHTML = '';
        
        document.getElementById('tagModal').classList.add('active');
    }

    async editTag(tagId) {
        try {
            const response = await fetch(`/api/tags/${tagId}`);
            const tag = await response.json();
            
            this.editingTagId = tagId;
            document.getElementById('modalTitle').textContent = 'Edit Tag';
            document.getElementById('tagName').value = tag.name;
            document.getElementById('tagCategory').value = tag.category;
            
            // Load parent options
            await this.loadParentOptions(tag.parent_id);
            
            // Load translations
            const translationList = document.getElementById('translationList');
            translationList.innerHTML = '';
            Object.entries(tag.translations || {}).forEach(([lang, trans]) => {
                translationList.innerHTML += `
                    <div class="translation-item">
                        <input type="text" class="form-input" value="${lang}" data-type="lang">
                        <input type="text" class="form-input" value="${trans}" data-type="trans">
                        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">×</button>
                    </div>
                `;
            });
            
            // Load synonyms
            const synonymList = document.getElementById('synonymList');
            synonymList.innerHTML = '';
            (tag.synonyms || []).forEach(syn => {
                synonymList.innerHTML += `
                    <div class="synonym-item">
                        <input type="text" class="form-input" value="${syn}">
                        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">×</button>
                    </div>
                `;
            });
            
            document.getElementById('modalAlert').innerHTML = '';
            document.getElementById('tagModal').classList.add('active');
        } catch (error) {
            console.error('Error loading tag for edit:', error);
            this.showError('Failed to load tag');
        }
    }

    async loadParentOptions(selectedParentId = null) {
        try {
            const response = await fetch('/api/tags');
            const tags = await response.json();
            
            const parentSelect = document.getElementById('tagParent');
            parentSelect.innerHTML = '<option value="">None (Root level)</option>';
            
            tags.forEach(tag => {
                // Don't show the tag being edited as a potential parent
                if (this.editingTagId && tag.id === this.editingTagId) return;
                
                const selected = selectedParentId === tag.id ? 'selected' : '';
                const indent = '&nbsp;&nbsp;'.repeat(tag.level);
                parentSelect.innerHTML += `<option value="${tag.id}" ${selected}>${indent}${tag.name} (${tag.category})</option>`;
            });
        } catch (error) {
            console.error('Error loading parent options:', error);
        }
    }

    addTranslation() {
        const list = document.getElementById('translationList');
        const item = document.createElement('div');
        item.className = 'translation-item';
        item.innerHTML = `
            <input type="text" class="form-input" placeholder="Language (e.g., kannada)" data-type="lang">
            <input type="text" class="form-input" placeholder="Translation" data-type="trans">
            <button type="button" class="remove-btn" onclick="this.parentElement.remove()">×</button>
        `;
        list.appendChild(item);
    }

    addSynonym() {
        const list = document.getElementById('synonymList');
        const item = document.createElement('div');
        item.className = 'synonym-item';
        item.innerHTML = `
            <input type="text" class="form-input" placeholder="Synonym">
            <button type="button" class="remove-btn" onclick="this.parentElement.remove()">×</button>
        `;
        list.appendChild(item);
    }

    async saveTag(event) {
        event.preventDefault();
        
        const name = document.getElementById('tagName').value.trim();
        const category = document.getElementById('tagCategory').value;
        const parentId = document.getElementById('tagParent').value;
        
        if (!name || !category) {
            this.showModalError('Name and category are required');
            return;
        }
        
        // Collect translations
        const translations = {};
        document.querySelectorAll('#translationList .translation-item').forEach(item => {
            const lang = item.querySelector('[data-type="lang"]').value.trim();
            const trans = item.querySelector('[data-type="trans"]').value.trim();
            if (lang && trans) {
                translations[lang] = trans;
            }
        });
        
        // Collect synonyms
        const synonyms = [];
        document.querySelectorAll('#synonymList .synonym-item input').forEach(input => {
            const syn = input.value.trim();
            if (syn) synonyms.push(syn);
        });
        
        const data = {
            name,
            category,
            parent_id: parentId ? parseInt(parentId) : null,
            translations,
            synonyms
        };
        
        try {
            const url = this.editingTagId ? `/api/tags/${this.editingTagId}` : '/api/tags';
            const method = this.editingTagId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to save tag');
            }
            
            this.closeModal();
            await this.loadTree();
            await this.loadStats();
            this.showSuccess(this.editingTagId ? 'Tag updated successfully' : 'Tag created successfully');
            
            // Reload the tag if we were editing
            if (this.editingTagId) {
                await this.loadTagDetails(this.editingTagId);
            }
        } catch (error) {
            console.error('Error saving tag:', error);
            this.showModalError(error.message);
        }
    }

    async deleteTag(tagId, tagName) {
        if (!confirm(`Are you sure you want to delete "${tagName}"?\n\nThis action cannot be undone.`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/tags/${tagId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete tag');
            }
            
            this.showSuccess('Tag deleted successfully');
            await this.loadTree();
            await this.loadStats();
            
            // Clear editor
            document.getElementById('editorContainer').innerHTML = `
                <div class="editor-empty">
                    <div class="editor-empty-icon">📝</div>
                    <p>Select a tag from the tree to edit,<br>or click "+ Add Tag" to create a new one</p>
                </div>
            `;
        } catch (error) {
            console.error('Error deleting tag:', error);
            this.showError(error.message);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/tags');
            const tags = await response.json();
            
            const countsResponse = await fetch('/api/tags/counts');
            const counts = await countsResponse.json();
            
            const totalTags = tags.length;
            const activeTags = counts.filter(t => t.count > 0).length;
            const orphans = tags.length - counts.length; // Tags not in counts are orphaned
            
            // Calculate recent (this is approximate - would need created_at in API)
            const recent = 0; // TODO: implement when API supports it
            
            document.getElementById('statTotalTags').textContent = totalTags;
            document.getElementById('statActiveTags').textContent = activeTags;
            document.getElementById('statOrphans').textContent = Math.max(0, orphans);
            document.getElementById('statRecent').textContent = recent;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    closeModal() {
        document.getElementById('tagModal').classList.remove('active');
    }

    showSuccess(message) {
        // Could implement a toast notification system
        alert(message);
    }

    showError(message) {
        // Could implement a toast notification system
        alert('Error: ' + message);
    }

    showModalError(message) {
        const alert = document.getElementById('modalAlert');
        alert.innerHTML = `<div class="alert alert-error">${message}</div>`;
        setTimeout(() => {
            alert.innerHTML = '';
        }, 5000);
    }
}

// Initialize on page load
const tagAdmin = new TagAdmin();
