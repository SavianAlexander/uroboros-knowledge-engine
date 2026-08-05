function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showToast(message, type = 'info', duration = 3500) {
    if (!message) return;
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-notification ${type}`;

    const iconMap = {
        success: '✓',
        error: '✕',
        danger: '⚠️',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-weight: bold; font-size: 0.9rem;">${iconMap[type] || 'ℹ️'}</span>
            <span>${escapeHtml(message)}</span>
        </div>
        <button class="toast-close-btn" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);

    if (duration > 0) {
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-10px)';
                setTimeout(() => toast.remove(), 250);
            }
        }, duration);
    }
}
window.showToast = showToast;

function getFileTypeIcon(filenameOrExt) {
    if (!filenameOrExt) return '/assets/ext_doc.svg';
    const ext = filenameOrExt.includes('.') ? filenameOrExt.split('.').pop().toLowerCase() : filenameOrExt.toLowerCase();
    const cat = typeof getFileCategory === 'function' ? getFileCategory(ext) : 'doc';
    return `/assets/ext_${cat}.svg`;
}
window.getFileTypeIcon = getFileTypeIcon;

function debounce(func, wait = 150) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
window.debounce = debounce;

function togglePdfExportDrawer() {
    const drawer = document.getElementById("pdf-export-drawer");
    if (drawer) {
        drawer.classList.toggle("hidden");
    }
}
window.togglePdfExportDrawer = togglePdfExportDrawer;

function setGraphPreset(presetName) {
    const catFilter = document.getElementById("graph-category-filter");
    if (!catFilter) return;
    if (presetName === 'code') {
        catFilter.value = 'code';
        filterGraphCategory('code');
    } else if (presetName === 'docs') {
        catFilter.value = 'doc';
        filterGraphCategory('doc');
    } else {
        catFilter.value = 'all';
        filterGraphCategory('all');
    }
}
window.setGraphPreset = setGraphPreset;

function toggleCommandPalette() {
    const modal = document.getElementById("command-palette-modal");
    if (!modal) return;
    const isHidden = modal.classList.toggle("hidden");
    if (!isHidden) {
        const input = document.getElementById("command-palette-input");
        if (input) {
            input.value = "";
            filterCommandPalette("");
            setTimeout(() => input.focus(), 50);
            setupPaletteKeyboardNav();
        }
        if (!modal.dataset.backdropBound) {
            modal.dataset.backdropBound = "true";
            modal.addEventListener("click", (e) => {
                if (e.target === modal) {
                    toggleCommandPalette();
                }
            });
        }
    }
}
window.toggleCommandPalette = toggleCommandPalette;

let paletteActiveIdx = -1;

function setupPaletteKeyboardNav() {
    const input = document.getElementById("command-palette-input");
    if (!input || input.dataset.navBound) return;
    input.dataset.navBound = "true";
    input.addEventListener("keydown", (e) => {
        const items = Array.from(document.querySelectorAll("#command-palette-list .palette-item")).filter(el => el.style.display !== "none");
        if (items.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            paletteActiveIdx = (paletteActiveIdx + 1) % items.length;
            items.forEach((item, idx) => item.classList.toggle("active", idx === paletteActiveIdx));
            items[paletteActiveIdx].scrollIntoView({ block: "nearest" });
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            paletteActiveIdx = (paletteActiveIdx - 1 + items.length) % items.length;
            items.forEach((item, idx) => item.classList.toggle("active", idx === paletteActiveIdx));
            items[paletteActiveIdx].scrollIntoView({ block: "nearest" });
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (paletteActiveIdx >= 0 && paletteActiveIdx < items.length) {
                items[paletteActiveIdx].click();
            } else if (items.length > 0) {
                items[0].click();
            }
        }
    });
}

function filterCommandPalette(query) {
    const q = (query || "").trim().toLowerCase();
    const items = document.querySelectorAll("#command-palette-list .palette-item");
    items.forEach(el => {
        const text = el.innerText.toLowerCase();
        el.style.display = (!q || text.includes(q)) ? "block" : "none";
    });
}
window.filterCommandPalette = filterCommandPalette;

function executePaletteCommand(cmd) {
    toggleCommandPalette();
    if (cmd === 'search') switchTab('search');
    else if (cmd === 'chat') switchTab('chat');
    else if (cmd === 'graph') { switchTab('search'); selectCategory(document.querySelector('[data-category="graph"]')); }
    else if (cmd === 'config') switchTab('config');
    else if (cmd === 'theme') toggleAppTheme();
    else if (cmd === 'csv') exportStatsCsv();
    else if (cmd === 'pdf') exportPdfReport();
}
window.executePaletteCommand = executePaletteCommand;

function toggleWorkspaceSidebar() {
    const sidebar = document.getElementById("workspace-sidebar");
    const toggleBtn = document.getElementById("sidebar-toggle-btn");
    if (sidebar) {
        const collapsed = sidebar.classList.toggle("collapsed");
        if (toggleBtn) toggleBtn.innerText = collapsed ? "►" : "◄";
    }
}
window.toggleWorkspaceSidebar = toggleWorkspaceSidebar;

function switchTab(tabId) {
    activeTab = tabId;
    localStorage.setItem("active-tab", tabId);
    
    // Update active visual styles of horizontal tabs
    document.querySelectorAll(".tab-link").forEach(btn => {
        const btnTab = btn.getAttribute("data-tab");
        let isActive = (btnTab === tabId);
        if (!isActive) {
            if ((tabId === "search" || tabId === "explorer") && (btnTab === "explorer" || btnTab === "search")) isActive = true;
            if ((tabId === "config" || tabId === "processes") && (btnTab === "processes" || btnTab === "config")) isActive = true;
            if ((tabId === "workspace" || tabId === "diagnostics") && (btnTab === "diagnostics" || btnTab === "workspace")) isActive = true;
        }
        btn.classList.toggle("active", isActive);
    });
    
    // Update tab visibility (supporting corporate view IDs and legacy fallbacks)
    document.querySelectorAll(".tab-view-content").forEach(view => {
        const viewId = view.id.replace("-tab-view", "");
        let isMatch = (viewId === tabId);
        if (!isMatch) {
            if ((tabId === "diagnostics" || tabId === "workspace") && (viewId === "workspace" || viewId === "diagnostics")) isMatch = true;
            if ((tabId === "processes" || tabId === "config") && (viewId === "config" || viewId === "processes")) isMatch = true;
            if ((tabId === "explorer" || tabId === "search") && (viewId === "search" || viewId === "explorer")) isMatch = true;
        }
        view.classList.toggle("hidden", !isMatch);
    });
    
    // Lazy-update data endpoints for active view
    if (tabId === "diagnostics" || tabId === "workspace") {
        fetchStats();
        fetchDirectoryTree();
    } else if (tabId === "processes" || tabId === "config") {
        fetchAutoRules();
        fetchMacrosList();
        fetchSynonymsList();
        fetchSnapshotsList();
        fetchPeers();
    } else if (tabId === "explorer" || tabId === "search") {
        fetchGlobalTags();
        triggerSearch();
        fetchDirectoryTree();
    } else if (tabId === "settings") {
        fetchStats();
    } else if (tabId === "account") {
        fetchStats();
        fetchSystemEnv();
    } else if (tabId === "chat") {
        fetchChatSessions();
    }
}

// ponytail: old toggleAccordion(groupId) removed — replaced by toggleAccordion(headerEl) at end of file

let searchTimeout;
let selectedCategory = "all";
let selectedTag = null;
let currentPreviewPath = null;
let searchMode = "keyword"; // "keyword" or "semantic"

let isEditingFile = false;

let folderScopePath = null;
let currentSearchResults = [];

document.addEventListener("DOMContentLoaded", () => {
    // Restore theme preference
    if (localStorage.getItem("app-theme") === "light") {
        document.body.classList.add("light-theme");
    }

    // Global Keyboard Shortcuts (Ctrl/Cmd+K -> Search, Ctrl/Cmd+P -> Palette, Ctrl/Cmd+B -> Sidebar, Ctrl/Cmd+S -> Save, Esc -> Close)
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            switchTab("search");
            const searchInput = document.getElementById("search-input");
            if (searchInput) searchInput.focus();
        } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "p") {
            e.preventDefault();
            toggleCommandPalette();
        } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
            e.preventDefault();
            toggleWorkspaceSidebar();
        } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
            const saveBtn = document.getElementById("workspace-save-btn");
            if (saveBtn && !saveBtn.disabled) {
                e.preventDefault();
                saveWorkspaceFile();
            }
        } else if (e.key === "Escape") {
            closePreview();
            const autoDropdown = document.getElementById("search-autocomplete-dropdown");
            if (autoDropdown) autoDropdown.classList.add("hidden");
            const pdfDrawer = document.getElementById("pdf-export-drawer");
            if (pdfDrawer && !pdfDrawer.classList.contains("hidden")) {
                pdfDrawer.classList.add("hidden");
            }
            const paletteModal = document.getElementById("command-palette-modal");
            if (paletteModal && !paletteModal.classList.contains("hidden")) {
                paletteModal.classList.add("hidden");
            }
        }
    });

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
    initSplitDivider();
    initMinimapListeners();

    const resultsSortSelect = document.getElementById("results-sort-select");
    if (resultsSortSelect) {
        resultsSortSelect.addEventListener("change", () => {
            applyResultsSorting();
        });
    }
    
    // ponytail: register search autosuggest events
    const searchInput = document.getElementById("search-input");
    const dropdown = document.getElementById("search-autocomplete-dropdown");
    let activeSuggestionIdx = -1;
    
    if (searchInput && dropdown) {
        const handleSearchInput = debounce(async (e) => {
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
                        
                        const fragment = document.createDocumentFragment();
                        data.suggestions.forEach((item, idx) => {
                            const itemEl = document.createElement("div");
                            itemEl.className = "autocomplete-item";
                            itemEl.dataset.index = idx;
                            itemEl.innerHTML = `
                                <span>${escapeHtml(item.text)}</span>
                                <span class="autocomplete-type">${escapeHtml(item.type)}</span>
                            `;
                            
                            itemEl.onclick = () => {
                                words[words.length - 1] = item.text;
                                searchInput.value = words.join(" ") + " ";
                                dropdown.classList.add("hidden");
                                triggerSearch();
                            };
                            fragment.appendChild(itemEl);
                        });
                        dropdown.appendChild(fragment);
                    } else {
                        dropdown.classList.add("hidden");
                    }
                } catch (err) {
                    console.error("Suggestion fetch failed", err);
                }
            } else {
                dropdown.classList.add("hidden");
            }
        }, 150);

        searchInput.addEventListener("input", handleSearchInput);

        searchInput.addEventListener("focus", async () => {
            if (!searchInput.value.trim()) {
                try {
                    const res = await fetch("/api/search/history");
                    const data = await res.json();
                    if (data.history && data.history.length > 0) {
                        dropdown.classList.remove("hidden");
                        dropdown.innerHTML = "";
                        activeSuggestionIdx = -1;
                        
                        const uniqueQueries = Array.from(new Set(data.history.map(item => item.query_string))).slice(0, 5);
                        
                        if (uniqueQueries.length > 0) {
                            const fragment = document.createDocumentFragment();
                            uniqueQueries.forEach((item, idx) => {
                                const itemEl = document.createElement("div");
                                itemEl.className = "autocomplete-item";
                                itemEl.dataset.index = idx;
                                itemEl.innerHTML = `
                                    <span style="font-weight: 500;">${escapeHtml(item)}</span>
                                    <span class="autocomplete-type" style="color: var(--accent);">history</span>
                                `;
                                itemEl.onclick = () => {
                                    searchInput.value = item;
                                    dropdown.classList.add("hidden");
                                    triggerSearch();
                                };
                                fragment.appendChild(itemEl);
                            });
                            dropdown.appendChild(fragment);
                        }
                    }
                } catch (err) {
                    console.error("Failed to load search history for autocomplete:", err);
                }
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
    if (typeof window.setGraphNeedsRedraw === "function") window.setGraphNeedsRedraw();
}

async function fetchMacrosList() {
    try {
        const response = await fetch("/api/macros");
        const data = await response.json();
        const select = document.getElementById("macro-select");
        if (select) select.innerHTML = '<option value="">-- Apply Macro --</option>';
        
        const sidebarContainer = document.getElementById("sidebar-macros");
        if (!sidebarContainer) return;
        sidebarContainer.innerHTML = "";
        
        if (data.macros && data.macros.length > 0) {
            let html = `<table class="high-density-table"><thead><tr><th>Macro</th><th>Expansion</th><th>Action</th></tr></thead><tbody>`;
            data.macros.forEach(m => {
                if (select) {
                    const opt = document.createElement("option");
                    opt.value = m.expansion;
                    opt.innerText = `%${m.name}% (${m.expansion})`;
                    select.appendChild(opt);
                }
                html += `<tr>
                    <td><strong>%${escapeHtml(m.name)}%</strong></td>
                    <td title="${escapeHtml(m.expansion)}">${escapeHtml(m.expansion)}</td>
                    <td><button class="rule-del-btn" onclick="deleteQueryMacro('${escapeHtml(m.name)}')">✕</button></td>
                </tr>`;
            });
            html += `</tbody></table>`;
            sidebarContainer.innerHTML = html;
        } else {
            sidebarContainer.innerHTML = '<span class="rules-empty">No macros configured.</span>';
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

let lastStatsDataStr = null;

async function fetchStats() {
    try {
        const response = await fetch("/api/stats");
        const dataStr = await response.text();
        if (dataStr === lastStatsDataStr) return;
        lastStatsDataStr = dataStr;
        const data = JSON.parse(dataStr);
        
        animateCountUp(document.getElementById("stat-files"), data.total_files || 0);
        document.getElementById("stat-size").innerText = formatBytes(data.total_size);
        
        const ribFiles = document.getElementById("stat-files-ribbon");
        if (ribFiles) animateCountUp(ribFiles, data.total_files || 0);
        const ribSize = document.getElementById("stat-size-ribbon");
        if (ribSize) ribSize.innerText = formatBytes(data.total_size);
        const ribTags = document.getElementById("stat-tags-ribbon");
        if (ribTags) animateCountUp(ribTags, data.total_tags || 0);
        const ribRules = document.getElementById("stat-rules-ribbon");
        if (ribRules) animateCountUp(ribRules, data.total_rules || 0);

        const tagsEl = document.getElementById("stat-tags");
        if (tagsEl) {
            tagsEl.innerText = data.total_tags !== undefined ? data.total_tags : "-";
        }
        const rulesEl = document.getElementById("stat-rules");
        if (rulesEl) {
            rulesEl.innerText = data.total_rules !== undefined ? data.total_rules : "-";
        }
        
        if (data.active_directory) {
            document.getElementById("active-dir-label").innerText = getBasename(data.active_directory);
            document.getElementById("active-dir-label").title = data.active_directory;
        }

        const syncListEl = document.getElementById("sync-peers-list");
        if (syncListEl) {
            syncListEl.innerHTML = "";
            if (!data.sync_peers || data.sync_peers.length === 0) {
                syncListEl.innerHTML = '<span class="timeline-empty">No registered sync peers.</span>';
            } else {
                data.sync_peers.forEach(peer => {
                    const row = document.createElement("div");
                    row.className = "timeline-row";
                    const escapedName = escapeHtml(peer.name || 'Unknown');
                    const escapedAddress = escapeHtml(peer.address || '');
                    row.innerHTML = `
                        <span>${escapedName}</span>
                        <strong>${escapedAddress}</strong>
                    `;
                    syncListEl.appendChild(row);
                });
            }
        }

        // Update Radial Health Gauge
        const healthCircle = document.getElementById("health-gauge-circle");
        const healthVal = document.getElementById("health-gauge-val");
        if (healthCircle && healthVal) {
            const fileCount = data.total_files || 0;
            const healthScore = Math.min(100, Math.max(70, 100 - Math.floor(fileCount / 500)));
            const offset = 201 * (1 - healthScore / 100);
            healthCircle.style.strokeDashoffset = offset;
            healthVal.innerText = healthScore + "%";
        }

        // Update System Status Pill
        const sysBadge = document.querySelector(".status-pill-ok, .status-pill-offline");
        if (sysBadge) {
            sysBadge.className = "badge status-pill-ok";
            sysBadge.innerHTML = '<span class="pulse-dot"></span> System OK';
        }

        renderDistributionChart(data.mime_breakdown, data.total_files);
        renderTimeline(data.timeline);
        updateFileCountBadge(data.total_files);
        populateSettingsSummary(data);
        populateAccountView(data);
        fetchAnalyticsPanelData();
    } catch (error) {
        console.error("Failed to load statistics:", error);
        const sysBadge = document.querySelector(".status-pill-ok, .status-pill-offline");
        if (sysBadge) {
            sysBadge.className = "badge status-pill-offline";
            sysBadge.innerHTML = '<span class="pulse-dot"></span> Offline / Reconnecting';
        }
    }
}

// Analytics Data Fetching & Rendering Engine (Milestone 4)
async function fetchAnalyticsPanelData() {
    try {
        const [storageRes, tagsRes, searchRes, logsRes, triggersRes] = await Promise.all([
            fetch('/api/analytics/storage').then(r => r.ok ? r.json() : null),
            fetch('/api/analytics/tags').then(r => r.ok ? r.json() : null),
            fetch('/api/analytics/search-activity').then(r => r.ok ? r.json() : null),
            fetch('/api/workflows/logs').then(r => r.ok ? r.json() : null),
            fetch('/api/workflows/triggers').then(r => r.ok ? r.json() : null)
        ]);

        if (storageRes) renderStorageAnalytics(storageRes);
        if (tagsRes) renderTagAnalytics(tagsRes);
        if (searchRes) renderSearchActivity(searchRes);
        if (logsRes && triggersRes) renderWorkflowLogs(logsRes, triggersRes);
    } catch (err) {
        console.error('Failed to load document intelligence analytics panel:', err);
    }
}

function renderStorageAnalytics(data) {
    const totalBytes = Object.values(data.by_mime || {}).reduce((a, b) => a + b, 0);
    const badge = document.getElementById('storage-total-badge');
    if (badge) badge.innerText = formatBytes(totalBytes);

    const tbody = document.getElementById('storage-dirs-tbody');
    if (tbody) {
        tbody.innerHTML = (data.top_directories || []).map(dir => `
            <tr>
                <td title="${escapeHtml(dir.directory || '')}">${escapeHtml(getBasename(dir.directory || ''))}</td>
                <td style="text-align: right;">${dir.count || 0}</td>
                <td style="text-align: right;">${formatBytes(dir.size_bytes || 0)}</td>
            </tr>
        `).join('') || '<tr><td colspan="3" style="text-align:center; color:var(--text-secondary);">No directory data</td></tr>';
    }
}

function renderTagAnalytics(data) {
    const badge = document.getElementById('tag-total-badge');
    if (badge) badge.innerText = `${data.total_tags || 0} Distinct Tags`;

    const histo = document.getElementById('tag-histogram-container');
    if (histo) {
        const topTags = data.top_tags || [];
        const maxCount = Math.max(1, ...topTags.map(t => t.count || 0));
        histo.innerHTML = topTags.map(t => {
            const pct = Math.round(((t.count || 0) / maxCount) * 100);
            return `
                <div style="display:flex; align-items:center; gap:0.5rem; font-size:0.75rem;">
                    <span style="width:80px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; color:var(--accent);">${escapeHtml(t.tag || '')}</span>
                    <div style="flex:1; background:var(--input-bg); height:8px; border-radius:4px; overflow:hidden;">
                        <div style="width:${pct}%; background:var(--accent); height:100%;"></div>
                    </div>
                    <span style="width:30px; text-align:right; color:var(--text-secondary);">${t.count || 0}</span>
                </div>
            `;
        }).join('') || '<div style="font-size:0.75rem; color:var(--text-secondary);">No tags recorded</div>';
    }

    const cooc = document.getElementById('tag-cooccurrence-container');
    if (cooc) {
        cooc.innerHTML = (data.tag_cooccurrence || []).map(pair => `
            <div class="tag-pair-chip" onclick="filterSearchByTagPair('${escapeHtml(pair.tag1 || '')}', '${escapeHtml(pair.tag2 || '')}')">
                <span>${escapeHtml(pair.tag1 || '')} + ${escapeHtml(pair.tag2 || '')}</span>
                <span class="tag-pair-weight">${pair.weight || 1}</span>
            </div>
        `).join('') || '<div style="font-size:0.75rem; color:var(--text-secondary);">No co-occurring tags</div>';
    }
}

function renderSearchActivity(data) {
    const totalEl = document.getElementById('search-total-queries');
    if (totalEl) totalEl.innerText = data.total_queries || 0;

    const latEl = document.getElementById('search-avg-latency');
    if (latEl) latEl.innerText = `${(data.avg_latency_ms || 0.0).toFixed(1)} ms`;

    const latBadge = document.getElementById('search-latency-badge');
    if (latBadge) latBadge.innerText = `${(data.avg_latency_ms || 0.0).toFixed(1)} ms avg`;

    const topList = document.getElementById('search-top-queries-list');
    if (topList) {
        topList.innerHTML = (data.top_queries || []).map(q => `
            <div class="timeline-row">
                <span style="color:var(--accent);">${escapeHtml(q.query || '')}</span>
                <strong>${q.count || 0} searches</strong>
            </div>
        `).join('') || '<span class="timeline-empty">No queries logged</span>';
    }

    const recentList = document.getElementById('search-recent-queries-list');
    if (recentList) {
        recentList.innerHTML = (data.recent_queries || []).map(q => `
            <div class="timeline-row">
                <span style="color:var(--text-primary);">${escapeHtml(q.query || '')}</span>
                <strong style="color:var(--text-secondary);">${q.result_count || 0} hits (${q.mode || 'fts'})</strong>
            </div>
        `).join('') || '<span class="timeline-empty">No recent searches</span>';
    }
}

function renderWorkflowLogs(logs, triggers) {
    const activeBadge = document.getElementById('workflow-active-badge');
    if (activeBadge) {
        const activeCount = (triggers || []).filter(t => t.is_active).length;
        activeBadge.innerText = `${activeCount} Active Triggers`;
    }

    const tbody = document.getElementById('workflow-logs-tbody');
    if (tbody) {
        tbody.innerHTML = (logs || []).slice(0, 15).map(log => {
            const isOk = log.status === 'dispatched' || log.status === 'success';
            const statusClass = isOk ? 'color: var(--success);' : 'color: var(--danger);';
            const timeStr = log.executed_at ? new Date(log.executed_at).toLocaleTimeString() : '-';
            return `
                <tr>
                    <td style="color: var(--text-secondary);">${timeStr}</td>
                    <td><span class="badge" style="font-size:0.65rem;">${escapeHtml(log.event_type || '')}</span></td>
                    <td style="${statusClass} font-weight:bold;">${escapeHtml(log.status || '')}</td>
                    <td style="text-align: right;">${log.response_status_code || '-'}</td>
                    <td style="text-align: right; color: var(--text-secondary);">${log.execution_time_ms ? log.execution_time_ms.toFixed(1) + ' ms' : '-'}</td>
                </tr>
            `;
        }).join('') || '<tr><td colspan="5" style="text-align:center; color:var(--text-secondary);">No workflow execution logs</td></tr>';
    }
}

async function triggerWorkflowTest() {
    try {
        const res = await fetch('/api/workflows/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_type: 'document_ingested', payload: { test: true } })
        });
        if (res.ok) {
            fetchAnalyticsPanelData();
        }
    } catch (err) {
        console.error('Failed to trigger test workflow:', err);
    }
}
window.triggerWorkflowTest = triggerWorkflowTest;

function filterSearchByTagPair(tag1, tag2) {
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.value = `${tag1} ${tag2}`;
        switchTab("search");
        if (typeof performSearch === "function") performSearch();
    }
}
window.filterSearchByTagPair = filterSearchByTagPair;

let showAllMimeTypes = false;

function renderDistributionChart(mimeBreakdown, totalFiles) {
    const container = document.getElementById("svg-chart-container");
    container.innerHTML = "";
    
    if (!mimeBreakdown || mimeBreakdown.length === 0) {
        container.innerHTML = '<div style="font-size: 0.8rem; font-style: italic; color: var(--text-secondary);">No files indexed.</div>';
        return;
    }

    // Sort descending by count
    const sorted = [...mimeBreakdown].sort((a, b) => b.count - a.count);
    const displayList = showAllMimeTypes ? sorted : sorted.slice(0, 5);
    const fragment = document.createDocumentFragment();

    displayList.forEach(item => {
        const pct = totalFiles > 0 ? Math.round((item.count / totalFiles) * 100) : 0;
        const row = document.createElement("div");
        row.className = "chart-bar-row";
        row.onclick = () => {
            let extension = (item.mime_type || '').split('/').pop();
            if (extension === 'octet-stream') extension = 'bin';
            const searchInput = document.getElementById("search-input");
            if (searchInput) {
                searchInput.value = `type:${extension} ` + searchInput.value.replace(/type:\S+/g, "").trim();
            }
            if (activeTab !== "search" && activeTab !== "explorer") {
                switchTab("explorer");
            }
            triggerSearch();
        };
        const escapedMime = escapeHtml(item.mime_type || '');
        row.innerHTML = `
            <div class="chart-bar-info">
                <span class="chart-bar-label" title="${escapedMime}">${escapedMime}</span>
                <span>${item.count} (${pct}%)</span>
            </div>
            <div class="chart-bar-outer">
                <div class="chart-bar-inner" style="width: ${pct}%"></div>
            </div>
        `;
        fragment.appendChild(row);
    });

    // If more than 5 items and not showing all, render "Other / Misc" summary row
    if (!showAllMimeTypes && sorted.length > 5) {
        const remaining = sorted.slice(5);
        const remainingCount = remaining.reduce((acc, curr) => acc + curr.count, 0);
        const remainingPct = totalFiles > 0 ? Math.round((remainingCount / totalFiles) * 100) : 0;

        const otherRow = document.createElement("div");
        otherRow.className = "chart-bar-row";
        otherRow.style.opacity = "0.85";
        otherRow.innerHTML = `
            <div class="chart-bar-info">
                <span class="chart-bar-label">Other / Misc (${remaining.length} types)</span>
                <span>${remainingCount} (${remainingPct}%)</span>
            </div>
            <div class="chart-bar-outer">
                <div class="chart-bar-inner" style="width: ${remainingPct}%; background: var(--text-secondary);"></div>
            </div>
        `;
        fragment.appendChild(otherRow);

        // Toggle button
        const toggleBtn = document.createElement("button");
        toggleBtn.className = "mime-toggle-btn";
        toggleBtn.innerText = `[ + View All ${sorted.length} Types ]`;
        toggleBtn.onclick = () => {
            showAllMimeTypes = true;
            renderDistributionChart(mimeBreakdown, totalFiles);
        };
        fragment.appendChild(toggleBtn);
    } else if (showAllMimeTypes && sorted.length > 5) {
        const toggleBtn = document.createElement("button");
        toggleBtn.className = "mime-toggle-btn";
        toggleBtn.innerText = `[ - View Top 5 Only ]`;
        toggleBtn.onclick = () => {
            showAllMimeTypes = false;
            renderDistributionChart(mimeBreakdown, totalFiles);
        };
        fragment.appendChild(toggleBtn);
    }

    container.appendChild(fragment);
}

function renderTimeline(timeline) {
    const container = document.getElementById("timeline-container");
    container.innerHTML = "";
    
    if (!timeline || timeline.length === 0) {
        container.innerHTML = '<span class="timeline-empty">No indexing activity recorded.</span>';
        return;
    }
    
    const counts = timeline.map(t => typeof t.count === 'number' ? t.count : 1);
    const maxVal = Math.max(...counts, 1);
    const width = 60, height = 20;
    const pts = counts.map((cnt, i) => {
        const x = (i / Math.max(counts.length - 1, 1)) * width;
        const y = height - (cnt / maxVal) * (height - 4) - 2;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");

    const sparklineSvg = `
        <svg class="sparkline-svg" viewBox="0 0 ${width} ${height}">
            <polyline points="${pts}"></polyline>
        </svg>
    `;
    
    timeline.forEach((item) => {
        const row = document.createElement("div");
        row.className = "timeline-row";
        row.style.display = "flex";
        row.style.justifyContent = "space-between";
        row.style.alignItems = "center";
        row.innerHTML = `
            <span>${escapeHtml(item.day || item.filename || 'Recent')}</span>
            <div style="display:flex; align-items:center; gap:0.5rem;">
                ${sparklineSvg}
                <strong>${item.count !== undefined ? item.count + ' files' : 'Indexed'}</strong>
            </div>
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

    const oversized = fileList.filter(item => item.file && item.file.size > 50 * 1024 * 1024);
    if (oversized.length > 0) {
        const proceed = confirm(`Warning: ${oversized.length} file(s) exceed 50MB (e.g. ${oversized[0].file.name}). Uploading large files may take time. Proceed?`);
        if (!proceed) {
            if (statusMsg) statusMsg.innerText = "Upload cancelled by user.";
            return;
        }
    }

    if (statusMsg) statusMsg.innerText = `Uploading ${fileList.length} file(s)...`;
    
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
        buildTreeUI(data.tree || data.files || []);
    } catch (error) {
        console.error("Failed to fetch directory tree:", error);
    }
}

