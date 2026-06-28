let activeTab = "workspace";

function switchTab(tabId) {
    activeTab = tabId;
    localStorage.setItem("active-tab", tabId);
    
    // Update active visual styles of horizontal tabs
    document.querySelectorAll(".tab-link").forEach(btn => {
        btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
    });
    
    // Update tab visibility
    document.querySelectorAll(".tab-view-content").forEach(view => {
        view.classList.toggle("hidden", view.id !== `${tabId}-tab-view`);
    });
    
    // Lazy-update/Fetch stats for the active view to avoid heavy multi-network loads
    if (tabId === "workspace") {
        fetchStats();
        fetchDirectoryTree();
    } else if (tabId === "search") {
        fetchGlobalTags();
        triggerSearch();
        if (typeof selectedCategory !== "undefined" && selectedCategory === "graph") {
            loadConceptGraph();
        }
    } else if (tabId === "config") {
        fetchAutoRules();
        fetchMacrosList();
        fetchSearchHistory();
        fetchSearchBookmarks();
        fetchPeers();
        fetchSnapshots();
    } else if (tabId === "chat") {
        // No specific data load required for chat, or handle welcome message
    }
}

function toggleAccordion(groupId) {
    const groupEl = document.getElementById(groupId);
    if (!groupEl) return;
    const trigger = groupEl.previousElementSibling;
    const arrow = trigger.querySelector(".accordion-arrow");
    
    const isOpen = groupEl.classList.toggle("open");
    trigger.classList.toggle("active", isOpen);
    
    if (arrow) {
        arrow.innerText = isOpen ? "▾" : "▸";
    }
}

let searchTimeout;
let selectedCategory = "all";
let selectedTag = null;
let currentPreviewPath = null;
let searchMode = "keyword"; // "keyword" or "semantic"

let isEditingFile = false;

let folderScopePath = null;

document.addEventListener("DOMContentLoaded", () => {
    // Restore theme preference
    if (localStorage.getItem("app-theme") === "light") {
        document.body.classList.add("light-theme");
    }
    fetchStats();
    fetchGlobalTags();
    fetchDirectoryTree();
    fetchAutoRules();
    fetchPeers();
    fetchSnapshots();
    setupDropZone();
    fetchMacrosList();
    fetchSearchHistory();
    fetchSearchBookmarks();
    
    // ponytail: register search autosuggest events
    const searchInput = document.getElementById("search-input");
    const dropdown = document.getElementById("search-autocomplete-dropdown");
    let activeSuggestionIdx = -1;
    
    if (searchInput && dropdown) {
        searchInput.addEventListener("input", async (e) => {
            const val = e.target.value;
            const words = val.split(/\s+/);
            const currentToken = words[words.length - 1];
            
            if (currentToken.length > 0) {
                try {
                    const res = await fetch(`/api/search/suggest?token=${encodeURIComponent(currentToken)}`);
                    const data = await res.json();
                    if (data.suggestions && data.suggestions.length > 0) {
                        dropdown.classList.remove("hidden");
                        dropdown.innerHTML = "";
                        activeSuggestionIdx = -1;
                        
                        data.suggestions.forEach((item, idx) => {
                            const itemEl = document.createElement("div");
                            itemEl.className = "autocomplete-item";
                            itemEl.dataset.index = idx;
                            itemEl.innerHTML = `
                                <span>${item.text}</span>
                                <span class="autocomplete-type">${item.type}</span>
                            `;
                            
                            itemEl.onclick = () => {
                                words[words.length - 1] = item.text;
                                searchInput.value = words.join(" ") + " ";
                                dropdown.classList.add("hidden");
                                triggerSearch();
                            };
                            dropdown.appendChild(itemEl);
                        });
                    } else {
                        dropdown.classList.add("hidden");
                    }
                } catch (err) {
                    console.error("Suggestion fetch failed", err);
                }
            } else {
                dropdown.classList.add("hidden");
            }
        });
        
        searchInput.addEventListener("keydown", (e) => {
            const items = dropdown.querySelectorAll(".autocomplete-item");
            if (dropdown.classList.contains("hidden") || items.length === 0) return;
            
            if (e.key === "ArrowDown") {
                e.preventDefault();
                activeSuggestionIdx = (activeSuggestionIdx + 1) % items.length;
                updateActiveSuggestion(items);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                activeSuggestionIdx = (activeSuggestionIdx - 1 + items.length) % items.length;
                updateActiveSuggestion(items);
            } else if (e.key === "Enter") {
                if (activeSuggestionIdx >= 0) {
                    e.preventDefault();
                    items[activeSuggestionIdx].click();
                }
            } else if (e.key === "Escape") {
                dropdown.classList.add("hidden");
            }
        });
        
        document.addEventListener("click", (e) => {
            if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add("hidden");
            }
        });
    }
    
    function updateActiveSuggestion(items) {
        items.forEach(el => el.classList.remove("active"));
        if (activeSuggestionIdx >= 0 && activeSuggestionIdx < items.length) {
            items[activeSuggestionIdx].classList.add("active");
            items[activeSuggestionIdx].scrollIntoView({ block: "nearest" });
        }
    }
    
    // Initialize or restore active tab state
    const savedTab = localStorage.getItem("active-tab") || "workspace";
    switchTab(savedTab);
});

function toggleAppTheme() {
    document.body.classList.toggle("light-theme");
    const mode = document.body.classList.contains("light-theme") ? "light" : "dark";
    localStorage.setItem("app-theme", mode);
}

async function fetchMacrosList() {
    try {
        const response = await fetch("/api/macros");
        const data = await response.json();
        const select = document.getElementById("macro-select");
        select.innerHTML = '<option value="">-- Apply Macro --</option>';
        
        const sidebarContainer = document.getElementById("sidebar-macros");
        if (sidebarContainer) {
            sidebarContainer.innerHTML = "";
        }
        
        if (data.macros && data.macros.length > 0) {
            data.macros.forEach(m => {
                const opt = document.createElement("option");
                opt.value = m.expansion;
                opt.innerText = `%${m.name}% (${m.expansion})`;
                select.appendChild(opt);
                
                if (sidebarContainer) {
                    const row = document.createElement("div");
                    row.className = "rule-item";
                    row.innerHTML = `
                        <span title="${m.expansion}"><strong>%${m.name}%</strong>: ${m.expansion}</span>
                        <button class="rule-del-btn" onclick="deleteQueryMacro('${m.name}')">✕</button>
                    `;
                    sidebarContainer.appendChild(row);
                }
            });
        } else {
            if (sidebarContainer) {
                sidebarContainer.innerHTML = '<span class="rules-empty">No macros configured.</span>';
            }
        }
    } catch (e) {
        console.error("Failed to fetch macros", e);
    }
}

async function addQueryMacroAction() {
    const nameInput = document.getElementById("macro-name-input");
    const expInput = document.getElementById("macro-expansion-input");
    const name = nameInput.value.trim();
    const expansion = expInput.value.trim();
    if (!name || !expansion) return;
    
    try {
        const res = await fetch("/api/macros", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, expansion })
        });
        if (res.ok) {
            nameInput.value = "";
            expInput.value = "";
            fetchMacrosList();
        }
    } catch (e) {
        console.error("Failed to add macro", e);
    }
}

