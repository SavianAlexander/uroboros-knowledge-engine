let searchTimeout;
let selectedCategory = "all";
let selectedTag = null;
let currentPreviewPath = null;

document.addEventListener("DOMContentLoaded", () => {
    fetchStats();
    fetchGlobalTags();
    fetchDirectoryTree();
    setupDropZone();
});

async function fetchStats() {
    try {
        const response = await fetch("/api/stats");
        const data = await response.json();
        
        document.getElementById("stat-files").innerText = data.total_files;
        document.getElementById("stat-size").innerText = formatBytes(data.total_size);
        
        if (data.active_directory) {
            document.getElementById("active-dir-label").innerText = getBasename(data.active_directory);
            document.getElementById("active-dir-label").title = data.active_directory;
        }

        renderDistributionChart(data.mime_breakdown, data.total_files);
        renderTimeline(data.timeline);
    } catch (error) {
        console.error("Failed to load statistics:", error);
    }
}

function renderDistributionChart(mimeBreakdown, totalFiles) {
    const container = document.getElementById("svg-chart-container");
    container.innerHTML = "";
    
    if (!mimeBreakdown || mimeBreakdown.length === 0) {
        container.innerHTML = '<div style="font-size: 0.8rem; font-style: italic; color: var(--text-secondary);">No files indexed.</div>';
        return;
    }
    
    mimeBreakdown.forEach(item => {
        const pct = totalFiles > 0 ? Math.round((item.count / totalFiles) * 100) : 0;
        const row = document.createElement("div");
        row.className = "chart-bar-row";
        row.innerHTML = `
            <div class="chart-bar-info">
                <span class="chart-bar-label" title="${item.mime_type}">${item.mime_type}</span>
                <span>${item.count} (${pct}%)</span>
            </div>
            <div class="chart-bar-outer">
                <div class="chart-bar-inner" style="width: ${pct}%"></div>
            </div>
        `;
        container.appendChild(row);
    });
}

function renderTimeline(timeline) {
    const container = document.getElementById("timeline-container");
    container.innerHTML = "";
    
    if (!timeline || timeline.length === 0) {
        container.innerHTML = '<span class="timeline-empty">No indexing activity recorded.</span>';
        return;
    }
    
    timeline.forEach(item => {
        const row = document.createElement("div");
        row.className = "timeline-row";
        row.innerHTML = `
            <span>${item.day}</span>
            <strong>${item.count} files</strong>
        `;
        container.appendChild(row);
    });
}

function getBasename(path) {
    return path.split(/[\\/]/).pop() || path;
}

function setupDropZone() {
    const dropZone = document.getElementById("drop-zone");
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });
    
    dropZone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        handleFilesUpload(files);
    }, false);

    dropZone.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.onchange = e => {
            handleFilesUpload(e.target.files);
        };
        input.click();
    });
}

async function handleFilesUpload(files) {
    const statusMsg = document.getElementById("indexing-status");
    if (!files || files.length === 0) return;

    statusMsg.innerText = `Uploading ${files.length} file(s)...`;
    
    for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append('file', files[i]);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                console.log(`Uploaded & Indexed: ${files[i].name}`);
            }
        } catch (error) {
            console.error(`Failed to upload ${files[i].name}`, error);
        }
    }
    
    statusMsg.innerText = "Indexing completed successfully.";
    fetchStats();
    fetchGlobalTags();
    fetchDirectoryTree();
    triggerSearch();
}

async function fetchGlobalTags() {
    try {
        const response = await fetch("/api/tags");
        const data = await response.json();
        const container = document.getElementById("sidebar-tags");
        container.innerHTML = "";
        
        if (data.tags.length === 0) {
            container.innerHTML = '<span class="tag-cloud-empty">No tags set yet.</span>';
            return;
        }

        data.tags.forEach(item => {
            const span = document.createElement("span");
            span.className = "tag-pill-sidebar";
            span.innerText = `${item.tag} (${item.count})`;
            span.onclick = () => filterByTag(item.tag);
            container.appendChild(span);
        });
    } catch (error) {
        console.error("Failed to fetch tags:", error);
    }
}

async function fetchDirectoryTree() {
    try {
        const response = await fetch("/api/tree");
        const data = await response.json();
        buildTreeUI(data.files);
    } catch (error) {
        console.error("Failed to fetch directory tree:", error);
    }
}