function getFileCategory(ext) {
    if (!ext) return 'doc';
    const e = ext.toLowerCase().replace(/^\./, '');
    if (['py', 'js', 'ts', 'html', 'css', 'json', 'xml', 'sh', 'sql', 'c', 'cpp', 'rs', 'go', 'java', 'php', 'rb', 'h', 'hpp', 'cs'].includes(e)) return 'code';
    if (['csv', 'xlsx', 'xls', 'tsv', 'ods'].includes(e)) return 'spreadsheet';
    if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico', 'tiff'].includes(e)) return 'image';
    if (['pdf', 'docx', 'doc', 'txt', 'md', 'rtf', 'odt', 'log'].includes(e)) return 'doc';
    if (['mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma'].includes(e)) return 'audio';
    if (['mp4', 'mkv', 'webm', 'avi', 'mov', 'wmv', 'flv'].includes(e)) return 'video';
    return 'doc';
}

function getFileIconSvg(ext, size = 12) {
    const iconPath = getFileTypeIcon(ext);
    return `<img src="${iconPath}" class="file-type-icon" style="width: ${size}px; height: ${size}px; margin-right: 4px; vertical-align: middle;" alt="${ext}" />`;
}

function buildTreeUI(files) {
    const container = document.getElementById("dir-tree");
    container.innerHTML = "";
    
    if (!files || files.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 1rem;"><span class="tree-empty">No directory indexed yet.</span><br/><button onclick="triggerIndexing()" class="settings-btn settings-btn-primary" style="margin-top: 0.5rem; padding: 0.25rem 0.6rem; font-size: 0.75rem;">⚡ Index Directory</button></div>';
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
                ${getFileIconSvg(ext, 12)}
                <span>${name}</span>
            `;
            div.onclick = () => selectWorkspaceFile(node._file.filepath);
            div.ondblclick = (e) => {
                e.stopPropagation();
                const span = div.querySelector("span");
                if (!span) return;
                const currentName = span.innerText;
                const input = document.createElement("input");
                input.type = "text";
                input.value = currentName;
                input.style.background = "var(--input-bg)";
                input.style.color = "var(--text-primary)";
                input.style.border = "1px solid var(--accent)";
                input.style.fontSize = "0.75rem";
                input.style.padding = "1px 4px";
                input.style.borderRadius = "2px";
                input.style.width = "80%";
                input.style.outline = "none";
                
                span.replaceWith(input);
                input.focus();
                input.select();
                
                let isRenaming = false;
                const confirmRename = async () => {
                    if (isRenaming) return;
                    isRenaming = true;
                    const newName = input.value.trim();
                    if (newName && newName !== currentName) {
                        try {
                            const response = await fetch("/api/file/rename", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ filepath: node._file.filepath, new_name: newName })
                            });
                            if (!response.ok) {
                                const err = await response.json();
                                alert(`Rename failed: ${err.detail}`);
                                input.replaceWith(span);
                            } else {
                                const res = await response.json();
                                loadWorkspaceData();
                                if (currentPreviewPath === node._file.filepath) {
                                    showPreview(res.new_filepath);
                                }
                            }
                        } catch (err) {
                            alert(`Error: ${err.message}`);
                            input.replaceWith(span);
                        }
                    } else {
                        input.replaceWith(span);
                    }
                };
                
                input.onkeydown = (evt) => {
                    if (evt.key === "Enter") {
                        confirmRename();
                    } else if (evt.key === "Escape") {
                        input.replaceWith(span);
                    }
                };
                input.onblur = () => {
                    confirmRename();
                };
            };
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

    const fragment = document.createDocumentFragment();
    for (const key in root) {
        renderNode(root[key], key, fragment);
    }
    container.appendChild(fragment);
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
    if (!container) return;
    container.innerHTML = "";
    if (!peers || peers.length === 0) {
        container.innerHTML = '<span class="rules-empty">No syncing nodes registered.</span>';
        return;
    }
    let html = `<table class="high-density-table"><thead><tr><th>Node Name</th><th>Address</th><th>Action</th></tr></thead><tbody>`;
    peers.forEach(peer => {
        html += `<tr>
            <td><strong>${escapeHtml(peer.name || 'Peer')}</strong></td>
            <td><code>${escapeHtml(peer.address || '')}</code></td>
            <td>
                <div style="display:flex; gap:0.25rem;">
                    <button class="peer-sync-btn" onclick="syncWithPeer('${escapeHtml(peer.address || '')}')">Sync</button>
                    <button class="rule-del-btn" onclick="deletePeer(${peer.id})">✕</button>
                </div>
            </td>
        </tr>`;
    });
    html += `</tbody></table>`;
    container.innerHTML = html;
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
        badge.innerHTML = `Tags: ${escapeHtml(selectedTag)} <span onclick="clearTagFilter(); event.stopPropagation();" style="cursor: pointer; margin-left: 6px; font-weight: bold;" title="Clear Tag Filter">✕</span>`;
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

function setSearchModeSilent(mode) {
    searchMode = mode;
    document.querySelectorAll(".mode-btn").forEach(btn => btn.classList.remove("active"));
    const kwBtn = document.getElementById("mode-keyword");
    const semBtn = document.getElementById("mode-semantic");
    if (kwBtn) kwBtn.classList.toggle("active", mode === "keyword");
    if (semBtn) semBtn.classList.toggle("active", mode === "semantic");
    
    const sliderContainer = document.getElementById("similarity-threshold-container");
    if (sliderContainer) {
        sliderContainer.classList.toggle("hidden", mode !== "semantic");
    }
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
    const countBadge = document.getElementById("rules-count-badge");
    if (countBadge) countBadge.innerText = `${rules ? rules.length : 0} Active Rules`;
    if (!container) return;
    if (!rules || rules.length === 0) {
        container.innerHTML = '<span class="rules-empty" style="display: block; padding: 0.75rem; color: var(--text-secondary); font-style: italic;">No automated tagging rules configured.</span>';
        return;
    }
    let html = `
        <table class="high-density-table">
            <thead>
                <tr>
                    <th style="width: 60px;">ID</th>
                    <th>Regex Pattern</th>
                    <th>Target Tag</th>
                    <th style="width: 70px;">Priority</th>
                    <th style="width: 80px;">Status</th>
                    <th style="width: 70px; text-align: right;">Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    rules.forEach(rule => {
        html += `
            <tr>
                <td style="font-family: monospace; color: var(--text-secondary);">#${rule.id}</td>
                <td style="font-family: monospace; color: var(--accent); font-weight: 600;">${escapeHtml(rule.pattern)}</td>
                <td><span class="tag-pill-sidebar">${escapeHtml(rule.tag)}</span></td>
                <td style="color: var(--text-secondary);">${rule.priority || 0}</td>
                <td><span class="status-badge-active">ACTIVE</span></td>
                <td style="text-align: right;">
                    <button onclick="deleteAutoRule(${rule.id})" title="Delete Rule" style="background: rgba(239,68,68,0.15); border: 1px solid var(--danger); color: var(--danger); border-radius: 2px; padding: 2px 6px; cursor: pointer; font-size: 0.7rem;">✕</button>
                </td>
            </tr>
        `;
    });
    html += `</tbody></table>`;
    container.innerHTML = html;
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
        new RegExp(pattern);
        patInput.style.borderColor = "var(--border-color)";
    } catch (e) {
        patInput.style.borderColor = "var(--danger)";
        showToast(`Invalid Regex Pattern: ${e.message}`, "error");
        return;
    }

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
            const countStr = (item.count !== undefined && item.count !== null) ? ` (${item.count})` : "";
            span.innerText = `${item.tag}${countStr}`;
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
        if (container) {
            container.innerHTML = "";
            if (!data.history || data.history.length === 0) {
                container.innerHTML = '<span class="rules-empty">No search query history logged.</span>';
            } else {
                let html = `<table class="high-density-table"><thead><tr><th>Query</th><th>Mode</th></tr></thead><tbody>`;
                data.history.forEach(item => {
                    const queryStr = item.query_string || "All Files";
                    const escapedQuery = escapeHtml(queryStr);
                    const mode = escapeHtml(item.search_mode || "keyword");
                    const rawQuery = escapeHtml(item.query_string || '');
                    html += `<tr style="cursor:pointer;" onclick="const input = document.getElementById('search-input'); if (input) input.value = '${rawQuery}'; setSearchModeSilent('${mode === 'semantic' ? 'semantic' : 'keyword'}'); switchTab('search'); triggerSearch();">
                        <td title="${escapedQuery}"><strong>${escapedQuery}</strong></td>
                        <td><span class="status-badge-active">${mode} (${item.result_count || 0})</span></td>
                    </tr>`;
                });
                html += `</tbody></table>`;
                container.innerHTML = html;
            }
        }

        const recentSearchesList = document.getElementById("recent-searches-list");
        if (recentSearchesList) {
            recentSearchesList.innerHTML = "";
            if (!data.history || data.history.length === 0) {
                recentSearchesList.innerHTML = '<span class="timeline-empty">No recent searches.</span>';
            } else {
                const top5 = data.history.slice(0, 5);
                top5.forEach(item => {
                    const div = document.createElement("div");
                    div.className = "timeline-row";
                    div.style.cursor = "pointer";
                    div.onclick = () => {
                        const input = document.getElementById("search-input");
                        if (input) input.value = item.query_string || "";
                        setSearchModeSilent(item.search_mode === "semantic" ? "semantic" : "keyword");
                        switchTab("search");
                        triggerSearch();
                    };
                    div.innerHTML = `
                        <span style="font-weight: 500;">${escapeHtml(item.query_string || 'All Files')}</span>
                        <strong class="badge" style="font-size: 0.6rem; padding: 0 0.2rem;">${escapeHtml(item.search_mode)} (${item.result_count})</strong>
                    `;
                    recentSearchesList.appendChild(div);
                });
            }
        }
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
        let html = `<table class="high-density-table"><thead><tr><th>Bookmark Name</th><th>Mode</th><th>Action</th></tr></thead><tbody>`;
        data.bookmarks.forEach(item => {
            const cleanQuery = item.query_string ? escapeHtml(item.query_string) : '';
            html += `<tr>
                <td style="cursor:pointer;" onclick="const input = document.getElementById('search-input'); if(input) input.value='${cleanQuery}'; setSearchMode('${item.search_mode === 'semantic' ? 'semantic' : 'keyword'}');" title="Query: ${cleanQuery}"><strong>${escapeHtml(item.name)}</strong></td>
                <td><span class="status-badge-active">${escapeHtml(item.search_mode)}</span></td>
                <td><button class="rule-del-btn" onclick="deleteSearchBookmark(${item.id})">✕</button></td>
            </tr>`;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
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

            currentSearchResults = data.results || [];
            applyResultsSorting();
            fetchSearchHistory();
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

    const fragment = document.createDocumentFragment();
    duplicates.forEach(set => {
        const div = document.createElement("div");
        div.className = "duplicate-group-card";
        
        let filesHtml = set.files.map(file => `
            <div class="duplicate-file-entry" onclick="showPreview('${file.filepath.replace(/\\/g, '\\\\')}')" style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1; min-width: 0; padding-right: 1rem;">
                    <strong>${file.filename}</strong><br/>
                    <small style="color: var(--text-secondary); font-size: 0.75rem; word-break: break-all;">${file.filepath}</small>
                </div>
                <button class="action-btn" onclick="event.stopPropagation(); deleteDuplicateCopy('${file.filepath.replace(/\\/g, '\\\\')}')" style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: var(--text-primary); padding: 0.2rem 0.5rem; font-size: 0.7rem; border-radius: 2px; cursor: pointer; transition: all 0.2s;">Delete Copy</button>
            </div>
        `).join("");

        div.innerHTML = `
            <span class="duplicate-hash">SHA256: ${set.sha256}</span>
            <div class="duplicate-files-list">
                ${filesHtml}
            </div>
        `;
        fragment.appendChild(div);
    });
    list.appendChild(fragment);
}

async function deleteDuplicateCopy(path) {
    if (!confirm(`Are you sure you want to permanently delete this duplicate copy?\n\nPath: ${path}`)) {
        return;
    }
    try {
        const response = await fetch(`/api/file/delete?path=${encodeURIComponent(path)}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `HTTP ${response.status}`);
        }
        alert("Duplicate copy successfully deleted.");
        fetchDuplicates();
        fetchStats(); // Update dashboard counts
    } catch (error) {
        alert(`Failed to delete copy: ${error.message}`);
    }
}

function safeRenderSnippet(snippet) {
    if (!snippet) return "";
    const parts = snippet.split(/(<mark>.*?<\/mark>)/gi);
    return parts.map(part => {
        if (part.toLowerCase().startsWith("<mark>") && part.toLowerCase().endsWith("</mark>")) {
            const inner = part.slice(6, -7);
            return `<mark>${escapeHtml(inner)}</mark>`;
        }
        return escapeHtml(part);
    }).join("");
}

let currentResultsLimit = 100;
let currentActiveResults = [];

function renderResults(results) {
    currentActiveResults = results;
    currentResultsLimit = 100;
    renderResultsPage();
}

function renderResultsPage() {
    const list = document.getElementById("results-list");
    const countBadge = document.getElementById("results-count");
    const results = currentActiveResults;

    list.innerHTML = "";
    countBadge.innerText = `${results.length} found`;
    
    // ponytail: add neon shadow animation triggers to the search results count badge
    if (results.length > 0) {
        countBadge.classList.add("neon-count-glow");
    } else {
        countBadge.classList.remove("neon-count-glow");
    }

    if (results.length === 0) {
        list.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 2rem 1rem; display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
                <img src="/assets/uroboros_empty_state.jpg" alt="Uroboros Empty State" style="width: 100px; height: 100px; border-radius: 50%; border: 1px solid var(--border-color); box-shadow: 0 0 20px rgba(234,224,200,0.15); object-fit: cover;" />
                <div style="font-family: var(--font-outfit); font-size: 0.95rem; font-weight: 600; color: var(--text-primary);">No records matched your search</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Try clearing active scope/filters or re-indexing target directory</div>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem; justify-content: center;">
                    <button onclick="triggerIndexing()" class="settings-btn settings-btn-primary" style="padding: 0.3rem 0.7rem; font-size: 0.75rem;">⚡ Re-Index Target Directory</button>
                    <button onclick="clearTagFilter(); clearFolderScopeFilter(); triggerSearch();" class="settings-btn" style="padding: 0.3rem 0.7rem; font-size: 0.75rem;">🧹 Clear Filters & Scope</button>
                    <button onclick="switchTab('chat');" class="settings-btn" style="padding: 0.3rem 0.7rem; font-size: 0.75rem;">💡 Ask AI Assistant</button>
                </div>
            </div>
        `;
        return;
    }

    const bulkBtn = document.getElementById("bulk-delete-btn");
    bulkBtn.classList.add("hidden");

    const slice = results.slice(0, currentResultsLimit);
    const fragment = document.createDocumentFragment();
    slice.forEach(file => {
        const div = document.createElement("div");
        div.className = "result-item";
        const ext = file.filename ? file.filename.split('.').pop().toLowerCase() : '';
        const category = getFileCategory(ext);
        div.setAttribute("data-ext", ext);
        div.setAttribute("data-category", category);
        
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
        const snippetHtml = file.snippet ? `<div class="result-snippet">${safeRenderSnippet(file.snippet)}</div>` : '';

        div.innerHTML = `
            <div class="result-info-header" style="align-items: center;">
                <input type="checkbox" class="bulk-select-chk" data-path="${encodeURIComponent(file.filepath)}" style="margin-right: 0.75rem; width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer;" />
                <div class="result-info" style="flex: 1;">
                    <span class="result-title"><span class="result-category-badge">${getFileIconSvg(ext, 14)} <span style="text-transform: uppercase;">${ext || 'FILE'}</span></span> ${escapeHtml(file.filename)} ${scoreBadge}</span>
                    <span class="result-path">${escapeHtml(file.filepath)}</span>
                    <div class="result-meta">
                        <span>${formatBytes(file.file_size)}</span>
                        <span>•</span>
                        <span>${file.mime_type || 'file'}</span>
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

        fragment.appendChild(div);
    });
    list.appendChild(fragment);

    if (results.length > currentResultsLimit) {
        const loadMoreBtn = document.createElement("button");
        loadMoreBtn.className = "settings-btn";
        loadMoreBtn.style.margin = "1rem auto";
        loadMoreBtn.style.display = "block";
        loadMoreBtn.innerText = `+ Show Next 100 Matches (${results.length - currentResultsLimit} remaining)`;
        loadMoreBtn.onclick = () => {
            currentResultsLimit += 100;
            renderResultsPage();
        };
        list.appendChild(loadMoreBtn);
    }
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

        // Show/hide video card and player
        const ext = (path.split('.').pop() || '').toLowerCase();
        const videoCard = document.getElementById("preview-video-card");
        const videoPlayer = document.getElementById("video-preview-player");
        const isVideo = ['mp4', 'webm', 'mkv', 'avi', 'mov'].includes(ext);
        if (videoCard && videoPlayer) {
            if (isVideo || data.video_metadata) {
                videoCard.classList.remove("hidden");
                const vFmt = document.getElementById("video-format");
                if (vFmt) vFmt.innerText = ext.toUpperCase();
                videoPlayer.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
            } else {
                videoCard.classList.add("hidden");
                videoPlayer.src = "";
            }
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
        } else if (suffix === 'md' && data.content) {
            previewArea.appendChild(overlay);
            const mdDiv = document.createElement("div");
            mdDiv.className = "markdown-preview";
            mdDiv.style.padding = "1rem";
            mdDiv.style.overflowY = "auto";
            mdDiv.style.maxHeight = "500px";
            mdDiv.innerHTML = renderMarkdown(data.content);
            previewArea.appendChild(mdDiv);
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
        
        const panel = document.getElementById("preview-panel");
        const inspectorOverlay = document.getElementById("inspector-overlay");
        if (panel) {
            panel.classList.remove("hidden");
            panel.classList.add("open");
        }
        if (inspectorOverlay) {
            inspectorOverlay.classList.remove("hidden");
            inspectorOverlay.classList.add("active");
        }
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

async function openFileNatively() {
    if (!currentPreviewPath) return;
    try {
        const response = await fetch('/api/file/open', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filepath: currentPreviewPath })
        });
        if (!response.ok) {
            const data = await response.json();
            showToast("Failed to open file: " + (data.detail || response.statusText), "error");
        } else {
            showToast("Opening file externally...", "info");
        }
    } catch (e) {
        showToast("Error opening file: " + e.message, "error");
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
            showToast(`File renamed to "${newName.trim()}"`, "success");
            fetchStats();
            fetchGlobalTags();
            fetchDirectoryTree();
            triggerSearch();
            showPreview(result.new_filepath);
        } else {
            showToast(`Rename failed: ${result.detail}`, "error");
        }
    } catch (error) {
        showToast(`Failed to rename file: ${error.message}`, "error");
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
            showToast("File deleted successfully", "success");
            closePreview();
            fetchStats();
            fetchGlobalTags();
            fetchDirectoryTree();
            triggerSearch();
        } else {
            const err = await response.json();
            showToast(`Delete failed: ${err.detail}`, "error");
        }
    } catch (error) {
        showToast(`Delete failed: ${error.message}`, "error");
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
            showToast(`Added tag "${tag}"`, "success");
            showPreview(currentPreviewPath);
            fetchGlobalTags();
        } else {
            const err = await response.json();
            showToast(`Failed to add tag: ${err.detail}`, "error");
        }
    } catch (error) {
        showToast(`Failed to add tag: ${error.message}`, "error");
    }
}

function renderFileTags(tags) {
    const list = document.getElementById("file-tags-list");
    list.innerHTML = "";
    if (tags && tags.length > 0) {
        const fragment = document.createDocumentFragment();
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
            fragment.appendChild(span);
        });
        list.appendChild(fragment);
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
    const panel = document.getElementById("preview-panel");
    const overlay = document.getElementById("inspector-overlay");
    if (panel) {
        panel.classList.remove("open");
        panel.classList.add("hidden");
    }
    if (overlay) {
        overlay.classList.remove("active");
        overlay.classList.add("hidden");
    }
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
function fetchSnapshotsList() {
    return fetchSnapshots();
}

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
    if (!container) return;
    container.innerHTML = "";
    if (!snapshots || snapshots.length === 0) {
        container.innerHTML = '<span class="rules-empty">No snapshots captured.</span>';
        return;
    }
    let html = `<table class="high-density-table"><thead><tr><th>Snapshot Date</th><th>Action</th></tr></thead><tbody>`;
    snapshots.forEach(ts => {
        const dateStr = new Date(ts * 1000).toLocaleString();
        html += `<tr>
            <td><strong>${dateStr}</strong></td>
            <td>
                <div style="display:flex; gap:0.25rem;">
                    <button class="peer-sync-btn" onclick="restoreSnapshot(${ts})" style="background: rgba(99, 102, 241, 0.15); border-color: var(--accent); color: var(--accent);">Rollback</button>
                    <button class="rule-del-btn" onclick="deleteSnapshot(${ts})">✕</button>
                </div>
            </td>
        </tr>`;
    });
    html += `</tbody></table>`;
    container.innerHTML = html;
}

async function createSnapshot() {
    try {
        const response = await fetch("/api/snapshots", { method: "POST" });
        if (response.ok) {
            showToast("DB Snapshot successfully captured!", "success");
            fetchSnapshots();
        } else {
            const err = await response.json();
            showToast(`Snapshot capture failed: ${err.detail || 'Unknown error'}`, "error");
        }
    } catch (e) {
        showToast(`Snapshot capture failed: ${e.message}`, "error");
    }
}

async function restoreSnapshot(timestamp) {
    const confirmed = confirm("Are you sure you want to restore this snapshot? All current database data will rollback to this point.");
    if (!confirmed) return;
    try {
        const response = await fetch(`/api/snapshots/restore?timestamp=${timestamp}`, { method: "POST" });
        if (response.ok) {
            showToast("Database rollback successful!", "success");
            fetchStats();
            fetchGlobalTags();
            fetchDirectoryTree();
            triggerSearch();
        } else {
            const err = await response.json();
            showToast(`Restore failed: ${err.detail || 'Unknown error'}`, "error");
        }
    } catch (e) {
        showToast(`Restore failed: ${e.message}`, "error");
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
            const btn = document.getElementById("record-memo-btn");
            if (btn) {
                btn.innerText = "● Record Voice Memo";
                btn.style.background = "var(--danger)";
            }
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
        showToast("Microphone access denied or device not found. Check browser permissions.", "warning");
        if (lbl) lbl.innerText = "Mic Access Denied";
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
    
    let needsRedraw = true;
    let forcesActive = true;
    window.setGraphNeedsRedraw = () => { needsRedraw = true; forcesActive = true; };

    // Fast O(1) node map & pre-resolve link endpoints
    const nodeMap = new Map();
    nodes.forEach(n => nodeMap.set(n.id, n));
    links.forEach(l => {
        l.sourceNode = nodeMap.get(l.source);
        l.targetNode = nodeMap.get(l.target);
    });

    // Fast O(1) adjacency map: nodeId -> Set of connected node IDs
    const adjacencyMap = new Map();
    nodes.forEach(n => adjacencyMap.set(n.id, new Set()));
    links.forEach(l => {
        if (l.sourceNode && l.targetNode) {
            adjacencyMap.get(l.source).add(l.target);
            adjacencyMap.get(l.target).add(l.source);
        }
    });

    // Spatial Grid Partitioning (Scell = 150px)
    const CELL_SIZE = 150;
    const spatialGrid = new Map();

    function rebuildSpatialGrid() {
        spatialGrid.clear();
        for (let i = 0; i < nodes.length; i++) {
            const n = nodes[i];
            const cx = Math.floor(n.x / CELL_SIZE);
            const cy = Math.floor(n.y / CELL_SIZE);
            const key = `${cx},${cy}`;
            let bucket = spatialGrid.get(key);
            if (!bucket) {
                bucket = [];
                spatialGrid.set(key, bucket);
            }
            bucket.push(n);
        }
    }
    window.rebuildSpatialGrid = rebuildSpatialGrid;

    // Spatial O(1) Mouse/Touch Hit Tester using 3x3 Grid Buckets
    function findNodeAtSpatial(mx, my, maxDist = 25) {
        const gx = (mx - offsetX) / zoomScale;
        const gy = (my - offsetY) / zoomScale;
        const cx = Math.floor(gx / CELL_SIZE);
        const cy = Math.floor(gy / CELL_SIZE);
        
        let nearestNode = null;
        let minDist = maxDist;

        for (let dx = -1; dx <= 1; dx++) {
            for (let dy = -1; dy <= 1; dy++) {
                const bucket = spatialGrid.get(`${cx + dx},${cy + dy}`);
                if (bucket) {
                    for (let i = 0; i < bucket.length; i++) {
                        const n = bucket[i];
                        const sx = n.x * zoomScale + offsetX;
                        const sy = n.y * zoomScale + offsetY;
                        const dist = Math.sqrt((sx - mx) * (sx - mx) + (sy - my) * (sy - my));
                        if (dist < minDist) {
                            minDist = dist;
                            nearestNode = n;
                        }
                    }
                }
            }
        }
        return nearestNode;
    }

    // Smooth canvas resizing via ResizeObserver while preserving aspect ratio
    if (window.graphResizeObserver) {
        window.graphResizeObserver.disconnect();
    }
    if (canvas.parentElement && typeof ResizeObserver !== "undefined") {
        window.graphResizeObserver = new ResizeObserver(debounce(entries => {
            for (let entry of entries) {
                const rect = entry.contentRect;
                if (rect.width > 0) {
                    const targetWidth = Math.floor(rect.width);
                    const targetHeight = Math.max(300, Math.floor(targetWidth * (400 / 600)));
                    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
                        canvas.width = targetWidth;
                        canvas.height = targetHeight;
                        applyLayoutPreset();
                        needsRedraw = true;
                        forcesActive = true;
                    }
                }
            }
        }, 150));
        window.graphResizeObserver.observe(canvas.parentElement);
    }
    
    let graphLayoutPreset = document.getElementById("graph-layout-preset") ? (document.getElementById("graph-layout-preset").value || "force") : "force";
    let activeGraphCategory = "all";
    let graphFilterQuery = "";

    window.filterGraphNodes = (val) => {
        graphFilterQuery = (val || "").trim().toLowerCase();
        needsRedraw = true;
        forcesActive = true;
    };

    window.filterGraphCategory = (cat) => {
        activeGraphCategory = cat || "all";
        needsRedraw = true;
        forcesActive = true;
    };
    
    window.changeGraphLayoutPreset = () => {
        const el = document.getElementById("graph-layout-preset");
        if (el) {
            graphLayoutPreset = el.value;
            applyLayoutPreset();
            needsRedraw = true;
            forcesActive = true;
        }
    };

    function applyLayoutPreset() {
        if (graphLayoutPreset === "circular") {
            const radius = Math.min(canvas.width, canvas.height) * 0.35;
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            nodes.forEach((n, idx) => {
                const angle = (idx / nodes.length) * 2 * Math.PI;
                n.targetX = cx + radius * Math.cos(angle);
                n.targetY = cy + radius * Math.sin(angle);
                if (typeof n.x === "undefined") { n.x = cx; n.y = cy; }
                n.vx = 0; n.vy = 0;
            });
        } else if (graphLayoutPreset === "grid") {
            const cols = Math.ceil(Math.sqrt(nodes.length));
            const spacingX = canvas.width / (cols + 1);
            const spacingY = canvas.height / (Math.ceil(nodes.length / cols) + 1);
            nodes.forEach((n, idx) => {
                const r = Math.floor(idx / cols);
                const c = idx % cols;
                n.targetX = spacingX * (c + 1);
                n.targetY = spacingY * (r + 1);
                if (typeof n.x === "undefined") { n.x = n.targetX; n.y = n.targetY; }
                n.vx = 0; n.vy = 0;
            });
        } else if (graphLayoutPreset === "tree") {
            const levels = 4;
            const levelHeight = canvas.height / (levels + 1);
            nodes.forEach((n, idx) => {
                const lvl = idx % levels;
                const siblingsCount = Math.ceil(nodes.length / levels);
                const posInLvl = Math.floor(idx / levels);
                const spacingX = canvas.width / (siblingsCount + 1);
                n.targetX = spacingX * (posInLvl + 1);
                n.targetY = levelHeight * (lvl + 1);
                if (typeof n.x === "undefined") { n.x = n.targetX; n.y = n.targetY; }
                n.vx = 0; n.vy = 0;
            });
        } else {
            // Assign target positions for force layout
            nodes.forEach(n => {
                if (typeof n.x === "undefined") {
                    n.x = Math.random() * (canvas.width - 40) + 20;
                    n.y = Math.random() * (canvas.height - 40) + 20;
                }
                n.targetX = n.x;
                n.targetY = n.y;
                n.vx = 0; n.vy = 0;
            });
        }
    }
    
    // Initial position assignment
    nodes.forEach(n => {
        if (typeof n.x === "undefined") {
            n.x = Math.random() * (canvas.width - 40) + 20;
            n.y = Math.random() * (canvas.height - 40) + 20;
        }
        n.vx = 0;
        n.vy = 0;
    });
    applyLayoutPreset();
    rebuildSpatialGrid();
    
    let draggedNode = null;
    let hoveredNodeId = null;
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
        needsRedraw = true;
        forcesActive = true;
    };
    window.resetConceptGraphView = () => {
        zoomScale = 1.0;
        offsetX = 0;
        offsetY = 0;
        needsRedraw = true;
        forcesActive = true;
    };
    
    // Interactive mouse gesture handlers with spatial O(1) hit testing
    canvas.onmousedown = (e) => {
        needsRedraw = true;
        forcesActive = true;
        const rect = canvas.getBoundingClientRect();
        const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
        const my = (e.clientY - rect.top) * (canvas.height / rect.height);
        
        const nearestNode = findNodeAtSpatial(mx, my, 25);
        
        if (nearestNode) {
            draggedNode = nearestNode;
            selectedNodeId = nearestNode.id;
            if (nearestNode.filepath) {
                showPreview(nearestNode.filepath);
            }
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
            draggedNode.targetX = draggedNode.x;
            draggedNode.targetY = draggedNode.y;
            draggedNode.vx = 0;
            draggedNode.vy = 0;
            needsRedraw = true;
            forcesActive = true;
        } else if (isPanning) {
            offsetX = mx - panStartX;
            offsetY = my - panStartY;
            needsRedraw = true;
        } else {
            const foundHover = findNodeAtSpatial(mx, my, 20);
            const newHover = foundHover ? foundHover.id : null;
            if (newHover !== hoveredNodeId) {
                hoveredNodeId = newHover;
                needsRedraw = true;
            }
            canvas.style.cursor = foundHover ? "pointer" : "default";
        }
    };

    canvas.onmouseup = () => {
        draggedNode = null;
        isPanning = false;
        needsRedraw = true;
    };

    canvas.onmouseleave = () => {
        draggedNode = null;
        isPanning = false;
        if (hoveredNodeId !== null) {
            hoveredNodeId = null;
            needsRedraw = true;
        }
    };

    const handleZoomWheel = debounce((e) => {
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
        
        offsetX = mx - gx * zoomScale;
        offsetY = my - gy * zoomScale;
        needsRedraw = true;
        forcesActive = true;
    }, 150);

    canvas.onwheel = (e) => {
        e.preventDefault();
        handleZoomWheel(e);
    };

    // Touch gesture handlers with spatial O(1) hit testing
    canvas.ontouchstart = (e) => {
        needsRedraw = true;
        forcesActive = true;
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            const mx = (touch.clientX - rect.left) * (canvas.width / rect.width);
            const my = (touch.clientY - rect.top) * (canvas.height / rect.height);

            const nearestNode = findNodeAtSpatial(mx, my, 25);

            if (nearestNode) {
                draggedNode = nearestNode;
                selectedNodeId = nearestNode.id;
                if (nearestNode.filepath) {
                    showPreview(nearestNode.filepath);
                }
            } else {
                selectedNodeId = null;
                isPanning = true;
                panStartX = mx - offsetX;
                panStartY = my - offsetY;
            }
        }
    };

    canvas.ontouchmove = (e) => {
        if (e.touches.length === 1) {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            const mx = (touch.clientX - rect.left) * (canvas.width / rect.width);
            const my = (touch.clientY - rect.top) * (canvas.height / rect.height);

            if (draggedNode) {
                draggedNode.x = (mx - offsetX) / zoomScale;
                draggedNode.y = (my - offsetY) / zoomScale;
                draggedNode.targetX = draggedNode.x;
                draggedNode.targetY = draggedNode.y;
                needsRedraw = true;
                forcesActive = true;
            } else if (isPanning) {
                offsetX = mx - panStartX;
                offsetY = my - panStartY;
                needsRedraw = true;
            }
        }
    };

    canvas.ontouchend = () => {
        draggedNode = null;
        isPanning = false;
        needsRedraw = true;
    };
    
    function updatePhysics() {
        if (!forcesActive) return;

        // Dynamic node layout transition towards targetX, targetY for non-force presets
        if (graphLayoutPreset !== "force") {
            let moved = false;
            nodes.forEach(n => {
                if (typeof n.targetX !== "undefined") {
                    const dx = n.targetX - n.x;
                    const dy = n.targetY - n.y;
                    if (Math.abs(dx) > 0.05 || Math.abs(dy) > 0.05) {
                        moved = true;
                    }
                    n.x += dx * 0.15;
                    n.y += dy * 0.15;
                }
            });
            if (moved) needsRedraw = true;
            else forcesActive = false;
            rebuildSpatialGrid();
            return;
        }

        rebuildSpatialGrid();
        
        // Centering forces focus selected node
        if (selectedNodeId) {
            const centerNode = nodeMap.get(selectedNodeId);
            if (centerNode) {
                const centerTargetX = (canvas.width / 2 - offsetX) / zoomScale;
                const centerTargetY = (canvas.height / 2 - offsetY) / zoomScale;
                const dx = centerTargetX - centerNode.x;
                const dy = centerTargetY - centerNode.y;
                if (Math.abs(dx) > 0.05 || Math.abs(dy) > 0.05) {
                    needsRedraw = true;
                }
                centerNode.x += dx * 0.1;
                centerNode.y += dy * 0.1;
            }
        }

        // Repulsion physics via 3x3 spatial grid neighborhood (O(N) physics)
        for (let i = 0; i < nodes.length; i++) {
            const ni = nodes[i];
            const cx = Math.floor(ni.x / CELL_SIZE);
            const cy = Math.floor(ni.y / CELL_SIZE);

            for (let dx = -1; dx <= 1; dx++) {
                for (let dy = -1; dy <= 1; dy++) {
                    const bucket = spatialGrid.get(`${cx + dx},${cy + dy}`);
                    if (bucket) {
                        for (let k = 0; k < bucket.length; k++) {
                            const nj = bucket[k];
                            if (nj.id === ni.id) continue;
                            const diffX = nj.x - ni.x;
                            const diffY = nj.y - ni.y;
                            const dist = Math.sqrt(diffX * diffX + diffY * diffY) || 1;
                            if (dist < 150) {
                                const force = (150 - dist) * 0.025;
                                ni.vx -= (diffX / dist) * force;
                                ni.vy -= (diffY / dist) * force;
                            }
                        }
                    }
                }
            }
        }
        
        // Attraction along links using pre-resolved endpoints
        links.forEach(l => {
            const sourceNode = l.sourceNode;
            const targetNode = l.targetNode;
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
        
        // Apply friction, boundary bounds, and compute total kinetic energy
        let totalKineticEnergy = 0;
        nodes.forEach(n => {
            n.x += n.vx;
            n.y += n.vy;
            n.vx *= 0.85;
            n.vy *= 0.85;
            totalKineticEnergy += (n.vx * n.vx + n.vy * n.vy);
            
            if (n.x < 20) n.x = 20;
            if (n.x > canvas.width - 20) n.x = canvas.width - 20;
            if (n.y < 20) n.y = 20;
            if (n.y > canvas.height - 20) n.y = canvas.height - 20;
        });

        // Kinetic Energy Cooling Threshold cutoff (E < 0.05)
        if (totalKineticEnergy < 0.05 && !draggedNode && !isPanning) {
            forcesActive = false;
            nodes.forEach(n => { n.vx = 0; n.vy = 0; });
        } else {
            needsRedraw = true;
        }
    }
    
    function draw() {
        if (draggedNode || isPanning) {
            needsRedraw = true;
        }

        // Interpolate smooth scale transition check
        nodes.forEach(n => {
            if (typeof n.currentScale === "undefined") n.currentScale = 1.0;
            const isHovered = (n.id === hoveredNodeId);
            const isSelected = (n.id === selectedNodeId);
            const targetScale = isSelected ? 1.5 : (isHovered ? 1.35 : 1.0);
            if (Math.abs(targetScale - n.currentScale) > 0.005) {
                needsRedraw = true;
            }
        });

        if (!needsRedraw) {
            graphAnimFrame = requestAnimationFrame(draw);
            return;
        }

        needsRedraw = false;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(offsetX, offsetY);
        ctx.scale(zoomScale, zoomScale);

        // Viewport Bounding Box Culling (with 60px margin)
        const margin = 60;
        const vXmin = (-offsetX / zoomScale) - margin;
        const vXmax = ((canvas.width - offsetX) / zoomScale) + margin;
        const vYmin = (-offsetY / zoomScale) - margin;
        const vYmax = ((canvas.height - offsetY) / zoomScale) + margin;

        const activeNodeId = selectedNodeId || hoveredNodeId;
        const activeConnectedSet = activeNodeId ? (adjacencyMap.get(activeNodeId) || new Set()) : null;
        
        // Category clustering hull backgrounds
        const groups = {
            code: { nodes: [], color: "rgba(99, 102, 241, 0.06)", border: "rgba(99, 102, 241, 0.15)" },
            spreadsheets: { nodes: [], color: "rgba(16, 185, 129, 0.06)", border: "rgba(16, 185, 129, 0.15)" },
            images: { nodes: [], color: "rgba(239, 68, 68, 0.06)", border: "rgba(239, 68, 68, 0.15)" },
            audio: { nodes: [], color: "rgba(244, 114, 182, 0.06)", border: "rgba(244, 114, 182, 0.15)" },
            video: { nodes: [], color: "rgba(192, 132, 252, 0.06)", border: "rgba(192, 132, 252, 0.15)" },
            documents: { nodes: [], color: "rgba(245, 158, 11, 0.06)", border: "rgba(245, 158, 11, 0.15)" }
        };
        
        nodes.forEach(n => {
            if (n.filename) {
                const ext = n.filename.split('.').pop().toLowerCase();
                const cat = getFileCategory(ext);
                if (cat === 'code') {
                    groups.code.nodes.push(n);
                } else if (cat === 'spreadsheet') {
                    groups.spreadsheets.nodes.push(n);
                } else if (cat === 'image') {
                    groups.images.nodes.push(n);
                } else if (cat === 'audio') {
                    groups.audio.nodes.push(n);
                } else if (cat === 'video') {
                    groups.video.nodes.push(n);
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

                if (cx + maxD + 25 >= vXmin && cx - maxD - 25 <= vXmax && cy + maxD + 25 >= vYmin && cy - maxD - 25 <= vYmax) {
                    ctx.fillStyle = grp.color;
                    ctx.strokeStyle = grp.border;
                    ctx.lineWidth = 1.0;
                    ctx.beginPath();
                    ctx.arc(cx, cy, maxD + 25, 0, 2 * Math.PI);
                    ctx.fill();
                    ctx.stroke();
                }
            }
        }
        
        // Draw Links with Viewport Culling & Visual Styling for wikilink_to / shared_tag_cluster
        links.forEach(l => {
            const s = l.sourceNode;
            const t = l.targetNode;
            if (!s || !t) return;

            // Viewport culling check for link segment
            const inViewport = (s.x >= vXmin && s.x <= vXmax && s.y >= vYmin && s.y <= vYmax) ||
                               (t.x >= vXmin && t.x <= vXmax && t.y >= vYmin && t.y <= vYmax);
            if (!inViewport) return;

            const isLinkConnected = activeNodeId && (l.source === activeNodeId || l.target === activeNodeId);
            const linkType = l.link_type || l.type || 'tagged_with';

            ctx.save();
            if (linkType === 'wikilink_to') {
                // Dashed purple glow
                ctx.setLineDash([6, 4]);
                if (isLinkConnected) {
                    ctx.strokeStyle = "rgba(168, 85, 247, 1.0)";
                    ctx.shadowColor = "rgba(168, 85, 247, 0.9)";
                    ctx.shadowBlur = 10;
                    ctx.lineWidth = 3.0;
                } else {
                    ctx.strokeStyle = "rgba(168, 85, 247, 0.75)";
                    ctx.lineWidth = 2.0;
                }
            } else if (linkType === 'shared_tag_cluster') {
                // Dotted amber
                ctx.setLineDash([2, 3]);
                if (isLinkConnected) {
                    ctx.strokeStyle = "rgba(245, 158, 11, 0.9)";
                    ctx.shadowColor = "#f59e0b";
                    ctx.shadowBlur = 12;
                    ctx.lineWidth = 2.5;
                } else if (activeNodeId) {
                    ctx.strokeStyle = "rgba(245, 158, 11, 0.05)";
                    ctx.lineWidth = 1.0;
                } else {
                    ctx.strokeStyle = "rgba(245, 158, 11, 0.15)";
                    ctx.lineWidth = 1.0;
                }
            } else {
                // Standard tagged_with edge
                ctx.setLineDash([]);
                if (activeNodeId && !isLinkConnected) {
                    ctx.strokeStyle = "rgba(63, 63, 70, 0.08)";
                    ctx.lineWidth = 1.0;
                } else {
                    ctx.strokeStyle = "rgba(99, 102, 241, 0.4)";
                    ctx.lineWidth = 1.5;
                }
            }

            ctx.beginPath();
            ctx.moveTo(s.x, s.y);
            ctx.lineTo(t.x, t.y);
            ctx.stroke();
            ctx.restore();
        });
        
        // Draw Nodes with Viewport Culling, smooth scale, hover glow, and shadow transitions
        nodes.forEach(n => {
            // Viewport Bounding Box Culling Guard
            if (n.x < vXmin || n.x > vXmax || n.y < vYmin || n.y > vYmax) return;

            let color = "var(--accent)"; // Default
            const isLightMode = document.body.classList.contains("light-theme");
            let ext = n.filename ? n.filename.split('.').pop().toLowerCase() : '';
            let cat = getFileCategory(ext);

            color = isLightMode ? "#78350f" : "#fcd34d";
            if (cat === 'code') {
                color = isLightMode ? "#312e81" : "#a5b4fc";
            } else if (cat === 'spreadsheet') {
                color = isLightMode ? "#064e3b" : "#6ee7b7";
            } else if (cat === 'image') {
                color = isLightMode ? "#7f1d1d" : "#fca5a5";
            } else if (cat === 'audio') {
                color = isLightMode ? "#581c87" : "#c084fc";
            } else if (cat === 'video') {
                color = isLightMode ? "#0c4a6e" : "#38bdf8";
            }

            let isCategoryMatch = (activeGraphCategory === "all" || cat === activeGraphCategory);
            let isQueryMatch = (!graphFilterQuery || (n.label && n.label.toLowerCase().includes(graphFilterQuery)));
            let isFilterDimmed = (!isCategoryMatch || !isQueryMatch);
            
            let isConnected = (n.id === selectedNodeId || n.id === hoveredNodeId);
            if (activeNodeId && !isConnected && activeConnectedSet) {
                isConnected = activeConnectedSet.has(n.id);
            }
            
            const isHovered = (n.id === hoveredNodeId);
            const isSelected = (n.id === selectedNodeId);

            // Interpolate smooth scale transition
            if (typeof n.currentScale === "undefined") n.currentScale = 1.0;
            const targetScale = isSelected ? 1.5 : (isHovered ? 1.35 : 1.0);
            n.currentScale += (targetScale - n.currentScale) * 0.2;
            
            ctx.save();
            ctx.fillStyle = color;
            ctx.globalAlpha = isFilterDimmed ? 0.1 : ((activeNodeId && !isConnected) ? 0.2 : 1.0);

            // Hover glow and shadow transitions
            if (isHovered || isSelected) {
                ctx.shadowColor = color;
                ctx.shadowBlur = isSelected ? 22 : 14;
            }

            ctx.beginPath();
            const baseRadius = isSelected ? 12 : 8;
            const radius = baseRadius * n.currentScale;
            ctx.arc(n.x, n.y, radius, 0, 2 * Math.PI);
            ctx.fill();
            ctx.restore();

            // Node Glyph Symbol Rendering inside node circle
            if (radius >= 6 && !isFilterDimmed) {
                const categoryGlyphs = {
                    code: '</>',
                    spreadsheet: '⊞',
                    image: '🖼',
                    doc: '📄',
                    audio: '🎵',
                    video: '🎬'
                };
                ctx.save();
                ctx.fillStyle = isLightMode ? '#ffffff' : '#121211';
                ctx.font = `bold ${Math.max(7, Math.floor(radius * 0.65))}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.globalAlpha = isFilterDimmed ? 0.15 : 0.95;
                ctx.fillText(categoryGlyphs[cat] || '📄', n.x, n.y);
                ctx.restore();
            }

            // Outer ring on hover/selected
            if (isHovered || isSelected) {
                ctx.save();
                ctx.strokeStyle = color;
                ctx.lineWidth = isSelected ? 2.5 : 1.5;
                ctx.globalAlpha = isSelected ? 0.9 : 0.6;
                ctx.beginPath();
                ctx.arc(n.x, n.y, radius + 4, 0, 2 * Math.PI);
                ctx.stroke();
                ctx.restore();
            }
            
            // Search match highlight border
            const qInput = document.getElementById("search-input");
            const qVal = qInput ? qInput.value.trim().toLowerCase() : "";
            if (qVal && n.label && n.label.toLowerCase().includes(qVal)) {
                ctx.save();
                ctx.strokeStyle = "#f59e0b";
                ctx.lineWidth = 3.0;
                ctx.beginPath();
                ctx.arc(n.x, n.y, radius + 2, 0, 2 * Math.PI);
                ctx.stroke();
                ctx.restore();
            }
            
            // Label with resolved hex fill and stroke halo rendering
            const isLight = document.body.classList.contains("light-theme");
            const textHex = isLight ? "#181A1E" : "#F4F0E6";
            const haloHex = isLight ? "#FCFBF7" : "#121211";
            
            ctx.save();
            ctx.font = (isSelected || isHovered) ? "bold 11px Inter, sans-serif" : "10px Inter, sans-serif";
            ctx.strokeStyle = haloHex;
            ctx.lineWidth = 3;
            ctx.lineJoin = "round";
            ctx.strokeText(n.label, n.x + (radius + 4), n.y + 4);
            ctx.fillStyle = textHex;
            ctx.fillText(n.label, n.x + (radius + 4), n.y + 4);
            ctx.restore();
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
        if (!container) return;
        container.innerHTML = "";
        if (!data.synonyms || data.synonyms.length === 0) {
            container.innerHTML = '<span class="rules-empty">No synonyms configured.</span>';
            return;
        }
        let html = `<table class="high-density-table"><thead><tr><th>Word</th><th>Substitutes</th></tr></thead><tbody>`;
        data.synonyms.forEach(item => {
            html += `<tr><td><strong>${escapeHtml(item.word)}</strong></td><td>${escapeHtml(item.substitutes)}</td></tr>`;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
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
            showToast(`Periodic backup scheduled every ${secs}s`, "success");
        } else {
            const err = await response.json();
            showToast(`Backup scheduling failed: ${err.detail || 'Unknown error'}`, "error");
        }
    } catch (e) {
        showToast(`Backup scheduling failed: ${e.message}`, "error");
    }
}

// Hook list loading into DOMContentLoaded checks
document.addEventListener("DOMContentLoaded", () => {
    fetchSynonymsList();
});

// client-side LLM runner chat engine (Milestone 3)
let activeSessionId = null;
let chatSessionsList = [];
let chatHistory = [];

function handleChatKeyDown(e) {
    if (e.key === "Enter") {
        sendChatMessage();
    }
}

function sendPromptChip(text) {
    const input = document.getElementById("chat-input");
    if (!input) return;
    input.value = text;
    sendChatMessage();
}

function fetchChatSessions() {
    return fetch("/api/chat/sessions")
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            return response.json();
        })
        .then(sessions => {
            chatSessionsList = Array.isArray(sessions) ? sessions : [];
            renderSessionList();
            if (chatSessionsList.length > 0) {
                if (!activeSessionId || !chatSessionsList.some(s => s.id === activeSessionId)) {
                    switchSession(chatSessionsList[0].id);
                }
            } else {
                createNewSession("New Session");
            }
            return chatSessionsList;
        })
        .catch(err => {
            console.error("Error fetching chat sessions:", err);
        });
}

function renderSessionList(filterQuery = "") {
    const container = document.getElementById("session-list");
    if (!container) return;

    container.innerHTML = "";
    const q = (filterQuery || "").toLowerCase().trim();

    const filtered = chatSessionsList.filter(s => {
        if (!q) return true;
        const titleMatch = (s.title || "").toLowerCase().includes(q);
        const modelMatch = (s.model_path || "").toLowerCase().includes(q);
        return titleMatch || modelMatch;
    });

    if (filtered.length === 0) {
        const emptyEl = document.createElement("div");
        emptyEl.style.padding = "0.75rem 0.5rem";
        emptyEl.style.fontSize = "0.75rem";
        emptyEl.style.color = "var(--text-secondary)";
        emptyEl.style.textAlign = "center";
        emptyEl.innerText = q ? "No matching sessions" : "No sessions yet";
        container.appendChild(emptyEl);
        return;
    }

    const fragment = document.createDocumentFragment();
    filtered.forEach(session => {
        const item = document.createElement("div");
        item.className = `session-item${session.id === activeSessionId ? " active" : ""}`;
        item.onclick = () => switchSession(session.id);

        const info = document.createElement("div");
        info.className = "session-item-info";

        const title = document.createElement("span");
        title.className = "session-item-title";
        title.innerText = session.title || "Untitled Session";
        title.title = session.title || "Untitled Session";

        const time = document.createElement("span");
        time.className = "session-item-time";
        const dateStr = session.updated_at || session.created_at || "";
        if (dateStr) {
            try {
                const d = new Date(dateStr);
                const pad = (n) => n.toString().padStart(2, '0');
                time.innerText = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
            } catch (e) {
                time.innerText = "";
            }
        } else {
            time.innerText = "";
        }

        info.appendChild(title);
        info.appendChild(time);

        const delBtn = document.createElement("button");
        delBtn.className = "delete-session-btn";
        delBtn.innerHTML = "✕";
        delBtn.title = "Delete Session";
        delBtn.onclick = (e) => deleteSession(e, session.id);

        item.appendChild(info);
        item.appendChild(delBtn);
        fragment.appendChild(item);
    });

    container.appendChild(fragment);
}

function createNewSession(title) {
    const modelPathEl = document.getElementById("gguf-model-path");
    const tempEl = document.getElementById("gguf-temperature");
    const ctxEl = document.getElementById("gguf-context-window");

    const tempVal = tempEl ? parseFloat(tempEl.value) : NaN;
    const temperature = !isNaN(tempVal) ? tempVal : 0.7;
    const ctxVal = ctxEl ? parseInt(ctxEl.value, 10) : NaN;
    const context_window = !isNaN(ctxVal) ? ctxVal : 4096;

    const payload = {
        title: title || "New Session",
        model_path: modelPathEl ? modelPathEl.value.trim() : "models/tinyllama-1.1b-chat.Q4_K_M.gguf",
        temperature: temperature,
        context_window: context_window
    };

    return fetch("/api/chat/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
    })
    .then(newSession => {
        chatSessionsList.unshift(newSession);
        switchSession(newSession.id);
        return newSession;
    })
    .catch(err => {
        console.error("Error creating session:", err);
    });
}

function switchSession(sessionId) {
    if (!sessionId) return;
    activeSessionId = sessionId;
    chatHistory = [];

    renderSessionList(document.getElementById("session-search-input")?.value || "");

    fetch(`/api/chat/sessions/${sessionId}`)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return res.json();
        })
        .then(sessionData => {
            const modelPathEl = document.getElementById("gguf-model-path");
            const tempEl = document.getElementById("gguf-temperature");
            const tempValEl = document.getElementById("gguf-temp-val");
            const ctxEl = document.getElementById("gguf-context-window");

            if (sessionData.model_path && modelPathEl) modelPathEl.value = sessionData.model_path;
            if (sessionData.temperature !== undefined && tempEl) {
                tempEl.value = sessionData.temperature;
                if (tempValEl) tempValEl.innerText = sessionData.temperature;
            }
            if (sessionData.context_window && ctxEl) ctxEl.value = sessionData.context_window;

            const messagesContainer = document.getElementById("chat-messages");
            if (messagesContainer) {
                messagesContainer.innerHTML = `
                    <div class="chat-message system">
                        <span class="message-sender"><img src="/assets/rag_assistant_avatar.jpg" style="width: 20px; height: 20px; border-radius: 50%; vertical-align: middle; margin-right: 6px; border: 1px solid var(--accent);" alt="Assistant Avatar" /> Uroboros Assistant</span>
                        <span class="message-content">Session active: <strong>${escapeHtml(sessionData.title || "Untitled")}</strong>. Ask me anything!</span>
                        <span class="message-time">18:00</span>
                    </div>
                `;
            }

            const citationContainer = document.getElementById("citation-chips-container");
            if (citationContainer) citationContainer.innerHTML = "";

            if (Array.isArray(sessionData.messages)) {
                sessionData.messages.forEach(msg => {
                    const senderRole = (msg.role === "user") ? "User" : "Assistant";
                    const sources = [...(msg.citations_json || []), ...(msg.web_sources_json || [])];
                    appendChatMessage(senderRole, msg.content, msg.role, sources.length > 0 ? sources : null);
                    chatHistory.push({ role: msg.role, content: msg.content });
                });
            }
        })
        .catch(err => {
            console.error("Error loading session:", err);
        });
}