async function deleteQueryMacro(name) {
    try {
        const res = await fetch(`/api/macros?name=${encodeURIComponent(name)}`, {
            method: "DELETE"
        });
        if (res.ok) {
            fetchMacrosList();
        }
    } catch (e) {
        console.error("Failed to delete macro", e);
    }
}


function applyQueryMacro() {
    const val = document.getElementById("macro-select").value;
    if (val) {
        const searchInput = document.getElementById("search-input");
        searchInput.value = val;
        triggerSearch();
    }
}

function setFolderScopeFilter(path) {
    folderScopePath = path;
    document.getElementById("active-scoped-path-lbl").innerText = path;
    document.getElementById("active-path-filter-card").classList.remove("hidden");
    triggerSearch();
}

function clearFolderScopeFilter() {
    folderScopePath = null;
    document.getElementById("active-path-filter-card").classList.add("hidden");
    triggerSearch();
}

async function fetchStats() {
    try {
        const response = await fetch("/api/stats");
        const data = await response.json();
        
        document.getElementById("stat-files").innerText = data.total_files;
        document.getElementById("stat-size").innerText = formatBytes(data.total_size);
        
        if (data.disk_storage) {
            const freeStr = formatBytes(data.disk_storage.free_bytes);
            document.getElementById("stat-disk-free").innerText = `${freeStr} (${data.disk_storage.free_percent}% free)`;
        }
        
        if (data.active_directory) {
            document.getElementById("active-dir-label").innerText = getBasename(data.active_directory);
            document.getElementById("active-dir-label").title = data.active_directory;
        }

        // ponytail: fetch query cache statistics
        try {
            const cacheRes = await fetch("/api/search/cache/stats");
            const cacheStats = await cacheRes.json();
            const cacheRatioEl = document.getElementById("stat-cache-ratio");
            if (cacheRatioEl && cacheStats) {
                cacheRatioEl.innerText = `${cacheStats.hit_ratio}% (${cacheStats.hits} hits / ${cacheStats.misses} misses)`;
            }
        } catch (cacheErr) {
            console.error("Failed to load cache stats", cacheErr);
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
            if (activeTab !== "search") {
                switchTab("search");
            }
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

async function getFilesFromDroppedItems(items) {
    const fileList = [];
    const traverse = async (entry) => {
        if (entry.isFile) {
            const file = await new Promise((resolve) => entry.file(resolve));
            const relPath = entry.fullPath.startsWith('/') ? entry.fullPath.substring(1) : entry.fullPath;
            fileList.push({ file, relativePath: relPath });
        } else if (entry.isDirectory) {
            const reader = entry.createReader();
            // Read all entries in directory
            const readAllEntries = async () => {
                let allEntries = [];
                while (true) {
                    const entries = await new Promise((resolve) => reader.readEntries(resolve));
                    if (entries.length === 0) break;
                    allEntries = allEntries.concat(entries);
                }
                return allEntries;
            };
            const entries = await readAllEntries();
            for (const child of entries) {
                await traverse(child);
            }
        }
    };
    for (let i = 0; i < items.length; i++) {
        if (items[i].kind === 'file') {
            const entry = items[i].webkitGetAsEntry();
            if (entry) {
                await traverse(entry);
            }
        }
    }
    return fileList;
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
    
    dropZone.addEventListener('drop', async e => {
        let fileList = [];
        if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
            fileList = await getFilesFromDroppedItems(e.dataTransfer.items);
        } else {
            const files = e.dataTransfer.files;
            for (let i = 0; i < files.length; i++) {
                fileList.push({ file: files[i], relativePath: files[i].name });
            }
        }
        handleFilesUpload(fileList);
    }, false);

    dropZone.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.onchange = e => {
            const fileList = [];
            const files = e.target.files;
            for (let i = 0; i < files.length; i++) {
                fileList.push({ file: files[i], relativePath: files[i].name });
            }
            handleFilesUpload(fileList);
        };
        input.click();
    });
}