function buildTreeUI(files) {
    const container = document.getElementById("dir-tree");
    container.innerHTML = "";
    
    if (!files || files.length === 0) {
        container.innerHTML = '<span class="tree-empty">No directory indexed yet.</span>';
        return;
    }

    const root = {};
    files.forEach(f => {
        const parts = f.filepath.split(/[\\/]/);
        let current = root;
        parts.forEach((part, i) => {
            if (!current[part]) {
                current[part] = (i === parts.length - 1) ? { _file: f } : {};
            }
            current = current[part];
        });
    });

    function renderNode(node, name, parentEl) {
        if (node._file) {
            const div = document.createElement("div");
            div.className = "tree-file-title";
            div.innerHTML = `📄 ${name}`;
            div.onclick = () => showPreview(node._file.filepath);
            parentEl.appendChild(div);
        } else {
            const folderDiv = document.createElement("div");
            folderDiv.className = "tree-folder";
            
            const title = document.createElement("div");
            title.className = "tree-folder-title";
            title.innerHTML = `📁 ${name}`;
            
            const content = document.createElement("div");
            content.style.display = "none";
            title.onclick = () => {
                content.style.display = content.style.display === "none" ? "block" : "none";
            };
            
            folderDiv.appendChild(title);
            folderDiv.appendChild(content);
            parentEl.appendChild(folderDiv);
            
            for (const key in node) {
                renderNode(node[key], key, content);
            }
        }
    }

    for (const key in root) {
        renderNode(root[key], key, container);
    }
}

function selectCategory(button) {
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    selectedCategory = button.getAttribute("data-category");
    triggerSearch();
}

function filterByTag(tag) {
    selectedTag = tag;
    const banner = document.getElementById("active-filters");
    const badge = document.getElementById("active-tag-badge");
    badge.innerText = `Tag: ${tag}`;
    banner.classList.remove("hidden");
    triggerSearch();
}

function clearTagFilter() {
    selectedTag = null;
    document.getElementById("active-filters").classList.add("hidden");
    triggerSearch();
}

function triggerSearch() {
    clearTimeout(searchTimeout);
    const query = document.getElementById("search-input").value.trim();

    searchTimeout = setTimeout(async () => {
        if (selectedCategory === "duplicates") {
            fetchDuplicates();
            return;
        }

        document.getElementById("results-title-header").innerText = "Matching Records";
        
        // Read sorting parameters
        const sortBy = document.getElementById("sort-by-select").value;
        const sortOrder = document.getElementById("sort-order-select").value;
        const dateFilter = document.getElementById("date-filter-select").value;

        let url = `/api/search?`;
        const params = [];
        if (query) params.push(`q=${encodeURIComponent(query)}`);
        if (selectedTag) params.push(`tag=${encodeURIComponent(selectedTag)}`);
        if (selectedCategory && selectedCategory !== "all") params.push(`category=${encodeURIComponent(selectedCategory)}`);
        
        params.push(`sort_by=${sortBy}`);
        params.push(`sort_order=${sortOrder}`);
        params.push(`date_filter=${dateFilter}`);
        
        url += params.join("&");

        try {
            const response = await fetch(url);
            const data = await response.json();
            renderResults(data.results);
        } catch (error) {
            console.error("Search failed:", error);
        }
    }, 150);
}

async function fetchDuplicates() {
    document.getElementById("results-title-header").innerText = "Duplicate File Sets";
    try {
        const response = await fetch("/api/duplicates");
        const data = await response.json();
        renderDuplicates(data.duplicates);
    } catch (error) {
        console.error("Failed to load duplicates:", error);
    }
}

function renderDuplicates(duplicates) {
    const list = document.getElementById("results-list");
    const countBadge = document.getElementById("results-count");
    list.innerHTML = "";
    countBadge.innerText = `${duplicates.length} sets found`;

    if (duplicates.length === 0) {
        list.innerHTML = '<div class="empty-state">No duplicate file sets detected. Complete integrity!</div>';
        return;
    }

    duplicates.forEach(set => {
        const div = document.createElement("div");
        div.className = "duplicate-group-card";
        
        let filesHtml = set.files.map(file => `
            <div class="duplicate-file-entry" onclick="showPreview('${file.filepath.replace(/\\/g, '\\\\')}')">
                <div>
                    <strong>${file.filename}</strong><br/>
                    <small style="color: var(--text-secondary); font-size: 0.75rem;">${file.filepath}</small>
                </div>
                <span>➔</span>
            </div>
        `).join("");

        div.innerHTML = `
            <span class="duplicate-hash">SHA256: ${set.sha256}</span>
            <div class="duplicate-files-list">
                ${filesHtml}
            </div>
        `;
        list.appendChild(div);
    });
}