function deleteSession(e, sessionId) {
    if (e) e.stopPropagation();
    if (!sessionId) return;

    fetch(`/api/chat/sessions/${sessionId}`, { method: "DELETE" })
        .then(res => {
            if (!res.ok && res.status !== 404) throw new Error(`HTTP error ${res.status}`);
            chatSessionsList = chatSessionsList.filter(s => s.id !== sessionId);
            if (activeSessionId === sessionId) {
                if (chatSessionsList.length > 0) {
                    switchSession(chatSessionsList[0].id);
                } else {
                    activeSessionId = null;
                    createNewSession("New Session");
                }
            } else {
                renderSessionList(document.getElementById("session-search-input")?.value || "");
            }
        })
        .catch(err => {
            console.error("Error deleting session:", err);
        });
}

function filterChatSessions(query) {
    renderSessionList(query);
}

function sendChatMessage() {
    const inputEl = document.getElementById("chat-input");
    const sendBtnEl = document.getElementById("chat-send-btn");
    if (!inputEl) return;
    const text = inputEl.value.trim();
    if (!text) return;

    // Clear input
    inputEl.value = "";

    // If no active session, create one first
    if (!activeSessionId) {
        createNewSession(text.substring(0, 30)).then(() => {
            sendChatMessageWithText(text, inputEl, sendBtnEl);
        });
        return;
    }

    sendChatMessageWithText(text, inputEl, sendBtnEl);
}