async function handleFilesUpload(fileList) {
    const statusMsg = document.getElementById("indexing-status");
    if (!fileList || fileList.length === 0) return;

    statusMsg.innerText = `Uploading ${fileList.length} file(s)...`;
    
    let uploadedCount = 0;
    const uploadSingle = async ({ file, relativePath }) => {
        const formData = new FormData();
        formData.append('file', file, relativePath);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                uploadedCount++;
                statusMsg.innerText = `Uploading... ${uploadedCount}/${fileList.length} completed.`;
                console.log(`Uploaded & Indexed: ${relativePath}`);
            }
        } catch (error) {
            console.error(`Failed to upload ${relativePath}`, error);
        }
    };

    // Concurrency pool with limit = 5
    const concurrency = 5;
    let nextIndex = 0;
    const worker = async () => {
        while (nextIndex < fileList.length) {
            const index = nextIndex++;
            await uploadSingle(fileList[index]);
        }
    };
    
    const workers = [];
    for (let i = 0; i < Math.min(concurrency, fileList.length); i++) {
        workers.push(worker());
    }
    await Promise.all(workers);
    
    statusMsg.innerText = "Indexing completed successfully.";
    fetchStats();
    fetchGlobalTags();
    fetchDirectoryTree();
    triggerSearch();
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

    let pathAccumulator = "";
    const root = {};
    files.forEach(f => {
        const parts = f.filepath.split(/[\\/]/);
        let current = root;
        parts.forEach((part, i) => {
            if (!current[part]) {
                current[part] = (i === parts.length - 1) ? { _file: f } : { _path: f.filepath.split(part)[0] + part };
            }
            current = current[part];
        });
    });

    function renderNode(node, name, parentEl) {
        if (node._file) {
            const div = document.createElement("div");
            div.className = "tree-file-title";
            const ext = name.split('.').pop().toLowerCase();
            div.setAttribute("data-ext", ext);
            div.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; vertical-align: middle; color: var(--accent);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                <span>${name}</span>
            `;
            div.onclick = () => selectWorkspaceFile(node._file.filepath);
            parentEl.appendChild(div);
        } else {
            const folderDiv = document.createElement("div");
            folderDiv.className = "tree-folder";
            
            const title = document.createElement("div");
            title.className = "tree-folder-title";
            
            const folderClosedSVG = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; vertical-align: middle; color: var(--accent);"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`;
            const folderOpenSVG = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; vertical-align: middle; color: var(--accent);"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>`;
            
            title.innerHTML = `${folderClosedSVG} <span>${name}</span>`;
            
            const content = document.createElement("div");
            content.style.display = "none";
            
            // Single-click expands, double-click sets folder filter scope
            title.onclick = (e) => {
                if (e.detail === 1) {
                    setTimeout(() => {
                        if (title.getAttribute("data-double-clicked") !== "true") {
                            const isCollapsed = content.style.display === "none";
                            content.style.display = isCollapsed ? "block" : "none";
                            title.innerHTML = isCollapsed ? `${folderOpenSVG} <span>${name}</span>` : `${folderClosedSVG} <span>${name}</span>`;
                        }
                        title.removeAttribute("data-double-clicked");
                    }, 200);
                }
            };
            
            title.ondblclick = () => {
                title.setAttribute("data-double-clicked", "true");
                setFolderScopeFilter(node._path || name);
            };
            
            folderDiv.appendChild(title);
            folderDiv.appendChild(content);
            parentEl.appendChild(folderDiv);
            
            for (const key in node) {
                if (key !== "_path") {
                    renderNode(node[key], key, content);
                }
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
    if (activeTab !== "search") {
        switchTab("search");
    }
    if (!selectedTag) {
        selectedTag = tag;
    } else {
        const tags = selectedTag.split(",").map(t => t.trim()).filter(Boolean);
        if (tags.includes(tag)) {
            const filtered = tags.filter(t => t !== tag);
            selectedTag = filtered.length > 0 ? filtered.join(",") : null;
        } else {
            tags.push(tag);
            selectedTag = tags.join(",");
        }
    }
    
    const banner = document.getElementById("active-filters");
    const badge = document.getElementById("active-tag-badge");
    if (selectedTag) {
        badge.innerText = `Tags: ${selectedTag}`;
        banner.classList.remove("hidden");
    } else {
        banner.classList.add("hidden");
    }
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
    
    const sliderContainer = document.getElementById("similarity-threshold-container");
    if (sliderContainer) {
        sliderContainer.classList.toggle("hidden", mode !== "semantic");
    }
    
    triggerSearch();
}

function updateSimilarityThresholdDisplay(val) {
    const valDisplay = document.getElementById("similarity-threshold-val");
    if (valDisplay) {
        valDisplay.innerText = `${val}%`;
    }
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
            <span><strong>${rule.pattern}</strong> ➔ <span class="badge" style="font-size: 0.65rem; padding:0 0.3rem">${rule.tag}</span> <small style="color: var(--text-secondary);">(${rule.priority || 0})</small></span>
            <button class="rule-del-btn" onclick="deleteAutoRule(${rule.id})">✕</button>
        `;
        container.appendChild(div);
    });
}

async function addAutoRule() {
    const patInput = document.getElementById("rule-pattern");
    const tagInput = document.getElementById("rule-tag");
    const priorityInput = document.getElementById("rule-priority");
    const pattern = patInput.value.trim();
    const tag = tagInput.value.trim();
    const priority = parseInt(priorityInput.value || 0);
    if (!pattern || !tag) return;

    try {
        const response = await fetch("/api/rules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pattern, tag, priority })
        });
        if (response.ok) {
            patInput.value = "";
            tagInput.value = "";
            priorityInput.value = "0";
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

let globalTagColors = {};

async function fetchGlobalTags() {
    try {
        const response = await fetch("/api/tags");
        const data = await response.json();
        const container = document.getElementById("sidebar-tags");
        container.innerHTML = "";
        
        globalTagColors = {};
        if (data.tags.length === 0) {
            container.innerHTML = '<span class="tag-cloud-empty">No tags set yet.</span>';
            return;
        }

        data.tags.forEach(item => {
            if (item.color) {
                globalTagColors[item.tag] = item.color;
            }
            
            const span = document.createElement("span");
            span.className = "tag-pill-sidebar";
            span.innerText = `${item.tag} (${item.count})`;
            if (item.color) {
                span.style.background = item.color;
                span.style.borderColor = item.color;
            }
            
            // Inline double-click color picker configurator UI
            span.ondblclick = () => {
                const picker = document.getElementById("global-tag-color-picker");
                if (picker) {
                    picker.value = item.color || "#6366f1";
                    picker.onchange = () => {
                        setTagColor(item.tag, picker.value);
                    };
                    picker.click();
                }
            };
            
            span.onclick = (e) => {
                if (e.target === span) filterByTag(item.tag);
            };
            container.appendChild(span);
        });
        
        // Populate word frequency tag cloud widget
        const freqContainer = document.getElementById("word-freq-tag-cloud");
        if (freqContainer) {
            freqContainer.innerHTML = "";
            if (data.tags.length === 0) {
                freqContainer.innerHTML = '<span class="tag-cloud-empty" style="font-size: 0.8rem; color: var(--text-secondary);">No tag frequencies found.</span>';
            } else {
                const counts = data.tags.map(t => t.count);
                const minCount = Math.min(...counts);
                const maxCount = Math.max(...counts);
                const countRange = maxCount - minCount || 1;
                
                data.tags.forEach(item => {
                    const span = document.createElement("span");
                    span.className = "tag-pill-sidebar";
                    span.innerText = item.tag;
                    
                    // Linear scaling mapping counts range between 0.7rem and 1.8rem
                    const size = 0.7 + ((item.count - minCount) / countRange) * 1.1;
                    span.style.fontSize = `${size}rem`;
                    span.style.padding = `${size * 0.3}rem ${size * 0.6}rem`;
                    
                    if (item.color) {
                        span.style.background = item.color;
                        span.style.borderColor = item.color;
                    }
                    span.onclick = () => filterByTag(item.tag);
                    freqContainer.appendChild(span);
                });
            }
        }
    } catch (error) {
        console.error("Failed to fetch tags:", error);
    }
}

async function fetchSearchHistory() {
    try {
        const response = await fetch("/api/search/history");
        const data = await response.json();
        const container = document.getElementById("sidebar-search-history");
        if (!container) return;
        container.innerHTML = "";
        if (!data.history || data.history.length === 0) {
            container.innerHTML = '<span class="rules-empty">No search query history logged.</span>';
            return;
        }
        data.history.forEach(item => {
            const div = document.createElement("div");
            div.className = "rule-item";
            div.style.cursor = "pointer";
            div.style.padding = "0.25rem";
            div.style.borderRadius = "4px";
            div.style.transition = "background-color 0.2s";
            
            const cleanQuery = item.query_string ? item.query_string.replace(/"/g, '&quot;') : '';
            div.onclick = () => {
                const input = document.getElementById("search-input");
                input.value = item.query_string || "";
                setSearchMode(item.search_mode === "semantic" ? "semantic" : "keyword");
            };
            
            div.onmouseover = () => div.style.backgroundColor = "rgba(99, 102, 241, 0.15)";
            div.onmouseout = () => div.style.backgroundColor = "transparent";
            
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                    <span style="font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 180px;" title="${cleanQuery}">${item.query_string || 'All Files'}</span>
                    <span class="badge" style="font-size: 0.6rem; padding: 0 0.2rem; border-color: rgba(99, 102, 241, 0.4);">${item.search_mode} (${item.result_count})</span>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Failed to load search history", e);
    }
}

async function fetchSearchBookmarks() {
    try {
        const response = await fetch("/api/bookmarks");
        const data = await response.json();
        const container = document.getElementById("sidebar-search-bookmarks");
        if (!container) return;
        container.innerHTML = "";
        if (!data.bookmarks || data.bookmarks.length === 0) {
            container.innerHTML = '<span class="rules-empty">No bookmarks saved yet.</span>';
            return;
        }
        data.bookmarks.forEach(item => {
            const div = document.createElement("div");
            div.className = "rule-item";
            div.style.display = "flex";
            div.style.justifyContent = "space-between";
            div.style.alignItems = "center";
            div.style.padding = "0.25rem";
            div.style.borderRadius = "4px";
            div.style.transition = "background-color 0.2s";
            
            const cleanQuery = item.query_string ? item.query_string.replace(/"/g, '&quot;') : '';
            const nameSpan = document.createElement("span");
            nameSpan.style.cursor = "pointer";
            nameSpan.style.fontWeight = "500";
            nameSpan.style.textOverflow = "ellipsis";
            nameSpan.style.overflow = "hidden";
            nameSpan.style.whiteSpace = "nowrap";
            nameSpan.style.maxWidth = "160px";
            nameSpan.innerText = item.name;
            nameSpan.title = `Query: ${cleanQuery} (${item.search_mode})`;
            nameSpan.onclick = () => {
                const input = document.getElementById("search-input");
                input.value = item.query_string || "";
                setSearchMode(item.search_mode === "semantic" ? "semantic" : "keyword");
            };
            
            const rightContainer = document.createElement("div");
            rightContainer.style.display = "flex";
            rightContainer.style.alignItems = "center";
            rightContainer.style.gap = "0.25rem";
            
            const modeBadge = document.createElement("span");
            modeBadge.className = "badge";
            modeBadge.style.fontSize = "0.6rem";
            modeBadge.style.padding = "0 0.2rem";
            modeBadge.style.borderColor = "rgba(99, 102, 241, 0.4)";
            modeBadge.innerText = item.search_mode;
            
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "rule-del-btn";
            deleteBtn.style.margin = "0";
            deleteBtn.style.padding = "0 2px";
            deleteBtn.style.fontSize = "0.75rem";
            deleteBtn.style.background = "transparent";
            deleteBtn.style.border = "none";
            deleteBtn.style.color = "var(--danger)";
            deleteBtn.style.cursor = "pointer";
            deleteBtn.innerText = "✕";
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteSearchBookmark(item.id);
            };
            
            rightContainer.appendChild(modeBadge);
            rightContainer.appendChild(deleteBtn);
            
            div.appendChild(nameSpan);
            div.appendChild(rightContainer);
            
            div.onmouseover = () => div.style.backgroundColor = "rgba(99, 102, 241, 0.15)";
            div.onmouseout = () => div.style.backgroundColor = "transparent";
            
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Failed to load search bookmarks", e);
    }
}

async function addSearchBookmark() {
    const input = document.getElementById("search-input");
    const queryVal = input ? input.value.trim() : "";
    const bookmarkName = prompt("Enter a name for this bookmark:", queryVal || "My Bookmark");
    if (!bookmarkName) return;
    
    try {
        const response = await fetch("/api/bookmarks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: bookmarkName,
                query_string: queryVal,
                search_mode: searchMode
            })
        });
        if (response.ok) {
            fetchSearchBookmarks();
        } else {
            const err = await response.json();
            alert(`Failed to save bookmark: ${err.detail}`);
        }
    } catch (e) {
        console.error("Failed to save bookmark", e);
    }
}

async function deleteSearchBookmark(id) {
    try {
        const response = await fetch(`/api/bookmarks?id=${id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            fetchSearchBookmarks();
        }
    } catch (e) {
        console.error("Failed to delete bookmark", e);
    }
}

async function setTagColor(tag, color) {
    try {
        const response = await fetch("/api/tags/color", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tag, color })
        });
        if (response.ok) {
            fetchGlobalTags();
            triggerSearch();
        }
    } catch (e) {
        console.error("Failed to save tag color", e);
    }
}