function renderResults(results) {
    const list = document.getElementById("results-list");
    const countBadge = document.getElementById("results-count");
    
    list.innerHTML = "";
    countBadge.innerText = `${results.length} found`;

    if (results.length === 0) {
        list.innerHTML = '<div class="empty-state">No matches found. Try another query/filter.</div>';
        return;
    }

    results.forEach(file => {
        const div = document.createElement("div");
        div.className = "result-item";
        div.onclick = () => showPreview(file.filepath);
        
        let tagsHtml = "";
        if (file.tags && file.tags.length > 0) {
            tagsHtml = `<div class="result-tags">` + 
                file.tags.map(t => `<span class="result-tag-pill">${t}</span>`).join("") + 
                `</div>`;
        }

        const snippetHtml = file.snippet ? `<div class="result-snippet">${file.snippet}</div>` : '';

        div.innerHTML = `
            <div class="result-info-header">
                <div class="result-info">
                    <span class="result-title">${file.filename}</span>
                    <span class="result-path">${file.filepath}</span>
                    <div class="result-meta">
                        <span>${formatBytes(file.file_size)}</span>
                        <span>•</span>
                        <span>${file.mime_type}</span>
                    </div>
                    ${tagsHtml}
                </div>
                <div class="arrow-indicator">➔</div>
            </div>
            ${snippetHtml}
        `;
        list.appendChild(div);
    });
}

async function showPreview(path) {
    try {
        currentPreviewPath = path;
        const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        document.getElementById("preview-title").innerText = data.filename;
        document.getElementById("preview-path").innerText = data.filepath;
        document.getElementById("preview-mime").innerText = data.mime_type;
        document.getElementById("preview-size").innerText = formatBytes(data.file_size);
        document.getElementById("preview-sha").innerText = data.sha256 || 'N/A';
        
        document.getElementById("file-notes-input").value = data.notes || "";
        document.getElementById("notes-status").innerText = "Auto-saves on blur";

        // Render metrics and summary
        const analyticsCard = document.getElementById("preview-analytics-card");
        const wordsSpan = document.getElementById("analytic-words");
        const parasSpan = document.getElementById("analytic-paragraphs");
        const summarySec = document.getElementById("summary-section");
        const summaryContent = document.getElementById("summary-content");

        if (data.word_count !== undefined && data.word_count > 0) {
            analyticsCard.classList.remove("hidden");
            wordsSpan.innerText = `${data.word_count} words (${data.char_count} chars)`;
            parasSpan.innerText = data.paragraph_count;
            if (data.summary) {
                summarySec.classList.remove("hidden");
                summaryContent.innerText = data.summary;
            } else {
                summarySec.classList.add("hidden");
            }
        } else {
            analyticsCard.classList.add("hidden");
            summarySec.classList.add("hidden");
        }

        renderFileTags(data.tags);
        
        const suggContainer = document.getElementById("suggested-tags-container");
        const suggList = document.getElementById("suggested-tags-list");
        suggList.innerHTML = "";
        
        if (data.suggested_tags && data.suggested_tags.length > 0) {
            const unusedSuggs = data.suggested_tags.filter(t => !data.tags.includes(t));
            if (unusedSuggs.length > 0) {
                suggContainer.classList.remove("hidden");
                unusedSuggs.forEach(tag => {
                    const btn = document.createElement("span");
                    btn.className = "suggested-tag-pill";
                    btn.innerText = `+ ${tag}`;
                    btn.onclick = () => addSuggestedTag(tag);
                    suggList.appendChild(btn);
                });
            } else {
                suggContainer.classList.add("hidden");
            }
        } else {
            suggContainer.classList.add("hidden");
        }

        const previewArea = document.getElementById("preview-content-area");
        previewArea.innerHTML = "";

        const suffix = data.filename.split('.').pop().toLowerCase();
        
        if (suffix === 'csv' && data.content) {
            const table = document.createElement("table");
            table.className = "csv-table";
            const lines = data.content.split('\n');
            lines.forEach((line, index) => {
                if (!line.trim()) return;
                const tr = document.createElement("tr");
                const cells = line.split(',');
                cells.forEach(cell => {
                    const el = document.createElement(index === 0 ? "th" : "td");
                    el.innerText = cell.trim();
                    tr.appendChild(el);
                });
                table.appendChild(tr);
            });
            previewArea.appendChild(table);
        } else if (suffix === 'json' && data.content) {
            try {
                const jsonObj = JSON.parse(data.content);
                const pre = document.createElement("pre");
                pre.innerHTML = `<code id="preview-code">${JSON.stringify(jsonObj, null, 2)}</code>`;
                previewArea.appendChild(pre);
            } catch (e) {
                const pre = document.createElement("pre");
                pre.innerHTML = `<code id="preview-code">${data.content}</code>`;
                previewArea.appendChild(pre);
            }
        } else if (data.content) {
            const pre = document.createElement("pre");
            pre.innerHTML = `<code id="preview-code">${data.content}</code>`;
            previewArea.appendChild(pre);
        } else {
            const div = document.createElement("div");
            div.style.padding = "1rem";
            div.style.color = "var(--text-secondary)";
            div.innerText = "[Binary/Image File - Preview Not Available]";
            previewArea.appendChild(div);
        }
        
        document.getElementById("preview-panel").classList.remove("hidden");
        document.querySelector(".main-content").classList.add("with-preview");
    } catch (error) {
        console.error("Failed to load file preview:", error);
    }
}