function sendChatMessageWithText(text, inputEl, sendBtnEl) {
    // Read GGUF controls
    const modelPathEl = document.getElementById("gguf-model-path");
    const tempEl = document.getElementById("gguf-temperature");
    const ctxEl = document.getElementById("gguf-context-window");
    const webToggleEl = document.getElementById("web-search-toggle");

    const modelPath = modelPathEl ? modelPathEl.value.trim() : "models/tinyllama-1.1b-chat.Q4_K_M.gguf";
    const tempVal = tempEl ? parseFloat(tempEl.value) : NaN;
    const temperature = !isNaN(tempVal) ? tempVal : 0.7;
    const ctxVal = ctxEl ? parseInt(ctxEl.value, 10) : NaN;
    const contextWindow = !isNaN(ctxVal) ? ctxVal : 4096;
    const webSearch = webToggleEl ? webToggleEl.checked : false;

    // Append User message
    appendChatMessage("User", text, "user");

    // Disable inputs during generation
    inputEl.disabled = true;
    if (sendBtnEl) sendBtnEl.disabled = true;

    // Show typing indicator
    showTypingIndicator();

    // Clear citations container for new turn
    const citationContainer = document.getElementById("citation-chips-container");
    if (citationContainer) citationContainer.innerHTML = "";

    // Stream response from /api/chat/stream using SSE with lineBuffer
    let assistantMsgEl = null;
    let assistantContentEl = null;
    let accumulatedReply = "";
    let lineBuffer = "";

    const requestPayload = {
        message: text,
        session_id: activeSessionId,
        model_path: modelPath,
        temperature: temperature,
        context_window: contextWindow,
        web_search: webSearch,
        history: chatHistory
    };

    fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestPayload)
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        
        removeTypingIndicator();

        assistantMsgEl = appendChatMessage("Assistant", "", "assistant");
        if (assistantMsgEl) {
            assistantContentEl = assistantMsgEl.querySelector(".message-content");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        function readStream() {
            return reader.read().then(({ done, value }) => {
                if (done) {
                    if (lineBuffer.trim()) {
                        handleSseChunkLine(lineBuffer.trim());
                    }
                    chatHistory.push({ role: "user", content: text });
                    chatHistory.push({ role: "assistant", content: accumulatedReply });
                    return;
                }

                lineBuffer += decoder.decode(value, { stream: true });
                const lines = lineBuffer.split("\n");
                lineBuffer = lines.pop(); // Retain incomplete trailing chunk

                for (const line of lines) {
                    handleSseChunkLine(line);
                }
                return readStream();
            });
        }

        function handleSseChunkLine(line) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith(":")) return;

            if (trimmed.startsWith("data: ")) {
                const payloadStr = trimmed.slice(6).trim();
                if (payloadStr === "[DONE]") return;

                try {
                    const parsed = JSON.parse(payloadStr);

                    // Grounded Citations & Web Sources
                    if (parsed.type === "sources" || parsed.sources || parsed.local_citations || parsed.web_sources) {
                        const localCits = parsed.local_citations || parsed.sources || [];
                        const webCits = parsed.web_sources || [];
                        const combinedSources = [...localCits, ...webCits];

                        if (combinedSources.length > 0) {
                            if (assistantMsgEl) renderSourceChips(combinedSources, assistantMsgEl);
                            renderGlobalCitationChips(combinedSources);
                        }
                    }

                    // Tokens & Live Markdown Output
                    if (parsed.type === "token" && parsed.content) {
                        accumulatedReply += parsed.content;
                        if (assistantContentEl) assistantContentEl.innerHTML = parseChatMarkdown(accumulatedReply);
                        const container = document.getElementById("chat-messages");
                        if (container) container.scrollTop = container.scrollHeight;
                    } else if (parsed.content) {
                        accumulatedReply += parsed.content;
                        if (assistantContentEl) assistantContentEl.innerHTML = parseChatMarkdown(accumulatedReply);
                        const container = document.getElementById("chat-messages");
                        if (container) container.scrollTop = container.scrollHeight;
                    }

                    if (parsed.error) {
                        accumulatedReply += `\n**Error:** ${parsed.error}`;
                        if (assistantContentEl) assistantContentEl.innerHTML = parseChatMarkdown(accumulatedReply);
                    }
                } catch (e) {}
            }
        }

        return readStream();
    })
    .catch(error => {
        console.error("Error in chat stream:", error);
        removeTypingIndicator();
        appendChatMessage("System", `Error: ${error.message}`, "system");
    })
    .finally(() => {
        inputEl.disabled = false;
        if (sendBtnEl) sendBtnEl.disabled = false;
        inputEl.focus();
    });
}