function triggerSearch() {
    clearTimeout(searchTimeout);
    const query = document.getElementById("search-input").value.trim();

    if (activeTab !== "search") {
        switchTab("search");
        return;
    }

    searchTimeout = setTimeout(async () => {
        if (selectedCategory === "duplicates") {
            fetchDuplicates();
            return;
        }

        document.getElementById("results-title-header").innerText = "Matching Records";
        
        // ponytail: validate search query parameters in real-time
        try {
            const valRes = await fetch("/api/search/validate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });
            const valData = await valRes.json();
            const syntaxEl = document.getElementById("search-syntax-feedback");
            if (syntaxEl && valData) {
                if (query.length > 0) {
                    syntaxEl.classList.remove("hidden");
                    const statusEl = document.getElementById("syntax-status-lbl");
                    const descEl = document.getElementById("syntax-desc-lbl");
                    if (valData.valid) {
                        syntaxEl.style.backgroundColor = "rgba(16, 185, 129, 0.08)";
                        syntaxEl.style.borderColor = "var(--success)";
                        statusEl.style.color = "var(--success)";
                        statusEl.innerText = "Query Syntax Valid";
                        descEl.innerText = "Correct query syntax matches and filters configured.";
                    } else {
                        syntaxEl.style.backgroundColor = "rgba(239, 68, 68, 0.08)";
                        syntaxEl.style.borderColor = "var(--danger)";
                        statusEl.style.color = "var(--danger)";
                        statusEl.innerText = `Syntax Alert: ${valData.error}`;
                        descEl.innerText = valData.suggestion;
                    }
                } else {
                    syntaxEl.classList.add("hidden");
                }
            }
        } catch (valErr) {
            console.error("Syntax validation failed", valErr);
        }
        
        // Read sorting parameters
        const sortBy = document.getElementById("sort-by-select").value;
        const sortOrder = document.getElementById("sort-order-select").value;
        const dateFilter = document.getElementById("date-filter-select").value;

        // Custom Snippet Configurations
        const snippetLimit = document.getElementById("snippet-limit-input").value || 15;
        const snippetStart = document.getElementById("snippet-start-input").value || "<mark>";
        const snippetEnd = document.getElementById("snippet-end-input").value || "</mark>";

        let url = `/api/search?`;
        const params = [];
        if (query) params.push(`q=${encodeURIComponent(query)}`);
        if (selectedTag) params.push(`tag=${encodeURIComponent(selectedTag)}`);
        if (selectedCategory && selectedCategory !== "all") params.push(`category=${encodeURIComponent(selectedCategory)}`);
        
        params.push(`sort_by=${sortBy}`);
        params.push(`sort_order=${sortOrder}`);
        params.push(`date_filter=${dateFilter}`);
        params.push(`mode=${searchMode}`);
        params.push(`snippet_limit=${snippetLimit}`);
        params.push(`highlight_start=${encodeURIComponent(snippetStart)}`);
        params.push(`highlight_end=${encodeURIComponent(snippetEnd)}`);
        
        const thresholdSlider = document.getElementById("similarity-threshold-slider");
        const similarityThreshold = thresholdSlider ? thresholdSlider.value : 0;
        params.push(`similarity_threshold=${similarityThreshold}`);
        
        const tagModeSelect = document.getElementById("search-tag-mode-select");
        const tagMode = tagModeSelect ? tagModeSelect.value : "AND";
        params.push(`tag_mode=${tagMode}`);
        
        if (folderScopePath) params.push(`folder_path=${encodeURIComponent(folderScopePath)}`);
        
        url += params.join("&");

        try {
            const response = await fetch(url);
            const data = await response.json();
            
            // ponytail: update search metrics dashboard card
            const metricsPanel = document.getElementById("search-metrics-panel");
            if (metricsPanel) {
                if (data.search_time_ms !== undefined) {
                    metricsPanel.classList.remove("hidden");
                    document.getElementById("metric-mode").innerText = (data.mode || "Keyword").toUpperCase();
                    document.getElementById("metric-time").innerText = `${data.search_time_ms} ms`;
                    document.getElementById("metric-count").innerText = `${data.results ? data.results.length : 0} match(es)`;
                    
                    const synElement = document.getElementById("metric-synonyms");
                    if (data.synonyms_expanded && data.synonyms_expanded.length > 0) {
                        const synsText = data.synonyms_expanded.join("; ");
                        synElement.innerText = synsText;
                        synElement.title = synsText;
                        synElement.style.color = "var(--success)";
                    } else {
                        synElement.innerText = "None";
                        synElement.title = "";
                        synElement.style.color = "var(--text-secondary)";
                    }

                    // ponytail: render visual execution plan flow segments
                    const planFlowContainer = document.getElementById("metric-execution-plan-flow");
                    if (planFlowContainer) {
                        planFlowContainer.innerHTML = "";
                        if (data.execution_plan && data.execution_plan.length > 0) {
                            data.execution_plan.forEach((step, idx) => {
                                if (idx > 0) {
                                    const arrow = document.createElement("span");
                                    arrow.style.color = "var(--text-secondary)";
                                    arrow.innerText = "➔";
                                    planFlowContainer.appendChild(arrow);
                                }
                                const stepSpan = document.createElement("span");
                                stepSpan.style.background = "rgba(99, 102, 241, 0.12)";
                                stepSpan.style.border = "1px solid rgba(99, 102, 241, 0.3)";
                                stepSpan.style.borderRadius = "4px";
                                stepSpan.style.padding = "2px 6px";
                                stepSpan.style.color = "var(--text-primary)";
                                stepSpan.innerText = step;
                                planFlowContainer.appendChild(stepSpan);
                            });
                        } else {
                            planFlowContainer.innerText = "None";
                        }
                    }
                } else {
                    metricsPanel.classList.add("hidden");
                }
            }

            renderResults(data.results);
            fetchSearchHistory();
            
            // ponytail: refresh cache stats values
            try {
                const cacheRes = await fetch("/api/search/cache/stats");
                const cacheStats = await cacheRes.json();
                const cacheRatioEl = document.getElementById("stat-cache-ratio");
                if (cacheRatioEl && cacheStats) {
                    cacheRatioEl.innerText = `${cacheStats.hit_ratio}% (${cacheStats.hits} hits / ${cacheStats.misses} misses)`;
                }
            } catch (cacheErr) {}
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
    
    // ponytail: add neon shadow animation triggers to the search results count badge
    if (results.length > 0) {
        countBadge.classList.add("neon-count-glow");
    } else {
        countBadge.classList.remove("neon-count-glow");
    }

    if (results.length === 0) {
        list.innerHTML = '<div class="empty-state">No matches found. Try another query/filter.</div>';
        return;
    }

    const bulkBtn = document.getElementById("bulk-delete-btn");
    bulkBtn.classList.add("hidden");

    results.forEach(file => {
        const div = document.createElement("div");
        div.className = "result-item";
        
        // Prevent preview selection when clicking checkbox
        div.onclick = (e) => {
            if (e.target.closest('input[type="checkbox"]') || e.target.closest('.result-tag-pill')) {
                return;
            }
            showPreview(file.filepath);
        };
        
        let tagsHtml = "";
        if (file.tags && file.tags.length > 0) {
            tagsHtml = `<div class="result-tags">` + 
                file.tags.map(t => {
                    const col = globalTagColors[t];
                    const styleAttr = col ? `style="background: ${col}; border-color: ${col};"` : "";
                    return `<span class="result-tag-pill" ${styleAttr}>${t}</span>`;
                }).join("") + 
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
            <div class="result-info-header" style="align-items: center;">
                <input type="checkbox" class="bulk-select-chk" data-path="${encodeURIComponent(file.filepath)}" style="margin-right: 0.75rem; width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer;" />
                <div class="result-info" style="flex: 1;">
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
        
        // Listen to checkbox state changes to toggle bulk delete button
        const chk = div.querySelector(".bulk-select-chk");
        chk.addEventListener("change", () => {
            const anyChecked = [...document.querySelectorAll(".bulk-select-chk")].some(c => c.checked);
            if (anyChecked) {
                bulkBtn.classList.remove("hidden");
            } else {
                bulkBtn.classList.add("hidden");
            }
        });

        list.appendChild(div);
    });
}

async function triggerBulkDelete() {
    const checkedBoxes = [...document.querySelectorAll(".bulk-select-chk")].filter(c => c.checked);
    const paths = checkedBoxes.map(c => decodeURIComponent(c.getAttribute("data-path")));
    if (paths.length === 0) return;
    
    if (!confirm(`Are you sure you want to permanently delete these ${paths.length} selected files?`)) {
        return;
    }
    
    try {
        const response = await fetch("/api/file/bulk-delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filepaths: paths })
        });
        if (response.ok) {
            triggerSearch();
            fetchStats();
            fetchDirectoryTree();
        } else {
            const err = await response.json();
            alert(`Bulk deletion encountered errors: ${JSON.stringify(err.detail)}`);
        }
    } catch (e) {
        console.error("Bulk deletion failed", e);
    }
}

async function showPreview(path) {
    if (activeTab !== "search") {
        switchTab("search");
    }
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
        const inlineEditor = document.getElementById("inline-text-editor");
        if (inlineEditor) {
            inlineEditor.classList.add("hidden");
        }
        const previewCode = document.getElementById("preview-code");
        if (previewCode && previewCode.parentElement) {
            previewCode.parentElement.classList.remove("hidden");
        }
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
            
            // Render bounding boxes on load (scaled dynamically)
            img.onload = () => {
                overlay.innerHTML = "";
                const scaleX = img.clientWidth / img.naturalWidth;
                const scaleY = img.clientHeight / img.naturalHeight;
                
                if (data.coords && data.coords.length > 0) {
                    data.coords.forEach(box => {
                        const highlight = document.createElement("div");
                        highlight.className = "ocr-bounding-highlight";
                        highlight.style.left = `${box.x * scaleX}px`;
                        highlight.style.top = `${box.y * scaleY}px`;
                        highlight.style.width = `${box.w * scaleX}px`;
                        highlight.style.height = `${box.h * scaleY}px`;
                        highlight.title = box.word;
                        overlay.appendChild(highlight);
                    });
                }
            };
            
            // Fallback render in case onload cached or fast
            if (img.complete) {
                img.onload();
            }
        } else if (suffix === 'html' && data.content) {
            previewArea.appendChild(overlay);
            const iframe = document.createElement("iframe");
            iframe.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
            iframe.style.width = "100%";
            iframe.style.height = "500px";
            iframe.style.border = "none";
            iframe.style.background = "white";
            previewArea.appendChild(iframe);
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
        const searchLayout = document.querySelector(".search-layout");
        if (searchLayout) {
            searchLayout.classList.add("with-preview");
        }
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
            const col = globalTagColors[t];
            if (col) {
                span.style.background = col;
                span.style.borderColor = col;
            }
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
    const searchLayout = document.querySelector(".search-layout");
    if (searchLayout) {
        searchLayout.classList.remove("with-preview");
    }
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
    
    const titleInput = document.getElementById("pdf-title-input");
    const customTitle = titleInput ? titleInput.value.trim() : "";
    const themeSelect = document.getElementById("pdf-theme-select");
    const themePalette = themeSelect ? themeSelect.value : "indigo";
    
    const params = [
        `style_template=${template}`, 
        `include_notes=${includeNotes}`,
        `report_title=${encodeURIComponent(customTitle)}`,
        `theme_palette=${themePalette}`
    ];
    
    // Check if user entered multiple tags inside pdf-tags-input
    const tagsInput = document.getElementById("pdf-tags-input");
    const multiTags = tagsInput ? tagsInput.value.trim() : "";
    
    if (multiTags) {
        params.push(`tag=${encodeURIComponent(multiTags)}`);
    } else if (selectedTag) {
        params.push(`tag=${encodeURIComponent(selectedTag)}`);
    }
    
    if (selectedCategory && selectedCategory !== "all") params.push(`category=${encodeURIComponent(selectedCategory)}`);
    if (folderScopePath) params.push(`folder_path=${encodeURIComponent(folderScopePath)}`);
    
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
let selectedNodeId = null;
Object.defineProperty(window, "selectedNodeId", {
    get: () => selectedNodeId,
    set: (v) => { selectedNodeId = v; }
});
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
    if (graphAnimFrame) {
        cancelAnimationFrame(graphAnimFrame);
    }
    const canvas = document.getElementById("concept-graph-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    
    let graphLayoutPreset = document.getElementById("graph-layout-preset").value || "force";
    
    window.changeGraphLayoutPreset = () => {
        graphLayoutPreset = document.getElementById("graph-layout-preset").value;
        applyLayoutPreset();
    };

    function applyLayoutPreset() {
        if (graphLayoutPreset === "circular") {
            const radius = Math.min(canvas.width, canvas.height) * 0.35;
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            nodes.forEach((n, idx) => {
                const angle = (idx / nodes.length) * 2 * Math.PI;
                n.x = cx + radius * Math.cos(angle);
                n.y = cy + radius * Math.sin(angle);
                n.vx = 0; n.vy = 0;
            });
        } else if (graphLayoutPreset === "grid") {
            const cols = Math.ceil(Math.sqrt(nodes.length));
            const spacingX = canvas.width / (cols + 1);
            const spacingY = canvas.height / (Math.ceil(nodes.length / cols) + 1);
            nodes.forEach((n, idx) => {
                const r = Math.floor(idx / cols);
                const c = idx % cols;
                n.x = spacingX * (c + 1);
                n.y = spacingY * (r + 1);
                n.vx = 0; n.vy = 0;
            });
        } else if (graphLayoutPreset === "tree") {
            // Simple top-down tree levels based on node idx
            const levels = 4;
            const levelHeight = canvas.height / (levels + 1);
            nodes.forEach((n, idx) => {
                const lvl = idx % levels;
                const siblingsCount = Math.ceil(nodes.length / levels);
                const posInLvl = Math.floor(idx / levels);
                const spacingX = canvas.width / (siblingsCount + 1);
                n.x = spacingX * (posInLvl + 1);
                n.y = levelHeight * (lvl + 1);
                n.vx = 0; n.vy = 0;
            });
        } else {
            // Assign random initial positions for force layout
            nodes.forEach(n => {
                if (!n.x) {
                    n.x = Math.random() * canvas.width;
                    n.y = Math.random() * canvas.height;
                }
                n.vx = 0; n.vy = 0;
            });
        }
    }
    
    // Assign random initial positions
    nodes.forEach(n => {
        n.x = Math.random() * canvas.width;
        n.y = Math.random() * canvas.height;
        n.vx = 0;
        n.vy = 0;
    });
    applyLayoutPreset();
    
    let draggedNode = null;
    let zoomScale = 1.0;
    let offsetX = 0;
    let offsetY = 0;
    let isPanning = false;
    let panStartX = 0;
    let panStartY = 0;

    window.zoomConceptGraph = (factor) => {
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const gcx = (cx - offsetX) / zoomScale;
        const gcy = (cy - offsetY) / zoomScale;
        zoomScale *= factor;
        zoomScale = Math.max(0.2, Math.min(zoomScale, 5.0));
        offsetX = cx - gcx * zoomScale;
        offsetY = cy - gcy * zoomScale;
    };
    window.resetConceptGraphView = () => {
        zoomScale = 1.0;
        offsetX = 0;
        offsetY = 0;
    };
    
    // ponytail: interactive mouse gesture handlers to support drag and drop nodes and background viewport pan/zoom
    canvas.onmousedown = (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
        const my = (e.clientY - rect.top) * (canvas.height / rect.height);
        
        let nearestNode = null;
        let minDist = 25;
        
        nodes.forEach(n => {
            const sx = n.x * zoomScale + offsetX;
            const sy = n.y * zoomScale + offsetY;
            const dist = Math.sqrt((sx - mx) * (sx - mx) + (sy - my) * (sy - my));
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
        const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
        const my = (e.clientY - rect.top) * (canvas.height / rect.height);

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
        const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
        const my = (e.clientY - rect.top) * (canvas.height / rect.height);
        
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
        if (graphLayoutPreset !== "force") return;
        
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
            
            // Check if node matches the search input query for bright yellow border highlighting
            const qInput = document.getElementById("search-input");
            const qVal = qInput ? qInput.value.trim().toLowerCase() : "";
            if (qVal && n.label.toLowerCase().includes(qVal)) {
                ctx.strokeStyle = "#f59e0b"; // Amber/yellow highlight border
                ctx.lineWidth = 3.0;
                ctx.stroke();
            }
            
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

async function fetchSynonymsList() {
    try {
        const response = await fetch("/api/synonyms");
        const data = await response.json();
        const container = document.getElementById("sidebar-synonyms");
        container.innerHTML = "";
        if (!data.synonyms || data.synonyms.length === 0) {
            container.innerHTML = '<span class="rules-empty">No synonyms configured.</span>';
            return;
        }
        data.synonyms.forEach(item => {
            const div = document.createElement("div");
            div.className = "rule-item";
            div.style.fontSize = "0.75rem";
            div.style.padding = "2px 0";
            div.innerHTML = `<span><strong>${item.word}</strong>: ${item.substitutes}</span>`;
            container.appendChild(div);
        });
    } catch (e) {
        console.error(e);
    }
}

async function addWordSynonym() {
    const wInput = document.getElementById("synonym-word");
    const sInput = document.getElementById("synonym-substitutes");
    const word = wInput.value.trim();
    const substitutes = sInput.value.trim();
    if (!word || !substitutes) return;

    try {
        const response = await fetch("/api/synonyms", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ word, substitutes })
        });
        if (response.ok) {
            wInput.value = "";
            sInput.value = "";
            fetchSynonymsList();
        }
    } catch (e) {
        console.error(e);
    }
}

async function scheduleBackupAction() {
    const secs = parseInt(document.getElementById("backup-seconds-input").value || 3600);
    try {
        const response = await fetch("/api/backups/schedule", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ interval_seconds: secs })
        });
        if (response.ok) {
            document.getElementById("backup-schedule-status").innerText = `Active schedule: ${secs}s`;
        }
    } catch (e) {
        console.error(e);
    }
}

// Hook list loading into DOMContentLoaded checks
document.addEventListener("DOMContentLoaded", () => {
    fetchSynonymsList();
});

// client-side LLM runner chat engine (Milestone 3)
let chatHistory = [];

function handleChatKeyDown(e) {
    if (e.key === "Enter") {
        sendChatMessage();
    }
}

function sendChatMessage() {
    const inputEl = document.getElementById("chat-input");
    const sendBtnEl = document.getElementById("chat-send-btn");
    if (!inputEl) return;
    const text = inputEl.value.trim();
    if (!text) return;

    // Clear input
    inputEl.value = "";

    // Append User message
    appendChatMessage("User", text, "user");

    // Disable inputs during generation
    inputEl.disabled = true;
    if (sendBtnEl) sendBtnEl.disabled = true;

    // Append a temporary loading element
    const messagesContainer = document.getElementById("chat-messages");
    let loadingEl = null;
    if (messagesContainer) {
        loadingEl = document.createElement("div");
        loadingEl.className = "chat-message assistant loading";

        const senderEl = document.createElement("span");
        senderEl.className = "message-sender";
        senderEl.innerText = "Assistant";

        const contentEl = document.createElement("span");
        contentEl.className = "message-content";
        contentEl.innerText = "Thinking...";

        loadingEl.appendChild(senderEl);
        loadingEl.appendChild(contentEl);
        messagesContainer.appendChild(loadingEl);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    const tempVal = document.getElementById("llm-temp-slider") ? parseFloat(document.getElementById("llm-temp-slider").value) : 0.3;
    const toppVal = document.getElementById("llm-topp-slider") ? parseFloat(document.getElementById("llm-topp-slider").value) : 0.9;

    // Call /api/chat via fetch, keeping track of history
    fetch("/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: text,
            history: chatHistory,
            temperature: tempVal,
            top_p: toppVal
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Remove loading element
        if (loadingEl && loadingEl.parentNode) {
            loadingEl.parentNode.removeChild(loadingEl);
        }

        const reply = data.response;
        const sources = data.sources || [];
        appendChatMessage("Assistant", reply, "assistant", sources);

        // Keep track of history
        chatHistory.push({ role: "user", content: text });
        chatHistory.push({ role: "assistant", content: reply });
    })
    .catch(error => {
        console.error("Error in chat:", error);
        // Remove loading element
        if (loadingEl && loadingEl.parentNode) {
            loadingEl.parentNode.removeChild(loadingEl);
        }
        appendChatMessage("System", `Error: ${error.message}`, "system");
    })
    .finally(() => {
        // Enable inputs
        inputEl.disabled = false;
        if (sendBtnEl) sendBtnEl.disabled = false;
        inputEl.focus();
    });
}

function appendChatMessage(sender, content, className, sources = null) {
    const messagesContainer = document.getElementById("chat-messages");
    if (!messagesContainer) return;

    const msgEl = document.createElement("div");
    msgEl.className = `chat-message ${className}`;

    const senderEl = document.createElement("span");
    senderEl.className = "message-sender";
    senderEl.innerText = sender;

    const contentEl = document.createElement("span");
    contentEl.className = "message-content";
    contentEl.innerText = content;

    const timeEl = document.createElement("span");
    timeEl.className = "message-time";
    const now = new Date();
    const pad = (n) => n.toString().padStart(2, '0');
    timeEl.innerText = `${pad(now.getHours())}:${pad(now.getMinutes())}`;

    msgEl.appendChild(senderEl);
    msgEl.appendChild(contentEl);
    msgEl.appendChild(timeEl);

    if (sources && sources.length > 0) {
        const sourcesContainer = document.createElement("div");
        sourcesContainer.className = "message-sources";
        sourcesContainer.style.fontSize = "0.75rem";
        sourcesContainer.style.marginTop = "0.4rem";
        sourcesContainer.style.color = "var(--text-secondary)";
        sourcesContainer.style.borderTop = "1px solid var(--border-color)";
        sourcesContainer.style.paddingTop = "0.3rem";
        
        const label = document.createElement("span");
        label.innerText = "Sources: ";
        label.style.fontWeight = "600";
        sourcesContainer.appendChild(label);
        
        sources.forEach((src, idx) => {
            const link = document.createElement("a");
            link.href = "#";
            link.innerText = src.filename;
            link.style.color = "var(--accent)";
            link.style.textDecoration = "underline";
            link.style.marginRight = "0.5rem";
            link.onclick = (e) => {
                e.preventDefault();
                switchTab('workspace');
                showPreview(src.filepath);
            };
            sourcesContainer.appendChild(link);
            if (idx < sources.length - 1) {
                sourcesContainer.appendChild(document.createTextNode(", "));
            }
        });
        msgEl.appendChild(sourcesContainer);
    }

    messagesContainer.appendChild(msgEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

window.handleChatKeyDown = handleChatKeyDown;
window.sendChatMessage = sendChatMessage;


/* Workspace Tree-Explorer & Split-screen functions */
let currentWorkspaceFilePath = null;

async function selectWorkspaceFile(path) {
    currentWorkspaceFilePath = path;
    try {
        const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
        if (!response.ok) {
            console.error("Failed to load file details");
            return;
        }
        const data = await response.json();

        const dashboard = document.getElementById("workspace-dashboard");
        const splitScreen = document.getElementById("workspace-split-screen");
        if (dashboard) dashboard.classList.add("hidden");
        if (splitScreen) splitScreen.classList.remove("hidden");

        const textarea = document.getElementById("workspace-editor-textarea");
        const saveBtn = document.getElementById("workspace-save-btn");
        
        textarea.value = data.content || "";
        textarea.removeAttribute("disabled");
        saveBtn.removeAttribute("disabled");

        renderWorkspacePreview(data);
        fetchWorkspaceInsights(path);
    } catch (error) {
        console.error("Error selecting workspace file:", error);
    }
}

function renderWorkspacePreview(data) {
    const previewContent = document.getElementById("workspace-preview-content");
    if (!previewContent) return;
    previewContent.innerHTML = "";

    const suffix = data.filename.split('.').pop().toLowerCase();

    if (suffix === 'pdf') {
        const iframe = document.createElement("iframe");
        iframe.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.border = "none";
        iframe.style.background = "white";
        previewContent.appendChild(iframe);
    } else if (['png', 'jpg', 'jpeg', 'bmp', 'gif'].includes(suffix)) {
        const img = document.createElement("img");
        img.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
        img.style.maxWidth = "100%";
        img.style.maxHeight = "100%";
        img.style.objectFit = "contain";
        img.style.display = "block";
        img.style.margin = "auto";
        previewContent.appendChild(img);
    } else if (suffix === 'html') {
        const iframe = document.createElement("iframe");
        iframe.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.border = "none";
        iframe.style.background = "white";
        previewContent.appendChild(iframe);
    } else if (data.content !== undefined && data.content !== null) {
        const pre = document.createElement("pre");
        pre.style.margin = "0";
        pre.style.padding = "1rem";
        pre.style.fontFamily = "monospace";
        pre.style.fontSize = "0.85rem";
        pre.style.color = "var(--text-primary)";
        pre.style.whiteSpace = "pre-wrap";
        pre.style.wordBreak = "break-all";
        
        const code = document.createElement("code");
        code.innerText = data.content;
        pre.appendChild(code);
        previewContent.appendChild(pre);
    } else {
        const div = document.createElement("div");
        div.className = "preview-placeholder";
        div.innerText = "[Binary File - Visual Preview Not Available]";
        previewContent.appendChild(div);
    }
}

async function saveWorkspaceFile() {
    if (!currentWorkspaceFilePath) return;
    const saveBtn = document.getElementById("workspace-save-btn");
    const textarea = document.getElementById("workspace-editor-textarea");
    const originalText = saveBtn.innerText;
    
    saveBtn.innerText = "Saving...";
    saveBtn.setAttribute("disabled", "true");

    try {
        const response = await fetch("/api/file/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                path: currentWorkspaceFilePath,
                content: textarea.value
            })
        });

        if (response.ok) {
            saveBtn.innerText = "Saved!";
            setTimeout(() => {
                saveBtn.innerText = originalText;
                saveBtn.removeAttribute("disabled");
            }, 1500);

            // Refresh preview
            selectWorkspaceFile(currentWorkspaceFilePath);

            // Refresh stats, tree and search lists
            fetchStats();
            fetchDirectoryTree();
            if (typeof triggerSearch === "function") {
                triggerSearch();
            }
        } else {
            alert("Failed to save file changes.");
            saveBtn.innerText = originalText;
            saveBtn.removeAttribute("disabled");
        }
    } catch (error) {
        console.error("Error saving workspace file:", error);
        alert("Error saving file: " + error.message);
        saveBtn.innerText = originalText;
        saveBtn.removeAttribute("disabled");
    }
}

function closeWorkspaceEditor() {
    currentWorkspaceFilePath = null;
    const dashboard = document.getElementById("workspace-dashboard");
    const splitScreen = document.getElementById("workspace-split-screen");
    if (dashboard) dashboard.classList.remove("hidden");
    if (splitScreen) splitScreen.classList.add("hidden");
    
    // Clear insights pane
    const insightsContent = document.getElementById("workspace-insights-content");
    if (insightsContent) {
        insightsContent.innerHTML = '<span class="insights-placeholder">Select a document to load insights.</span>';
    }
    const regenerateBtn = document.getElementById("workspace-regenerate-insights-btn");
    if (regenerateBtn) {
        regenerateBtn.setAttribute("disabled", "true");
    }
}

window.selectWorkspaceFile = selectWorkspaceFile;
window.saveWorkspaceFile = saveWorkspaceFile;
window.closeWorkspaceEditor = closeWorkspaceEditor;
window.fetchWorkspaceInsights = fetchWorkspaceInsights;


// --- Split-Screen Document Insights (Milestone 4) ---

// ponytail: lightweight regex-based markdown parser to avoid external dependencies
function renderMarkdown(md) {
    if (!md) return "";
    let html = md;
    
    // Escape HTML tags to establish a secure execution boundary
    html = html
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
        
    // Headers
    html = html.replace(/^### (.*?)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.*?)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.*?)$/gm, "<h1>$1</h1>");
    
    // Unordered lists
    html = html.replace(/^[ \t]*[\*\-\+][ \t](.*?)\r?$/gm, "<ul><li>$1</li></ul>");
    // Ordered lists (capturing the number to maintain value)
    html = html.replace(/^[ \t]*(\d+)\.[ \t](.*?)\r?$/gm, '<ol><li value="$1">$2</li></ol>');
    // Merge adjacent list containers
    html = html.replace(/<\/ul>\s*<ul>/g, "");
    html = html.replace(/<\/ol>\s*<ol>/g, "");
    
    // Bold and Italic formatting
    html = html.replace(/\*\*([^<>]+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/__([^<>]+?)__/g, "<strong>$1</strong>");
    html = html.replace(/\*([^<>]+?)\*/g, "<em>$1</em>");
    html = html.replace(/_([^<>]+?)_/g, "<em>$1</em>");
    
    // Paragraph tags
    let result = [];
    let currentPara = [];
    let lines = html.split(/\r?\n/);
    for (let line of lines) {
        let trimmed = line.trim();
        if (!trimmed) {
            if (currentPara.length > 0) {
                result.push(`<p>${currentPara.join("<br>")}</p>`);
                currentPara = [];
            }
            continue;
        }
        let lower = trimmed.toLowerCase();
        if (lower.startsWith("<h") || lower.startsWith("<ul") || lower.startsWith("<ol") || lower.startsWith("<li") || lower.startsWith("</ul") || lower.startsWith("</ol")) {
            if (currentPara.length > 0) {
                result.push(`<p>${currentPara.join("<br>")}</p>`);
                currentPara = [];
            }
            result.push(trimmed);
        } else {
            currentPara.push(trimmed);
        }
    }
    if (currentPara.length > 0) {
        result.push(`<p>${currentPara.join("<br>")}</p>`);
    }
    html = result.join("");

    return html;
}

async function fetchWorkspaceInsights(path) {
    const filePath = path || currentWorkspaceFilePath;
    if (!filePath) return;

    const insightsContent = document.getElementById("workspace-insights-content");
    const regenerateBtn = document.getElementById("workspace-regenerate-insights-btn");

    if (insightsContent) {
        insightsContent.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.5rem; color: var(--text-secondary); padding: 2rem 0;">
                <div class="insights-loading-spinner"></div>
                <span>Generating insights using local LLM...</span>
            </div>
        `;
    }

    if (regenerateBtn) {
        regenerateBtn.setAttribute("disabled", "true");
        regenerateBtn.innerText = "Generating...";
    }

    try {
        const tempVal = document.getElementById("llm-temp-slider") ? parseFloat(document.getElementById("llm-temp-slider").value) : 0.3;
        const toppVal = document.getElementById("llm-topp-slider") ? parseFloat(document.getElementById("llm-topp-slider").value) : 0.9;
        
        const response = await fetch("/api/file/insights", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                filepath: filePath,
                temperature: tempVal,
                top_p: toppVal
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `HTTP error ${response.status}`);
        }

        const data = await response.json();

        if (insightsContent) {
            insightsContent.innerHTML = renderMarkdown(data.insights);
        }
    } catch (error) {
        console.error("Error fetching workspace insights:", error);
        if (insightsContent) {
            insightsContent.innerHTML = `
                <div style="color: #ff5555; padding: 0.5rem; border: 1px dashed #ff5555; border-radius: 2px; font-size: 0.8rem; background: rgba(255, 85, 85, 0.05);">
                    <strong>Error generating insights:</strong> ${error.message}
                </div>
            `;
        }
    } finally {
        if (regenerateBtn) {
            regenerateBtn.removeAttribute("disabled");
            regenerateBtn.innerText = "Regenerate";
        }
    }
}