async function saveFileNotes() {
    if (!currentPreviewPath) return;
    const notesVal = document.getElementById("file-notes-input").value;
    const status = document.getElementById("notes-status");
    
    status.innerText = "Saving notes...";
    try {
        const response = await fetch("/api/file/notes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filepath: currentPreviewPath, notes: notesVal })
        });
        if (response.ok) {
            status.innerText = "Notes saved successfully!";
            triggerSearch();
        }
    } catch (error) {
        status.innerText = "Failed to save annotations.";
    }
}

async function renameFileAction() {
    if (!currentPreviewPath) return;
    const currentName = getBasename(currentPreviewPath);
    const newName = prompt("Enter a new name for the file (including extension):", currentName);
    if (!newName || newName.trim() === "" || newName === currentName) return;

    try {
        const response = await fetch("/api/file/rename", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filepath: currentPreviewPath, new_name: newName.trim() })
        });
        const result = await response.json();
        
        if (response.ok) {
            fetchStats();
            fetchGlobalTags();
            fetchDirectoryTree();
            triggerSearch();
            showPreview(result.new_filepath);
        } else {
            alert(`Rename failed: ${result.detail}`);
        }
    } catch (error) {
        console.error("Failed to rename file:", error);
    }
}

async function deleteFileAction() {
    if (!currentPreviewPath) return;
    const confirmed = confirm("Are you sure you want to permanently delete this file from disk and database?");
    if (!confirmed) return;

    try {
        const response = await fetch(`/api/file/delete?path=${encodeURIComponent(currentPreviewPath)}`, {
            method: "DELETE"
        });
        if (response.ok) {
            closePreview();
            fetchStats();
            fetchGlobalTags();
            fetchDirectoryTree();
            triggerSearch();
        } else {
            const err = await response.json();
            alert(`Delete failed: ${err.detail}`);
        }
    } catch (error) {
        console.error("Delete call failed:", error);
    }
}

async function addSuggestedTag(tag) {
    if (!currentPreviewPath) return;
    try {
        const response = await fetch("/api/file/tag", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filepath: currentPreviewPath, tag })
        });
        if (response.ok) {
            showPreview(currentPreviewPath);
            fetchGlobalTags();
        }
    } catch (error) {
        console.error("Failed to add suggested tag:", error);
    }
}

function renderFileTags(tags) {
    const list = document.getElementById("file-tags-list");
    list.innerHTML = "";
    if (tags && tags.length > 0) {
        tags.forEach(t => {
            const span = document.createElement("span");
            span.className = "tag-badge-pill";
            span.innerHTML = `
                ${t}
                <button class="tag-delete-btn" onclick="removeFileTag('${t}')">✕</button>
            `;
            list.appendChild(span);
        });
    }
}

async function addFileTag() {
    const input = document.getElementById("new-tag-input");
    const tag = input.value.trim();
    if (!tag || !currentPreviewPath) return;

    try {
        const response = await fetch("/api/file/tag", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filepath: currentPreviewPath, tag })
        });
        if (response.ok) {
            input.value = "";
            showPreview(currentPreviewPath);
            fetchGlobalTags();
        }
    } catch (error) {
        console.error("Failed to add tag:", error);
    }
}

async function removeFileTag(tag) {
    if (!currentPreviewPath) return;
    try {
        const response = await fetch(`/api/file/tag?filepath=${encodeURIComponent(currentPreviewPath)}&tag=${encodeURIComponent(tag)}`, {
            method: "DELETE"
        });
        if (response.ok) {
            showPreview(currentPreviewPath);
            fetchGlobalTags();
        }
    } catch (error) {
        console.error("Failed to delete tag:", error);
    }
}

function closePreview() {
    document.getElementById("preview-panel").classList.add("hidden");
    document.querySelector(".main-content").classList.remove("with-preview");
    currentPreviewPath = null;
}

function formatBytes(bytes, decimals = 2) {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