function parseChatMarkdown(text) {
    if (!text) return "";
    
    // Escape HTML to prevent XSS
    let html = escapeHtml(text);
    
    // Parse multi-line code blocks with copy wrapper
    html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
        return `<div class="chat-code-block-wrapper"><button class="copy-code-btn" onclick="copyChatCode(this)">Copy</button><pre><code>${code.trim()}</code></pre></div>`;
    });
    
    // Parse inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Parse bold text
    html = html.replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>');
    
    // Parse bullet lists
    const lines = html.split('\n');
    let inList = false;
    const processedLines = lines.map(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            const itemContent = trimmed.substring(2);
            if (!inList) {
                inList = true;
                return `<ul><li>${itemContent}</li>`;
            }
            return `<li>${itemContent}</li>`;
        } else {
            if (inList) {
                inList = false;
                return `</ul>${line}`;
            }
            return line;
        }
    });
    if (inList) {
        processedLines.push('</ul>');
    }
    
    return processedLines.join('\n').replace(/\n/g, '<br>');
}

function copyChatCode(btn) {
    if (!btn) return;
    const wrapper = btn.closest(".chat-code-block-wrapper");
    if (!wrapper) return;
    const codeEl = wrapper.querySelector("code");
    if (!codeEl) return;
    const text = codeEl.innerText || codeEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
        btn.innerText = "Copied!";
        setTimeout(() => { btn.innerText = "Copy"; }, 2000);
    });
}

