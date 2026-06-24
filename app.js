let searchTimeout;
let selectedCategory = "all";
let selectedTag = null;
let currentPreviewPath = null;
let searchMode = "keyword"; // "keyword" or "semantic"

let isEditingFile = false;

document.addEventListener("DOMContentLoaded", () => {
    fetchStats();
    fetchGlobalTags();
    fetchDirectoryTree();
    fetchAutoRules();
    fetchPeers();
    fetchSnapshots();
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
        row.onclick = () => {
            let extension = item.mime_type.split('/').pop();
            // Simplify application octet stream / common extensions mapping
            if (extension === 'octet-stream') extension = 'bin';
            const searchInput = document.getElementById("search-input");
            searchInput.value = `type:${extension} ` + searchInput.value.replace(/type:\S+/g, "").trim();
            triggerSearch();
        };
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

async function fetchPeers() {
    try {
        const response = await fetch("/api/sync/peers");
        const data = await response.json();
        renderPeers(data.peers);
    } catch (error) {
        console.error("Failed to load peers", error);
    }
}

function renderPeers(peers) {
    const container = document.getElementById("sidebar-peers");
    container.innerHTML = "";
    if (!peers || peers.length === 0) {
        container.innerHTML = '<span class="rules-empty">No syncing nodes registered.</span>';
        return;
    }
    peers.forEach(peer => {
        const div = document.createElement("div");
        div.className = "rule-item";
        div.innerHTML = `
            <span><strong>${peer.name}</strong> (${peer.address})</span>
            <div>
                <button class="peer-sync-btn" onclick="syncWithPeer('${peer.address}')">Sync</button>
                <button class="rule-del-btn" onclick="deletePeer(${peer.id})">✕</button>
            </div>
        `;
        container.appendChild(div);
    });
}

async function addPeer() {
    const addressInput = document.getElementById("peer-address");
    const nameInput = document.getElementById("peer-name");
    const address = addressInput.value.trim();
    const name = nameInput.value.trim();
    if (!address || !name) return;

    try {
        const response = await fetch("/api/sync/peers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ address, name })
        });
        if (response.ok) {
            addressInput.value = "";
            nameInput.value = "";
            fetchPeers();
        } else {
            const err = await response.json();
            alert(`Failed: ${err.detail}`);
        }
    } catch (e) {
        console.error("Peer registration failed", e);
    }
}

async function deletePeer(id) {
    try {
        const response = await fetch(`/api/sync/peers?id=${id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            fetchPeers();
        }
    } catch (e) {
        console.error("Peer deletion failed", e);
    }
}

async function syncWithPeer(peerAddress) {
    alert(`Starting sync exchange with peer node: ${peerAddress}`);
    try {
        const response = await fetch("/api/sync/exchange", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target_peer: peerAddress })
        });
        const result = await response.json();
        if (response.ok) {
            alert(`Sync completed! Synced ${result.synced.length} new files: ${result.synced.join(", ")}`);
            fetchStats();
            fetchDirectoryTree();
            triggerSearch();
        } else {
            alert(`Sync failed: ${result.detail}`);
        }
    } catch (e) {
        alert(`Sync failed to connect to peer node: ${e}`);
    }
}
function selectCategory(button) {
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    selectedCategory = button.getAttribute("data-category");
    
    const resultsListWrapper = document.getElementById("results-list-wrapper");
    const graphWrapper = document.getElementById("graph-wrapper");
    
    if (selectedCategory === "graph") {
        resultsListWrapper.classList.add("hidden");
        graphWrapper.classList.remove("hidden");
        loadConceptGraph();
    } else {
        resultsListWrapper.classList.remove("hidden");
        graphWrapper.classList.add("hidden");
        triggerSearch();
    }
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

function setSearchMode(mode) {
    searchMode = mode;
    document.querySelectorAll(".mode-btn").forEach(btn => btn.classList.remove("active"));
    document.getElementById(`mode-keyword`).classList.toggle("active", mode === "keyword");
    document.getElementById(`mode-semantic`).classList.toggle("active", mode === "semantic");
    triggerSearch();
}

async function fetchAutoRules() {
    try {
        const response = await fetch("/api/rules");
        const data = await response.json();
        renderAutoRules(data.rules);
    } catch (error) {
        console.error("Failed to load rules:", error);
    }
}

function renderAutoRules(rules) {
    const container = document.getElementById("sidebar-rules");
    container.innerHTML = "";
    if (!rules || rules.length === 0) {
        container.innerHTML = '<span class="rules-empty">No automated tagging rules.</span>';
        return;
    }
    rules.forEach(rule => {
        const div = document.createElement("div");
        div.className = "rule-item";
        div.innerHTML = `
            <span><strong>${rule.pattern}</strong> ➔ <span class="badge" style="font-size: 0.65rem; padding:0 0.3rem">${rule.tag}</span></span>
            <button class="rule-del-btn" onclick="deleteAutoRule(${rule.id})">✕</button>
        `;
        container.appendChild(div);
    });
}

async function addAutoRule() {
    const patInput = document.getElementById("rule-pattern");
    const tagInput = document.getElementById("rule-tag");
    const pattern = patInput.value.trim();
    const tag = tagInput.value.trim();
    if (!pattern || !tag) return;

    try {
        const response = await fetch("/api/rules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pattern, tag })
        });
        if (response.ok) {
            patInput.value = "";
            tagInput.value = "";
            fetchAutoRules();
            fetchStats();
        } else {
            const err = await response.json();
            alert(`Failed: ${err.detail}`);
        }
    } catch (e) {
        console.error("Rule creation failed:", e);
    }
}

async function deleteAutoRule(id) {
    try {
        const response = await fetch(`/api/rules?id=${id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            fetchAutoRules();
        }
    } catch (e) {
        console.error("Rule deletion failed:", e);
    }
}

async function testAutoRule() {
    const pattern = document.getElementById("rule-pattern").value.trim();
    const tag = document.getElementById("rule-tag").value.trim();
    if (!pattern) {
        alert("Please specify a regex pattern first.");
        return;
    }
    
    try {
        const response = await fetch("/api/rules/test-preview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pattern, tag: tag || "preview" })
        });
        const result = await response.json();
        if (response.ok) {
            if (result.matches.length === 0) {
                alert("0 documents match this pattern rule.");
            } else {
                const list = result.matches.map(m => `• ${m.filename}`).join("\n");
                alert(`The following ${result.matches.length} document(s) will match and receive the tag:\n\n${list}`);
            }
        } else {
            alert(`Simulation Error: ${result.detail}`);
        }
    } catch (e) {
        alert("Network connection failed.");
    }
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
        params.push(`mode=${searchMode}`);
        
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

        const scoreBadge = file.score !== undefined ? `
        <div style="display: inline-flex; align-items: center; gap: 0.35rem; vertical-align: middle; margin-left: 0.5rem;">
            <svg width="18" height="18" viewBox="0 0 36 36" style="transform: rotate(-90deg); filter: drop-shadow(0 0 2px rgba(16,185,129,0.3));">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="4.5" />
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#10b981" stroke-dasharray="${file.score}, 100" stroke-width="4.5" stroke-linecap="round" />
            </svg>
            <span class="badge" style="background: rgba(16, 185, 129, 0.12); border-color: rgba(16, 185, 129, 0.4); color: var(--success); font-size:0.65rem; padding: 0 0.35rem;">${file.score}% Match</span>
        </div>` : '';
        const snippetHtml = file.snippet ? `<div class="result-snippet">${file.snippet}</div>` : '';

        div.innerHTML = `
            <div class="result-info-header">
                <div class="result-info">
                    <span class="result-title">${file.filename} ${scoreBadge}</span>
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
        
        // Reset inline editor UI
        isEditingFile = false;
        document.getElementById("inline-text-editor").classList.add("hidden");
        document.getElementById("preview-code").parentElement.classList.remove("hidden");
        document.getElementById("edit-toggle-btn").innerText = "📝 Edit File";

        // Show/hide audio card and player
        const audioCard = document.getElementById("preview-audio-card");
        const audioPlayer = document.getElementById("audio-preview-player");
        if (data.audio_metadata) {
            audioCard.classList.remove("hidden");
            document.getElementById("audio-duration").innerText = data.audio_metadata.duration + "s";
            document.getElementById("audio-samplerate").innerText = data.audio_metadata.samplerate + " Hz";
            document.getElementById("audio-channels").innerText = data.audio_metadata.channels;
            document.getElementById("audio-bitrate").innerText = data.audio_metadata.bitrate;
            audioPlayer.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
        } else {
            audioCard.classList.add("hidden");
            audioPlayer.src = "";
        }

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
        
        // Ensure overlay element exists or recreate it
        let overlay = document.getElementById("ocr-highlights-container");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "ocr-highlights-container";
            overlay.className = "ocr-highlights-container";
            overlay.style.position = "absolute";
            overlay.style.top = "0";
            overlay.style.left = "0";
            overlay.style.width = "100%";
            overlay.style.height = "100%";
            overlay.style.pointerEvents = "none";
            overlay.style.zIndex = "5";
            previewArea.appendChild(overlay);
        }
        overlay.innerHTML = "";

        const suffix = data.filename.split('.').pop().toLowerCase();
        
        if (suffix === 'csv' && data.content) {
            previewArea.appendChild(overlay); // keep overlay active but empty
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
            previewArea.appendChild(overlay);
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
        } else if (['png', 'jpg', 'jpeg', 'bmp'].includes(suffix)) {
            // Render local image directly
            const img = document.createElement("img");
            // API path fallback
            img.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
            img.style.maxWidth = "100%";
            img.style.display = "block";
            img.style.position = "relative";
            
            previewArea.appendChild(overlay);
            previewArea.appendChild(img);
            
            // Render bounding boxes
            if (data.coords && data.coords.length > 0) {
                data.coords.forEach(box => {
                    const highlight = document.createElement("div");
                    highlight.className = "ocr-bounding-highlight";
                    highlight.style.left = `${box.x}px`;
                    highlight.style.top = `${box.y}px`;
                    highlight.style.width = `${box.w}px`;
                    highlight.style.height = `${box.h}px`;
                    highlight.title = box.word;
                    overlay.appendChild(highlight);
                });
            }
        } else if (data.content) {
            previewArea.appendChild(overlay);
            const pre = document.createElement("pre");
            pre.innerHTML = `<code id="preview-code">${data.content}</code>`;
            previewArea.appendChild(pre);
        } else {
            previewArea.appendChild(overlay);
            const div = document.createElement("div");
            div.style.padding = "1rem";
            div.style.color = "var(--text-secondary)";
            div.innerText = "[Binary File - Preview Not Available]";
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

async function triggerIndexing() {
    const dirInput = document.getElementById("dir-input");
    const directory = dirInput.value.trim();
    if (!directory) {
        alert("Please enter a valid directory path");
        return;
    }
    
    const progressCard = document.getElementById("progress-bar-card");
    const progressFile = document.getElementById("progress-bar-file");
    const progressPct = document.getElementById("progress-bar-pct");
    const progressInner = document.getElementById("progress-inner");
    
    progressCard.classList.remove("hidden");
    progressFile.innerText = "Connecting to indexer pipeline...";
    progressPct.innerText = "0%";
    progressInner.style.width = "0%";
    
    // Connect to Server Sent Events
    const eventSource = new EventSource("/api/index/events");
    
    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.done) {
                progressFile.innerText = "Indexing completed!";
                progressPct.innerText = "100%";
                progressInner.style.width = "100%";
                setTimeout(() => progressCard.classList.add("hidden"), 3000);
                eventSource.close();
                fetchStats();
                fetchGlobalTags();
                fetchDirectoryTree();
                triggerSearch();
            } else if (data.error) {
                progressFile.innerText = `Error: ${data.error}`;
                eventSource.close();
            } else {
                progressFile.innerText = `Indexing: ${data.filename} (${data.current}/${data.total})`;
                progressPct.innerText = `${data.pct}%`;
                progressInner.style.width = `${data.pct}%`;
            }
        } catch (e) {
            console.error("Failed to parse SSE", e);
        }
    };
    
    eventSource.onerror = () => {
        progressFile.innerText = "Connection lost. Checking status...";
        eventSource.close();
    };
    
    try {
        await fetch("/api/index", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ directory })
        });
    } catch (e) {
        console.error("Index post failed", e);
    }
}

/* Snapshots Vault Actions */
async function fetchSnapshots() {
    try {
        const response = await fetch("/api/snapshots");
        const data = await response.json();
        renderSnapshots(data.snapshots);
    } catch (e) {
        console.error("Failed to load snapshots", e);
    }
}

function renderSnapshots(snapshots) {
    const container = document.getElementById("sidebar-snapshots");
    container.innerHTML = "";
    if (!snapshots || snapshots.length === 0) {
        container.innerHTML = '<span class="rules-empty">No snapshots captured.</span>';
        return;
    }
    snapshots.forEach(ts => {
        const dateStr = new Date(ts * 1000).toLocaleString();
        const div = document.createElement("div");
        div.className = "rule-item";
        div.innerHTML = `
            <span><strong>Snapshot</strong><br/><small style="font-size:0.7rem; color:var(--text-secondary)">${dateStr}</small></span>
            <div>
                <button class="peer-sync-btn" onclick="restoreSnapshot(${ts})" style="background: rgba(99, 102, 241, 0.15); border-color: var(--accent); color: var(--accent);">Rollback</button>
                <button class="rule-del-btn" onclick="deleteSnapshot(${ts})">✕</button>
            </div>
        `;
        container.appendChild(div);
    });
}

async function createSnapshot() {
    try {
        const response = await fetch("/api/snapshots", { method: "POST" });
        if (response.ok) {
            alert("Snapshot successfully captured!");
            fetchSnapshots();
        }
    } catch (e) {
        console.error("Snapshot capture failed", e);
    }
}

async function restoreSnapshot(timestamp) {
    const confirmed = confirm("Are you sure you want to restore this snapshot? All current databases data will rollback to this point.");
    if (!confirmed) return;
    try {
        const response = await fetch(`/api/snapshots/restore?timestamp=${timestamp}`, { method: "POST" });
        if (response.ok) {
            alert("Database rollback successful!");
            fetchStats();
            fetchGlobalTags();
            fetchDirectoryTree();
            triggerSearch();
        }
    } catch (e) {
        console.error("Restore failed", e);
    }
}

function exportPdfReport() {
    const template = document.getElementById("pdf-template-select").value;
    const includeNotes = document.getElementById("pdf-include-notes-checkbox").checked;
    const params = [`style_template=${template}`, `include_notes=${includeNotes}`];
    if (selectedTag) params.push(`tag=${encodeURIComponent(selectedTag)}`);
    if (selectedCategory && selectedCategory !== "all") params.push(`category=${encodeURIComponent(selectedCategory)}`);
    
    let url = "/api/report/export";
    if (params.length > 0) {
        url += "?" + params.join("&");
    }
    window.open(url, "_blank");
}

function exportStatsCsv() {
    window.open("/api/stats/export", "_blank");
}

let mediaRecorder = null;
let recordedChunks = [];
let recordSecs = 0;
let recordInterval = null;

async function toggleAudioRecording() {
    // ponytail: capture microphone audio recording and upload to ACTIVE_DIR via MediaRecorder API
    const btn = document.getElementById("record-memo-btn");
    const lbl = document.getElementById("recorder-time-lbl");
    
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        btn.innerText = "● Record Voice Memo";
        btn.style.background = "var(--danger)";
        clearInterval(recordInterval);
        return;
    }
    
    recordedChunks = [];
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                recordedChunks.push(e.data);
            }
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
            const formData = new FormData();
            const timestamp = Date.now();
            formData.append("file", audioBlob, `voice-memo-${timestamp}.wav`);
            
            lbl.innerText = "Processing & Indexing...";
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    lbl.innerText = "Saved successfully!";
                    fetchStats();
                    fetchDirectoryTree();
                    triggerSearch();
                } else {
                    lbl.innerText = "Failed to upload.";
                }
            } catch (err) {
                lbl.innerText = "Error uploading memo.";
            }
            setTimeout(() => {
                lbl.innerText = "00:00 (Ready)";
            }, 3000);
            
            // Stop tracks
            stream.getTracks().forEach(t => t.stop());
        };
        
        mediaRecorder.start();
        btn.innerText = "■ Stop Recording";
        btn.style.background = "#3b82f6";
        
        recordSecs = 0;
        lbl.innerText = "00:00 (Recording...)";
        recordInterval = setInterval(() => {
            recordSecs++;
            const mins = String(Math.floor(recordSecs / 60)).padStart(2, '0');
            const secs = String(recordSecs % 60).padStart(2, '0');
            lbl.innerText = `${mins}:${secs} (Recording...)`;
        }, 1000);
        
    } catch (e) {
        alert("Failed to access microphone. Please check permissions.");
    }
}

async function deleteSnapshot(timestamp) {
    try {
        const response = await fetch(`/api/snapshots?timestamp=${timestamp}`, { method: "DELETE" });
        if (response.ok) {
            fetchSnapshots();
        }
    } catch (e) {
        console.error("Delete snapshot failed", e);
    }
}

/* Inline File Edit Actions */
function toggleInlineEdit() {
    if (!currentPreviewPath) return;
    const btn = document.getElementById("edit-toggle-btn");
    const editor = document.getElementById("inline-text-editor");
    const codePre = document.getElementById("preview-code").parentElement;
    
    if (!isEditingFile) {
        // Fetch raw file text to populate
        const codeElement = document.getElementById("preview-code");
        editor.value = codeElement.innerText;
        
        codePre.classList.add("hidden");
        editor.classList.remove("hidden");
        btn.innerText = "💾 Save Changes";
        isEditingFile = true;
    } else {
        saveInlineEdit(editor.value);
    }
}

async function saveInlineEdit(content) {
    const btn = document.getElementById("edit-toggle-btn");
    const editor = document.getElementById("inline-text-editor");
    const codePre = document.getElementById("preview-code").parentElement;
    
    btn.innerText = "Saving...";
    try {
        const response = await fetch("/api/file/edit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filepath: currentPreviewPath, content })
        });
        if (response.ok) {
            alert("File changes saved successfully!");
            isEditingFile = false;
            editor.classList.add("hidden");
            codePre.classList.remove("hidden");
            btn.innerText = "📝 Edit File";
            showPreview(currentPreviewPath);
            fetchStats();
            triggerSearch();
        } else {
            alert("Failed to save changes.");
            btn.innerText = "💾 Save Changes";
        }
    } catch (e) {
        console.error("Edit request failed", e);
        btn.innerText = "💾 Save Changes";
    }
}

/* Physics-based 2D force-directed concept graph rendering */
let graphAnimFrame;
async function loadConceptGraph() {
    try {
        const response = await fetch("/api/graph");
        const data = await response.json();
        drawGraph(data.nodes, data.links);
    } catch (e) {
        console.error("Failed to load graph", e);
    }
}

function drawGraph(nodes, links) {
    const canvas = document.getElementById("concept-graph-canvas");
    const ctx = canvas.getContext("2d");
    
    cancelAnimationFrame(graphAnimFrame);
    
    // Track selected node inside graph visualization context
    let selectedNodeId = null;
    
    // Assign random initial positions
    nodes.forEach(n => {
        n.x = Math.random() * canvas.width;
        n.y = Math.random() * canvas.height;
        n.vx = 0;
        n.vy = 0;
    });
    
    let draggedNode = null;
    let zoomScale = 1.0;
    let offsetX = 0;
    let offsetY = 0;
    let isPanning = false;
    let panStartX = 0;
    let panStartY = 0;
    
    // ponytail: interactive mouse gesture handlers to support drag and drop nodes and background viewport pan/zoom
    canvas.onmousedown = (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        
        // Transform screen coords to canvas coords depending on zoom/pan offsets
        const gx = (mx - offsetX) / zoomScale;
        const gy = (my - offsetY) / zoomScale;
        
        let nearestNode = null;
        let minDist = 25;
        
        nodes.forEach(n => {
            const dist = Math.sqrt((n.x - gx) * (n.x - gx) + (n.y - gy) * (n.y - gy));
            if (dist < minDist) {
                minDist = dist;
                nearestNode = n;
            }
        });
        
        if (nearestNode) {
            draggedNode = nearestNode;
            selectedNodeId = nearestNode.id;
            
            fetch(`/api/tree`).then(r => r.json()).then(data => {
                const found = data.files.find(f => f.filename === nearestNode.label);
                if (found) {
                    showPreview(found.filepath);
                }
            });
        } else {
            selectedNodeId = null;
            isPanning = true;
            panStartX = mx - offsetX;
            panStartY = my - offsetY;
        }
    };

    canvas.onmousemove = (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        if (draggedNode) {
            draggedNode.x = (mx - offsetX) / zoomScale;
            draggedNode.y = (my - offsetY) / zoomScale;
            draggedNode.vx = 0;
            draggedNode.vy = 0;
        } else if (isPanning) {
            offsetX = mx - panStartX;
            offsetY = my - panStartY;
        }
    };

    canvas.onmouseup = () => {
        draggedNode = null;
        isPanning = false;
    };

    canvas.onmouseleave = () => {
        draggedNode = null;
        isPanning = false;
    };

    canvas.onwheel = (e) => {
        e.preventDefault();
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        
        const gx = (mx - offsetX) / zoomScale;
        const gy = (my - offsetY) / zoomScale;
        
        const zoomFactor = 1.1;
        if (e.deltaY < 0) {
            zoomScale *= zoomFactor;
        } else {
            zoomScale /= zoomFactor;
        }
        zoomScale = Math.max(0.2, Math.min(zoomScale, 5.0));
        
        // Recalculate panning offsets to zoom centered on cursor
        offsetX = mx - gx * zoomScale;
        offsetY = my - gy * zoomScale;
    };
    
    function updatePhysics() {
        // Centering forces focus selected node
        if (selectedNodeId) {
            const centerNode = nodes.find(n => n.id === selectedNodeId);
            if (centerNode) {
                // Focus in centered coordinates space
                const centerTargetX = (canvas.width / 2 - offsetX) / zoomScale;
                const centerTargetY = (canvas.height / 2 - offsetY) / zoomScale;
                const dx = centerTargetX - centerNode.x;
                const dy = centerTargetY - centerNode.y;
                centerNode.x += dx * 0.1;
                centerNode.y += dy * 0.1;
            }
        }

        // Repulsion between nodes
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[j].x - nodes[i].x;
                const dy = nodes[j].y - nodes[i].y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                if (dist < 150) {
                    const force = (150 - dist) * 0.05;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    nodes[i].vx -= fx;
                    nodes[i].vy -= fy;
                    nodes[j].vx += fx;
                    nodes[j].vy += fy;
                }
            }
        }
        
        // Attraction along links
        links.forEach(l => {
            const sourceNode = nodes.find(n => n.id === l.source);
            const targetNode = nodes.find(n => n.id === l.target);
            if (sourceNode && targetNode) {
                const dx = targetNode.x - sourceNode.x;
                const dy = targetNode.y - sourceNode.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const force = (dist - 100) * 0.03 * (l.weight || 1);
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                sourceNode.vx += fx;
                sourceNode.vy += fy;
                targetNode.vx -= fx;
                targetNode.vy -= fy;
            }
        });
        
        // Apply friction and bounds boundary
        nodes.forEach(n => {
            n.x += n.vx;
            n.y += n.vy;
            n.vx *= 0.85;
            n.vy *= 0.85;
            
            // Constrain inside boundaries
            if (n.x < 20) n.x = 20;
            if (n.x > canvas.width - 20) n.x = canvas.width - 20;
            if (n.y < 20) n.y = 20;
            if (n.y > canvas.height - 20) n.y = canvas.height - 20;
        });
    }
    
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(offsetX, offsetY);
        ctx.scale(zoomScale, zoomScale);
        
        // ponytail: automatic category clustering hull backgrounds calculations
        const groups = {
            code: { nodes: [], color: "rgba(99, 102, 241, 0.06)", border: "rgba(99, 102, 241, 0.15)" },
            spreadsheets: { nodes: [], color: "rgba(16, 185, 129, 0.06)", border: "rgba(16, 185, 129, 0.15)" },
            images: { nodes: [], color: "rgba(239, 68, 68, 0.06)", border: "rgba(239, 68, 68, 0.15)" },
            documents: { nodes: [], color: "rgba(245, 158, 11, 0.06)", border: "rgba(245, 158, 11, 0.15)" }
        };
        
        nodes.forEach(n => {
            if (n.filename) {
                const ext = n.filename.split('.').pop().toLowerCase();
                if (['py', 'js', 'html', 'css', 'json', 'xml'].includes(ext)) {
                    groups.code.nodes.push(n);
                } else if (['xlsx', 'csv'].includes(ext)) {
                    groups.spreadsheets.nodes.push(n);
                } else if (['png', 'jpg', 'jpeg', 'bmp'].includes(ext)) {
                    groups.images.nodes.push(n);
                } else {
                    groups.documents.nodes.push(n);
                }
            }
        });
        
        for (const key in groups) {
            const grp = groups[key];
            if (grp.nodes.length >= 2) {
                let sumX = 0, sumY = 0;
                grp.nodes.forEach(n => { sumX += n.x; sumY += n.y; });
                const cx = sumX / grp.nodes.length;
                const cy = sumY / grp.nodes.length;
                
                let maxD = 0;
                grp.nodes.forEach(n => {
                    const d = Math.sqrt((n.x - cx) * (n.x - cx) + (n.y - cy) * (n.y - cy));
                    if (d > maxD) maxD = d;
                });
                
                ctx.fillStyle = grp.color;
                ctx.strokeStyle = grp.border;
                ctx.lineWidth = 1.0;
                ctx.beginPath();
                ctx.arc(cx, cy, maxD + 25, 0, 2 * Math.PI);
                ctx.fill();
                ctx.stroke();
            }
        }
        
        // Draw Links
        links.forEach(l => {
            const s = nodes.find(n => n.id === l.source);
            const t = nodes.find(n => n.id === l.target);
            if (s && t) {
                // Dim links that aren't connected to the selected node
                if (selectedNodeId && l.source !== selectedNodeId && l.target !== selectedNodeId) {
                    ctx.strokeStyle = "rgba(63, 63, 70, 0.08)";
                } else {
                    ctx.strokeStyle = "rgba(99, 102, 241, 0.4)";
                }
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(s.x, s.y);
                ctx.lineTo(t.x, t.y);
                ctx.stroke();
            }
        });
        
        // Draw Nodes
        nodes.forEach(n => {
            let color = "var(--accent)"; // Default
            if (n.filename) {
                const ext = n.filename.split('.').pop().toLowerCase();
                if (['py', 'js', 'html', 'css', 'json', 'xml'].includes(ext)) {
                    color = "#6366f1"; // Code: Purple/Indigo Accent
                } else if (['xlsx', 'csv'].includes(ext)) {
                    color = "#10b981"; // Spreadsheets: Green Success
                } else if (['png', 'jpg', 'jpeg', 'bmp'].includes(ext)) {
                    color = "#ef4444"; // Images: Red Danger
                } else if (['pdf', 'docx', 'rtf', 'txt', 'md'].includes(ext)) {
                    color = "#f59e0b"; // Documents: Amber Yellow
                }
            }
            
            // Dim nodes that aren't direct neighbors of selected node
            let isConnected = (n.id === selectedNodeId);
            if (selectedNodeId && !isConnected) {
                isConnected = links.some(l => 
                    (l.source === selectedNodeId && l.target === n.id) || 
                    (l.target === selectedNodeId && l.source === n.id)
                );
            }
            
            ctx.fillStyle = color;
            ctx.globalAlpha = (selectedNodeId && !isConnected) ? 0.2 : 1.0;
            
            ctx.beginPath();
            // Highlight selected node with a larger radius
            const radius = (n.id === selectedNodeId) ? 12 : 8;
            ctx.arc(n.x, n.y, radius, 0, 2 * Math.PI);
            ctx.fill();
            
            // Label
            ctx.fillStyle = "var(--text-primary)";
            ctx.font = (n.id === selectedNodeId) ? "bold 11px Inter" : "10px Inter";
            ctx.fillText(n.label, n.x + (radius + 4), n.y + 4);
        });
        ctx.globalAlpha = 1.0;
        
        ctx.restore();
        
        updatePhysics();
        graphAnimFrame = requestAnimationFrame(draw);
    }
    
    draw();
}