let lastChatSender = null;

function appendChatMessage(sender, content, className, sources = null) {
    const messagesContainer = document.getElementById("chat-messages");
    if (!messagesContainer) return;

    const isGrouped = (lastChatSender === sender);
    lastChatSender = sender;

    const msgEl = document.createElement("div");
    msgEl.className = `chat-message ${className}${isGrouped ? ' grouped' : ''}`;

    const senderEl = document.createElement("span");
    senderEl.className = "message-sender";
    if (className === "assistant" || sender === "Assistant") {
        senderEl.innerHTML = `<img src="/assets/rag_assistant_avatar.jpg" style="width: 18px; height: 18px; border-radius: 50%; vertical-align: middle; margin-right: 4px; border: 1px solid var(--accent);" alt="AI Avatar" /> ${sender}`;
    } else {
        senderEl.innerText = sender;
    }

    const contentEl = document.createElement("span");
    contentEl.className = "message-content";
    contentEl.innerHTML = parseChatMarkdown(content);

    const timeEl = document.createElement("span");
    timeEl.className = "message-time";
    const now = new Date();
    const pad = (n) => n.toString().padStart(2, '0');
    timeEl.innerText = `${pad(now.getHours())}:${pad(now.getMinutes())}`;

    msgEl.appendChild(senderEl);
    msgEl.appendChild(contentEl);
    msgEl.appendChild(timeEl);

    // If assistant message, append copy button
    if (className === "assistant") {
        const copyBtn = document.createElement("button");
        copyBtn.className = "chat-copy-btn";
        copyBtn.innerText = "Copy";
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(content).then(() => {
                copyBtn.innerText = "Copied!";
                setTimeout(() => {
                    copyBtn.innerText = "Copy";
                }, 2000);
            });
        };
        msgEl.appendChild(copyBtn);
    }

    if (sources && sources.length > 0) {
        renderSourceChips(sources, msgEl);
    }

    const isNearBottom = messagesContainer.scrollHeight - messagesContainer.clientHeight - messagesContainer.scrollTop <= 120;
    messagesContainer.appendChild(msgEl);
    if (className === "user" || isNearBottom) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    return msgEl;
}

function renderSourceChips(sources, containerEl) {
    if (!sources || !sources.length || !containerEl) return;
    let sourcesContainer = containerEl.querySelector(".message-sources");
    if (!sourcesContainer) {
        sourcesContainer = document.createElement("div");
        sourcesContainer.className = "message-sources";
        
        const label = document.createElement("span");
        label.innerText = "Sources: ";
        label.style.fontWeight = "600";
        sourcesContainer.appendChild(label);
        containerEl.appendChild(sourcesContainer);
    } else {
        const existingChips = sourcesContainer.querySelectorAll(".source-chip");
        existingChips.forEach(c => c.remove());
    }

    sources.forEach((src) => {
        const chip = document.createElement("a");
        chip.href = src.url || "#";
        const isWeb = Boolean(src.url || src.domain || src.is_web);
        chip.className = `source-chip ${isWeb ? 'web-source-chip' : 'local-source-chip'}`;

        const filename = src.title || src.filename || (src.filepath ? src.filepath.split(/[/\\]/).pop() : "document");
        const srcExt = filename ? filename.split('.').pop().toLowerCase() : '';
        const cat = typeof getFileCategory === "function" ? getFileCategory(srcExt) : "doc";
        chip.setAttribute("data-category", cat);
        chip.setAttribute("data-ext", srcExt);

        const iconSvg = isWeb ? "🌐" : (typeof getFileIconSvg === "function" ? getFileIconSvg(srcExt, 12) : "📄");
        chip.innerHTML = `${iconSvg} <span>${escapeHtml(filename)}</span>`;

        chip.onclick = (e) => {
            e.preventDefault();
            if (isWeb && src.url) {
                window.open(src.url, '_blank');
            } else {
                if (typeof switchTab === "function") switchTab('workspace');
                if (typeof showPreview === "function") showPreview(src.filepath);
            }
        };
        sourcesContainer.appendChild(chip);
    });
}

function renderGlobalCitationChips(sources) {
    const container = document.getElementById("citation-chips-container");
    if (!container || !sources || !sources.length) return;
    container.innerHTML = "";

    const label = document.createElement("span");
    label.innerText = "Grounded Citations: ";
    label.style.fontWeight = "600";
    label.style.color = "var(--text-secondary)";
    container.appendChild(label);

    sources.forEach(src => {
        const chip = document.createElement("a");
        chip.href = src.url || "#";
        const isWeb = Boolean(src.url || src.domain || src.is_web);
        chip.className = `source-chip ${isWeb ? 'web-source-chip' : 'local-source-chip'}`;

        const filename = src.title || src.filename || (src.filepath ? src.filepath.split(/[/\\]/).pop() : "document");
        const srcExt = filename ? filename.split('.').pop().toLowerCase() : '';
        const iconSvg = isWeb ? "🌐" : (typeof getFileIconSvg === "function" ? getFileIconSvg(srcExt, 12) : "📄");
        chip.innerHTML = `${iconSvg} <span>${escapeHtml(filename)}</span>`;

        chip.onclick = (e) => {
            e.preventDefault();
            if (isWeb && src.url) {
                window.open(src.url, '_blank');
            } else {
                if (typeof switchTab === "function") switchTab('workspace');
                if (typeof showPreview === "function") showPreview(src.filepath);
            }
        };
        container.appendChild(chip);
    });
}

window.fetchChatSessions = fetchChatSessions;
window.createNewSession = createNewSession;
window.switchSession = switchSession;
window.deleteSession = deleteSession;
window.filterChatSessions = filterChatSessions;
window.handleChatKeyDown = handleChatKeyDown;
window.sendChatMessage = sendChatMessage;
window.sendPromptChip = sendPromptChip;
window.renderSourceChips = renderSourceChips;
window.renderGlobalCitationChips = renderGlobalCitationChips;
window.parseChatMarkdown = parseChatMarkdown;
window.copyChatCode = copyChatCode;


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

        renderBreadcrumbTrail(path);
        highlightActiveTreeNode(path);

        const textarea = document.getElementById("workspace-editor-textarea");
        const saveBtn = document.getElementById("workspace-save-btn");
        
        textarea.value = data.content || "";
        textarea.removeAttribute("disabled");
        saveBtn.removeAttribute("disabled");
        updateEditorCounters(textarea.value);
        setTimeout(updateMinimap, 50); // slight delay to allow textarea rendering and sizing

        if (!textarea.dataset.shortcutsBound) {
            textarea.dataset.shortcutsBound = "true";
            textarea.addEventListener("keydown", (e) => {
                if (e.ctrlKey && e.key.toLowerCase() === 's') {
                    e.preventDefault();
                    saveWorkspaceFile();
                }
                if (e.key === 'Tab') {
                    e.preventDefault();
                    const start = textarea.selectionStart;
                    const end = textarea.selectionEnd;
                    const val = textarea.value;
                    textarea.value = val.substring(0, start) + "    " + val.substring(end);
                    textarea.selectionStart = textarea.selectionEnd = start + 4;
                    updateEditorCounters(textarea.value);
                    updateMinimap();
                }
            });
            textarea.addEventListener("input", () => {
                updateEditorCounters(textarea.value);
                updateMinimap();
            });
        }

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
    } else if (['mp4', 'webm', 'mkv', 'avi', 'mov'].includes(suffix)) {
        const video = document.createElement("video");
        video.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
        video.controls = true;
        video.style.maxWidth = "100%";
        video.style.maxHeight = "100%";
        video.style.display = "block";
        video.style.margin = "0 auto";
        video.onerror = () => {
            previewContent.innerHTML = `<div class="preview-placeholder" style="color:var(--danger); border:1px solid var(--danger); padding:1rem; text-align:center;">⚠️ Native browser video player cannot play this codec format.<br/><small>Click "Open Externally" to view.</small></div>`;
        };
        previewContent.appendChild(video);
    } else if (['mp3', 'wav', 'ogg', 'aac', 'm4a', 'flac'].includes(suffix)) {
        const audio = document.createElement("audio");
        audio.src = `/api/file/raw?path=${encodeURIComponent(data.filepath)}`;
        audio.controls = true;
        audio.style.width = "90%";
        audio.style.display = "block";
        audio.style.margin = "2rem auto";
        audio.onerror = () => {
            previewContent.innerHTML = `<div class="preview-placeholder" style="color:var(--danger); border:1px solid var(--danger); padding:1rem; text-align:center;">⚠️ Native browser audio player cannot play this codec format.<br/><small>Click "Open Externally" to listen.</small></div>`;
        };
        previewContent.appendChild(audio);
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

let isWorkspaceEditorDirty = false;

function closeWorkspaceEditor() {
    if (isWorkspaceEditorDirty) {
        const proceed = confirm("You have unsaved changes in the text editor. Close without saving?");
        if (!proceed) return;
    }
    isWorkspaceEditorDirty = false;
    currentWorkspaceFilePath = null;
    const dashboard = document.getElementById("workspace-dashboard");
    const splitScreen = document.getElementById("workspace-split-screen");
    if (dashboard) dashboard.classList.remove("hidden");
    if (splitScreen) splitScreen.classList.add("hidden");
    
    const breadcrumb = document.getElementById("explorer-breadcrumb-trail");
    if (breadcrumb) breadcrumb.classList.add("hidden");
    
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

function renderBreadcrumbTrail(path) {
    const el = document.getElementById("explorer-breadcrumb-trail");
    if (!el) return;
    if (!path) {
        el.classList.add("hidden");
        return;
    }
    el.classList.remove("hidden");
    const normalized = path.replace(/\\/g, "/");
    const parts = normalized.split("/").filter(Boolean);
    let accum = "";
    let html = `<span class="breadcrumb-segment" onclick="clearFolderScopeFilter(); triggerSearch();">Root</span>`;
    parts.forEach((part, idx) => {
        accum += (accum ? "/" : "") + part;
        const currentPath = accum;
        const isLast = (idx === parts.length - 1);
        html += ` <span class="breadcrumb-sep">/</span> `;
        if (isLast) {
            html += `<span class="breadcrumb-segment active" title="${escapeHtml(currentPath)}">${escapeHtml(part)}</span>`;
        } else {
            html += `<span class="breadcrumb-segment" title="${escapeHtml(currentPath)}" onclick="setFolderScopeFilter('${escapeHtml(currentPath)}')">${escapeHtml(part)}</span>`;
        }
    });
    el.innerHTML = html;
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

    const copyBtn = document.getElementById("workspace-copy-insights-btn");

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
    if (copyBtn) {
        copyBtn.setAttribute("disabled", "true");
    }

    try {
        const response = await fetch("/api/file/insights", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ filepath: filePath })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `HTTP error ${response.status}`);
        }

        const data = await response.json();

        if (insightsContent) {
            insightsContent.innerHTML = renderMarkdown(data.insights);
        }
        if (copyBtn) {
            copyBtn.removeAttribute("disabled");
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

function insertMarkdownFormat(prefix, suffix) {
    const textarea = document.getElementById("workspace-editor-textarea");
    if (!textarea || textarea.disabled) return;
    
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selected = text.substring(start, end);
    
    const replacement = prefix + selected + suffix;
    textarea.value = text.substring(0, start) + replacement + text.substring(end);
    
    textarea.selectionStart = start + prefix.length;
    textarea.selectionEnd = start + prefix.length + selected.length;
    textarea.focus();
    updateEditorCounters(textarea.value);
    updateMinimap();
}

function initSplitDivider() {
    const divider = document.getElementById("workspace-split-divider");
    const previewPane = document.getElementById("workspace-preview-pane");
    const container = document.getElementById("workspace-split-screen");
    
    if (!divider || !previewPane || !container) return;
    
    let isDragging = false;
    
    divider.addEventListener("mousedown", (e) => {
        isDragging = true;
        divider.classList.add("dragging");
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none";
    });
    
    document.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        
        const containerRect = container.getBoundingClientRect();
        let newWidthPx = e.clientX - containerRect.left;
        let percentage = (newWidthPx / containerRect.width) * 100;
        
        if (percentage < 15) percentage = 15;
        if (percentage > 85) percentage = 85;
        
        previewPane.style.width = `${percentage}%`;
    });
    
    document.addEventListener("mouseup", () => {
        if (isDragging) {
            isDragging = false;
            divider.classList.remove("dragging");
            document.body.style.cursor = "";
            document.body.style.userSelect = "";
        }
    });
}

function copyWorkspaceInsights() {
    const insightsContent = document.getElementById("workspace-insights-content");
    if (!insightsContent) return;
    
    const text = insightsContent.innerText;
    if (!text || text.includes("Select a document to load insights") || text.includes("Generating insights using local LLM")) return;
    
    navigator.clipboard.writeText(text).then(() => {
        const copyBtn = document.getElementById("workspace-copy-insights-btn");
        if (copyBtn) {
            const originalText = copyBtn.innerText;
            copyBtn.innerText = "Copied!";
            setTimeout(() => {
                copyBtn.innerText = originalText;
            }, 1500);
        }
    }).catch(err => {
        console.error("Failed to copy insights:", err);
    });
}

function updateEditorCounters(text) {
    const statusBar = document.getElementById("editor-status-bar");
    if (!statusBar) return;
    
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    
    statusBar.innerText = `Words: ${words} | Characters: ${chars}`;
}

function applyResultsSorting() {
    const sortVal = document.getElementById("results-sort-select") ? document.getElementById("results-sort-select").value : "relevance";
    
    let sorted = [...currentSearchResults];
    
    if (sortVal === "name_asc") {
        sorted.sort((a, b) => a.filename.localeCompare(b.filename));
    } else if (sortVal === "name_desc") {
        sorted.sort((a, b) => b.filename.localeCompare(a.filename));
    } else if (sortVal === "size_desc") {
        sorted.sort((a, b) => (b.file_size || 0) - (a.file_size || 0));
    } else if (sortVal === "size_asc") {
        sorted.sort((a, b) => (a.file_size || 0) - (b.file_size || 0));
    } else if (sortVal === "date_desc") {
        sorted.sort((a, b) => (b.modified_at || 0) - (a.modified_at || 0));
    } else if (sortVal === "date_asc") {
        sorted.sort((a, b) => (a.modified_at || 0) - (b.modified_at || 0));
    }
    
    renderResults(sorted);
}

function updateMinimap() {
    const textarea = document.getElementById("workspace-editor-textarea");
    const minimap = document.getElementById("workspace-editor-minimap");
    const slider = document.getElementById("minimap-slider");
    
    if (!textarea || !minimap || !slider) return;
    
    const textNodes = Array.from(minimap.childNodes).filter(node => node.id !== "minimap-slider");
    textNodes.forEach(node => node.remove());
    
    const textSpan = document.createElement("span");
    textSpan.innerText = textarea.value;
    minimap.appendChild(textSpan);
    
    const scrollHeight = textarea.scrollHeight;
    const clientHeight = textarea.clientHeight;
    
    if (scrollHeight <= clientHeight) {
        slider.style.height = "100%";
        slider.style.top = "0px";
    } else {
        const ratio = clientHeight / scrollHeight;
        const sliderHeight = Math.max(15, ratio * minimap.clientHeight);
        slider.style.height = `${sliderHeight}px`;
        
        const scrollRatio = textarea.scrollTop / (scrollHeight - clientHeight);
        const maxSliderTop = minimap.clientHeight - sliderHeight;
        slider.style.top = `${scrollRatio * maxSliderTop}px`;
    }
}

function initMinimapListeners() {
    const textarea = document.getElementById("workspace-editor-textarea");
    const minimap = document.getElementById("workspace-editor-minimap");
    const slider = document.getElementById("minimap-slider");
    
    if (!textarea || !minimap || !slider) return;
    
    textarea.addEventListener("scroll", () => {
        const scrollHeight = textarea.scrollHeight;
        const clientHeight = textarea.clientHeight;
        const sliderHeight = parseFloat(slider.style.height) || 0;
        
        if (scrollHeight > clientHeight) {
            const scrollRatio = textarea.scrollTop / (scrollHeight - clientHeight);
            const maxSliderTop = minimap.clientHeight - sliderHeight;
            slider.style.top = `${scrollRatio * maxSliderTop}px`;
        }
    });
    
    let isDragging = false;
    let startY = 0;
    let startSliderTop = 0;
    
    const onDrag = (e) => {
        if (!isDragging) return;
        const deltaY = e.clientY - startY;
        const sliderHeight = parseFloat(slider.style.height) || 0;
        const maxSliderTop = minimap.clientHeight - sliderHeight;
        let newTop = Math.max(0, Math.min(maxSliderTop, startSliderTop + deltaY));
        
        slider.style.top = `${newTop}px`;
        
        const scrollRatio = maxSliderTop > 0 ? newTop / maxSliderTop : 0;
        const scrollHeight = textarea.scrollHeight;
        const clientHeight = textarea.clientHeight;
        textarea.scrollTop = scrollRatio * (scrollHeight - clientHeight);
    };
    
    slider.addEventListener("mousedown", (e) => {
        e.stopPropagation();
        isDragging = true;
        startY = e.clientY;
        startSliderTop = parseFloat(slider.style.top) || 0;
        document.body.style.userSelect = "none";
        document.addEventListener("mousemove", onDrag);
    });
    
    document.addEventListener("mouseup", () => {
        if (isDragging) {
            isDragging = false;
            document.body.style.userSelect = "";
            document.removeEventListener("mousemove", onDrag);
        }
    });
    
    minimap.addEventListener("click", (e) => {
        if (e.target === slider) return;
        const rect = minimap.getBoundingClientRect();
        const clickY = e.clientY - rect.top;
        const sliderHeight = parseFloat(slider.style.height) || 0;
        const maxSliderTop = minimap.clientHeight - sliderHeight;
        
        let newTop = clickY - (sliderHeight / 2);
        newTop = Math.max(0, Math.min(maxSliderTop, newTop));
        slider.style.top = `${newTop}px`;
        
        const scrollRatio = maxSliderTop > 0 ? newTop / maxSliderTop : 0;
        const scrollHeight = textarea.scrollHeight;
        const clientHeight = textarea.clientHeight;
        textarea.scrollTop = scrollRatio * (scrollHeight - clientHeight);
    });
}

function exportSearchResultsCsv() {
    if (!currentSearchResults || currentSearchResults.length === 0) {
        alert("No search results to export.");
        return;
    }
    
    // Construct CSV Header
    let csvContent = "Filepath,Filename,Size (Bytes),Modified At,Tags\n";
    
    // Populate rows
    currentSearchResults.forEach(item => {
        const filepath = `"${(item.filepath || '').replace(/"/g, '""')}"`;
        const filename = `"${(item.filename || '').replace(/"/g, '""')}"`;
        const size = item.file_size || 0;
        const modified = item.modified_at || '';
        const tags = `"${(item.tags || []).join(', ').replace(/"/g, '""')}"`;
        
        csvContent += `${filepath},${filename},${size},${modified},${tags}\n`;
    });
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "search_results.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


// ============================================================
// AREA 2: Animated KPI Count-Up
// ============================================================
function animateCountUp(el, target, duration = 800) {
    if (!el) return;
    const start = parseInt(el.innerText) || 0;
    if (start === target) return;
    const range = target - start;
    const startTime = performance.now();
    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // ponytail: easeOutQuad, no dependency
        const eased = 1 - (1 - progress) * (1 - progress);
        el.innerText = Math.round(start + range * eased);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// ============================================================
// AREA 5: Chat — Typing indicator, relative time, code copy
// ============================================================
function showTypingIndicator() {
    const msgs = document.getElementById("chat-messages");
    if (!msgs || document.getElementById("typing-bubble")) return;
    const div = document.createElement("div");
    div.className = "chat-message assistant";
    div.id = "typing-bubble";
    div.innerHTML = `
        <span class="message-sender"><img src="/assets/rag_assistant_avatar.jpg" style="width:20px;height:20px;border-radius:50%;vertical-align:middle;margin-right:6px;border:1px solid var(--accent);" alt="" /> Uroboros Assistant</span>
        <span class="message-content"><span class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span></span>
    `;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById("typing-bubble");
    if (el) el.remove();
}

function formatRelativeTime(dateStr) {
    if (!dateStr) return "";
    const now = Date.now();
    const then = new Date(dateStr).getTime();
    const diffSec = Math.floor((now - then) / 1000);
    if (diffSec < 60) return "just now";
    if (diffSec < 3600) return Math.floor(diffSec / 60) + "m ago";
    if (diffSec < 86400) return Math.floor(diffSec / 3600) + "h ago";
    return Math.floor(diffSec / 86400) + "d ago";
}

// ============================================================
// AREA 6: Settings — Accordion toggle & VACUUM with status
// ============================================================
function toggleAccordion(headerEl) {
    const section = headerEl.closest(".accordion-section");
    if (section) section.classList.toggle("open");
}

async function runVacuumWithStatus() {
    const statusEl = document.getElementById("vacuum-op-status");
    if (statusEl) {
        statusEl.className = "op-status-indicator";
        statusEl.innerText = "Running...";
        statusEl.classList.add("visible");
    }
    try {
        const res = await fetch("/api/backup", { method: "POST" });
        const d = await res.json();
        if (statusEl) {
            statusEl.className = "op-status-indicator success visible";
            statusEl.innerText = "✓ VACUUM & WAL Maintenance Completed: " + (d.status || "success");
        }
        showToast("Database maintenance completed successfully.", "success");
    } catch (e) {
        if (statusEl) {
            statusEl.className = "op-status-indicator error visible";
            statusEl.innerText = "✕ Failed: " + e.message;
        }
        showToast("Database maintenance failed: " + e.message, "error");
    }
    // Auto-hide after 5s
    setTimeout(() => { if (statusEl) statusEl.classList.remove("visible"); }, 5000);
}

function populateSettingsSummary(statsData) {
    const cfgTheme = document.getElementById("cfg-theme");
    if (cfgTheme) cfgTheme.innerText = document.body.classList.contains("light-theme") ? "Light" : "Dark";
    const cfgDbSize = document.getElementById("cfg-db-size");
    if (cfgDbSize && statsData.db_size !== undefined) cfgDbSize.innerText = formatBytes(statsData.db_size);
    const cfgFileCount = document.getElementById("cfg-file-count");
    if (cfgFileCount && statsData.total_files !== undefined) cfgFileCount.innerText = statsData.total_files;
}

// ============================================================
// AREA 7: Account — Env info, activity timeline, storage bar
// ============================================================
async function fetchSystemEnv() {
    try {
        const res = await fetch("/api/system/env");
        const d = await res.json();
        const set = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val || "—"; };
        set("env-python", d.python_version);
        set("env-sqlite", d.sqlite_version);
        set("env-os", d.os_platform);
        set("env-uvicorn", d.uvicorn_version);
        set("env-db-path", d.db_file_path);
    } catch (e) {
        console.warn("Failed to fetch system env:", e);
    }
}

function populateAccountView(statsData) {
    // Storage bar
    const bar = document.getElementById("acct-storage-bar");
    const usedLabel = document.getElementById("acct-storage-used");
    if (bar && statsData.db_size !== undefined) {
        // ponytail: heuristic cap at 500MB for visual scaling
        const capBytes = 500 * 1024 * 1024;
        const pct = Math.min((statsData.db_size / capBytes) * 100, 100);
        bar.style.width = pct.toFixed(1) + "%";
    }
    if (usedLabel && statsData.db_size !== undefined) {
        usedLabel.innerText = formatBytes(statsData.db_size) + " used";
    }

    // Activity timeline from search history
    const timeline = document.getElementById("acct-activity-timeline");
    if (timeline && statsData.timeline && statsData.timeline.length > 0) {
        timeline.innerHTML = "";
        statsData.timeline.slice(0, 8).forEach(item => {
            const div = document.createElement("div");
            div.className = "activity-item";
            div.innerHTML = `
                <div class="activity-item-time">${formatRelativeTime(item.modified_at) || item.modified_at || ""}</div>
                <div class="activity-item-desc">Indexed: ${escapeHtml(item.filename || "")}</div>
            `;
            timeline.appendChild(div);
        });
    }
}

// ============================================================
// AREA 4: Explorer — File count badge
// ============================================================
function updateFileCountBadge(count) {
    let badge = document.querySelector(".file-count-badge");
    if (!badge) {
        const header = document.querySelector(".explorer-sidebar .explorer-header");
        if (header) {
            badge = document.createElement("span");
            badge.className = "file-count-badge";
            header.appendChild(badge);
        }
    }
    if (badge) badge.innerText = (count || 0) + " files";
}

function copyEditorText() {
    const textarea = document.getElementById("workspace-editor-textarea");
    if (!textarea || !textarea.value) return;
    navigator.clipboard.writeText(textarea.value);
    showToast("Editor text copied to clipboard!", "success");
}

function clearEditorText() {
    const textarea = document.getElementById("workspace-editor-textarea");
    if (!textarea) return;
    if (confirm("Clear editor content?")) {
        textarea.value = "";
        updateEditorCounters("");
        isWorkspaceEditorDirty = true;
    }
}

function downloadEditorText() {
    const textarea = document.getElementById("workspace-editor-textarea");
    if (!textarea || !textarea.value) return;
    const blob = new Blob([textarea.value], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = currentWorkspaceFilePath ? currentWorkspaceFilePath.split(/[\\/]/).pop() : "document.txt";
    a.click();
    showToast("File downloaded!", "success");
}

function filterTableRows(containerId, query) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const rows = container.querySelectorAll("table tbody tr");
    const q = query.toLowerCase().trim();
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(q) ? "" : "none";
    });
}

function highlightActiveTreeNode(path) {
    if (!path) return;
    const baseName = path.split(/[\\/]/).pop();
    document.querySelectorAll(".tree-file-title").forEach(el => el.classList.remove("tree-file-selected"));
    document.querySelectorAll(".tree-file-title").forEach(el => {
        if (el.innerText.trim() === baseName) {
            el.classList.add("tree-file-selected");
            let parent = el.parentElement;
            while (parent && !parent.classList.contains("file-tree-container")) {
                if (parent.classList.contains("tree-folder-children")) {
                    parent.style.display = "block";
                }
                parent = parent.parentElement;
            }
        }
    });
}
