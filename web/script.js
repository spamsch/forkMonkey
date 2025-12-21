// ForkMonkey Web Interface

// Initialize particles background
// Initialize particles background
particlesJS('particles-js', {
    particles: {
        number: { value: 40, density: { enable: true, value_area: 800 } },
        color: { value: '#00ff88' },
        shape: { type: 'circle' },
        opacity: {
            value: 0.2,
            random: true,
            anim: { enable: true, speed: 0.5, opacity_min: 0.05, sync: false }
        },
        size: {
            value: 2,
            random: true,
            anim: { enable: true, speed: 1, size_min: 0.1, sync: false }
        },
        line_linked: {
            enable: true,
            distance: 150,
            color: '#00ff88',
            opacity: 0.1,
            width: 1
        },
        move: {
            enable: true,
            speed: 0.5,
            direction: 'none',
            random: true,
            straight: false,
            out_mode: 'out',
            bounce: false
        }
    },
    interactivity: {
        detect_on: 'canvas',
        events: {
            onhover: { enable: true, mode: 'bubble' },
            onclick: { enable: true, mode: 'push' },
            resize: true
        },
        modes: {
            bubble: { distance: 200, size: 4, duration: 2, opacity: 0.4, speed: 3 },
            push: { particles_nb: 4 }
        }
    },
    retina_detect: true
});

// Rarity colors
const rarityColors = {
    common: '#00ff88',
    uncommon: '#ffd93d',
    rare: '#ff6b9d',
    legendary: '#ffd700'
};

// Load monkey data
async function loadMonkeyData() {
    try {
        // Show loading state
        document.body.classList.add('loading');

        // Determine base path based on environment
        // - GitHub Pages: use relative path (monkey_data copied to web folder)
        // - Local server: use root path
        const isGitHubPages = window.location.hostname.includes('github.io');
        const basePath = isGitHubPages ? 'monkey_data/' : '/monkey_data/';

        // Load DNA
        const dnaResponse = await fetch(basePath + 'dna.json');
        if (!dnaResponse.ok) throw new Error('DNA file not found');
        const dna = await dnaResponse.json();

        // Load stats
        const statsResponse = await fetch(basePath + 'stats.json');
        if (!statsResponse.ok) throw new Error('Stats file not found');
        const stats = await statsResponse.json();

        // Load history
        const historyResponse = await fetch(basePath + 'history.json');
        if (!historyResponse.ok) throw new Error('History file not found');
        const history = await historyResponse.json();

        // Load SVG
        const svgResponse = await fetch(basePath + 'monkey.svg');
        if (!svgResponse.ok) throw new Error('SVG file not found');
        const svgText = await svgResponse.text();

        // Update UI
        updateHeader(dna, stats);
        updateMonkeyDisplay(svgText, dna, stats);
        updateTraits(dna.traits);
        updateHistory(history.entries || []);

        // Remove loading state
        document.body.classList.remove('loading');

    } catch (error) {
        console.error('Error loading monkey data:', error);
        showError('Failed to load monkey data. Make sure you have initialized a monkey first!');
    }
}

// Update header stats
function updateHeader(dna, stats) {
    document.getElementById('generation').textContent = dna.generation || '1';
    document.getElementById('age').textContent = `${stats.age_days || 0}d`;
    document.getElementById('rarity').textContent = `${(stats.rarity_score || 0).toFixed(1)}%`;
}

// Update monkey display
function updateMonkeyDisplay(svgText, dna, stats) {
    const container = document.getElementById('monkey-svg');
    container.innerHTML = svgText;

    document.getElementById('dna-hash').textContent = dna.dna_hash || 'Unknown';
    document.getElementById('mutations').textContent = dna.mutation_count || '0';
    document.getElementById('parent').textContent = dna.parent_id || 'Genesis';
}

// Update traits grid
function updateTraits(traits) {
    const grid = document.getElementById('traits-grid');
    grid.innerHTML = '';

    // Sort traits by category
    const sortedTraits = Object.entries(traits).sort((a, b) => {
        return a[0].localeCompare(b[0]);
    });

    sortedTraits.forEach(([category, trait]) => {
        const card = createTraitCard(category, trait);
        grid.appendChild(card);
    });
}

// Create trait card
function createTraitCard(category, trait) {
    const card = document.createElement('div');
    card.className = `trait-card ${trait.rarity}`;

    // Format category name
    const formattedCategory = category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    // Format trait value
    const formattedValue = trait.value
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    card.innerHTML = `
        <div class="trait-info">
            <div class="trait-category">${formattedCategory}</div>
            <div class="trait-value">${formattedValue}</div>
        </div>
        <div class="trait-rarity">${trait.rarity}</div>
    `;

    return card;
}

// Update history timeline
function updateHistory(entries) {
    // This function is now deprecated in favor of loadEvolutionTimeline
    // Keep it for backward compatibility but make it a no-op
    // The evolution timeline is loaded separately when switching to the History tab
    console.log(`History has ${entries.length} entries (now shown in Evolution Timeline)`);
}

// Create history entry
function createHistoryEntry(entry) {
    const div = document.createElement('div');
    div.className = 'history-entry';

    // Format date
    const date = new Date(entry.timestamp);
    const formattedDate = date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    div.innerHTML = `
        <div class="history-date">${formattedDate}</div>
        <div class="history-content">
            <div class="history-story">${entry.story || 'Evolution occurred'}</div>
            <div class="history-stats">
                <span>Gen: ${entry.generation}</span>
                <span>•</span>
                <span>Mutations: ${entry.mutation_count}</span>
                <span>•</span>
                <span>Rarity: ${(entry.rarity_score || 0).toFixed(1)}%</span>
            </div>
        </div>
    `;

    return div;
}

// Load Community Data
async function loadCommunityData() {
    const grid = document.getElementById('community-grid');

    grid.innerHTML = `
        <div class="loading-spinner">
            <p>ACCESSING FORKNET ARCHIVES...</p>
        </div>
    `;

    try {
        // Try to fetch static data file
        const response = await fetch('community_data.json');

        if (!response.ok) {
            throw new Error('Data file not found');
        }

        const data = await response.json();

        if (data.forks && data.forks.length > 0) {
            renderCommunityGrid(data.forks);
        } else {
            grid.innerHTML = '<div class="nes-container is-dark"><p>No other monkeys found in archives.</p></div>';
        }

    } catch (error) {
        console.warn("Community load error:", error);

        // Show demo data if file missing (dev mode or first run)
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

        if (isLocal) {
            grid.innerHTML = `
                <div class="nes-container is-dark">
                    <p style="color:#ffd700">⚠️ Local Mode: No community_data.json found.</p>
                    <p>Run <code>python src/scan_community.py</code> to generate it.</p>
                </div>
            `;
        } else {
            grid.innerHTML = `
                <div class="nes-container is-dark">
                    <p>Archive Empty.</p>
                    <p style="font-size:0.8rem">The scanner runs daily. Check back tomorrow!</p>
                </div>
            `;
        }
    }
}

function renderCommunityGrid(forks) {
    const grid = document.getElementById('community-grid');
    grid.innerHTML = '';

    forks.forEach(fork => {
        // Skip invalid monkeys
        if (!fork.monkey_stats && !fork.monkey_svg) return;

        const card = document.createElement('a');
        card.className = 'community-card';
        card.href = fork.url;
        card.target = '_blank';

        // Use SVG if available, otherwise fallback
        const previewContent = fork.monkey_svg ||
            '<div style="color:var(--text-muted); font-size: 3rem;">?</div>';

        const isRoot = fork.is_root ? '<span class="owner-badge" style="background:var(--primary);color:#000">ROOT</span>' : '';
        const stats = fork.monkey_stats || { generation: '?', rarity_score: 0, age_days: 0 };

        card.innerHTML = `
            <div class="card-header">
                <span class="repo-name">${fork.owner}/${fork.repo}</span>
                <span class="owner-badge">Gen ${stats.generation}</span>
                ${isRoot}
            </div>
            <div class="card-preview">
                ${previewContent}
            </div>
            <div class="card-stats">
                <div class="stat-row">
                    <label>Rarity</label>
                    <value>${(stats.rarity_score || 0).toFixed(1)}%</value>
                </div>
                <div class="stat-row">
                    <label>Age</label>
                    <value>${stats.age_days || 0}d</value>
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}

// Download monkey SVG
function downloadMonkey() {
    const svgElement = document.querySelector('#monkey-svg svg');
    if (!svgElement) {
        alert('No monkey to download!');
        return;
    }

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `forkmonkey-${Date.now()}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Show error message
function showError(message) {
    const container = document.getElementById('monkey-svg');
    container.innerHTML = `
        <div class="nes-container is-rounded is-dark">
            <p style="color: #ff6b9d;">${message}</p>
            <br>
            <p style="font-size: 0.8rem;">Run: <code>python src/cli.py init</code></p>
        </div>
    `;
}

// Tab Switching
function switchTab(tabId) {
    // Global state
    if (typeof window.currentTab === 'undefined') window.currentTab = 'dashboard';

    // Update tabs
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.nav-tab[data-tab="${tabId}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');

    window.currentTab = tabId;

    // Load data based on tab
    if (tabId === 'community') {
        loadCommunityData();
    } else if (tabId === 'history') {
        loadEvolutionTimeline();
    }
}

// Auto-refresh every 60 seconds
let autoRefreshInterval;

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        if (window.currentTab === 'dashboard') loadMonkeyData();
    }, 60000); // 60 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // R key to refresh
    if (e.key === 'r' || e.key === 'R') {
        if (window.currentTab === 'community') {
            loadCommunityData();
        } else if (window.currentTab === 'history') {
            loadEvolutionTimeline();
        } else {
            loadMonkeyData();
        }
    }

    // D key to download
    if (e.key === 'd' || e.key === 'D') {
        downloadMonkey();
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Tab event listeners
    document.querySelectorAll('.nav-tab').forEach(button => {
        button.addEventListener('click', () => {
            switchTab(button.dataset.tab);
        });
    });

    loadMonkeyData();
    startAutoRefresh();

    // Add visual feedback for loading
    console.log('%c🐵 ForkMonkey Web Interface Loaded!', 'color: #00ff88; font-size: 20px; font-weight: bold;');
    console.log('%cKeyboard shortcuts:', 'color: #ffd93d; font-weight: bold;');
    console.log('%c  R - Refresh data', 'color: #fff;');
    console.log('%c  D - Download SVG', 'color: #fff;');
});

// Handle page visibility (pause auto-refresh when tab is hidden)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        if (typeof window.currentTab !== 'undefined' && window.currentTab === 'dashboard') {
            loadMonkeyData();
        }
    }
});

// Export functions for global access
window.loadMonkeyData = loadMonkeyData;
window.downloadMonkey = downloadMonkey;
window.loadCommunityData = loadCommunityData;

/* ========================================
   PROFESSIONAL ENHANCEMENTS
   ======================================== */

// Load Evolution Timeline from history.json (NO 404s!)
async function loadEvolutionTimeline() {
    const timeline = document.getElementById('evolution-timeline');
    const countEl = document.getElementById('evolution-count');

    try {
        // Determine base path
        const isGitHubPages = window.location.hostname.includes('github.io');
        const basePath = isGitHubPages ? 'monkey_data/' : '/monkey_data/';

        // Load history.json - this already has all the evolution data!
        const historyResponse = await fetch(basePath + 'history.json');
        if (!historyResponse.ok) throw new Error('Failed to load history');

        const history = await historyResponse.json();
        const entries = history.entries || [];

        // Update count
        countEl.textContent = entries.length;

        // Render timeline
        timeline.innerHTML = '';

        if (entries.length === 0) {
            timeline.innerHTML = `
                <div class="nes-container is-dark">
                    <p>No evolution history yet. Your monkey will evolve daily!</p>
                </div>
            `;
            return;
        }

        // Show most recent entries first (reverse order)
        const recentEntries = entries.slice().reverse();

        recentEntries.forEach((entry, index) => {
            const item = createEvolutionItemFromHistory(entry, index);
            timeline.appendChild(item);
        });

    } catch (error) {
        console.error('Error loading evolution timeline:', error);
        timeline.innerHTML = `
            <div class="nes-container is-dark">
                <p style="color: var(--secondary);">Failed to load evolution timeline.</p>
            </div>
        `;
    }
}

function createEvolutionItemFromHistory(entry, index) {
    const item = document.createElement('div');
    item.className = 'evolution-item slide-in';
    item.style.animationDelay = `${index * 0.05}s`;

    // Format date
    const date = new Date(entry.timestamp);
    const dateStr = date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    // Create SVG filename from timestamp (format: YYYY-MM-DD_HH-MM_monkey.svg)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const svgFilename = `${year}-${month}-${day}_${hours}-${minutes}_monkey.svg`;

    // Use GitHub raw URL for public access
    const githubRepo = 'forkZoo/forkMonkey';
    const branch = 'main';
    const svgUrl = `https://raw.githubusercontent.com/${githubRepo}/${branch}/monkey_evolution/${svgFilename}`;

    // Create placeholder
    item.innerHTML = `
        <div class="evolution-thumbnail" style="background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%); padding: 20px; display: flex; align-items: center; justify-content: center;">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 10px;">⏳</div>
                <div style="font-size: 0.7rem; color: var(--text-muted);">Gen ${entry.generation}</div>
            </div>
        </div>
        <div class="evolution-date">${dateStr}</div>
        <div class="evolution-gen">Rarity: ${(entry.rarity_score || 0).toFixed(1)}%</div>
        <div style="font-size: 0.65rem; color: var(--text-muted); margin-top: 4px; text-align: center; padding: 0 4px; line-height: 1.2;">${entry.story || 'Evolution occurred'}</div>
    `;

    // Load SVG from GitHub
    fetch(svgUrl)
        .then(response => {
            if (response.ok) return response.text();
            throw new Error('SVG not found');
        })
        .then(svgText => {
            const thumbnail = item.querySelector('.evolution-thumbnail');
            // Wrap SVG in a container for better sizing
            thumbnail.innerHTML = `<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; padding: 10px;">${svgText}</div>`;
            item.addEventListener('click', () => showEvolutionDetails(entry, dateStr, svgText));
        })
        .catch(() => {
            const thumbnail = item.querySelector('.evolution-thumbnail');
            thumbnail.innerHTML = `<div style="text-align: center;"><div style="font-size: 3rem; margin-bottom: 10px;">🐵</div><div style="font-size: 0.7rem; color: var(--text-muted);">Gen ${entry.generation}</div></div>`;
            item.addEventListener('click', () => showEvolutionDetails(entry, dateStr, null));
        });

    return item;
}

function showEvolutionDetails(entry, dateStr, svgText) {
    const traitsHtml = Object.entries(entry.traits || {})
        .map(([key, value]) => `
            <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: var(--text-muted); text-transform: capitalize;">${key.replace('_', ' ')}</span>
                <span style="color: var(--primary); text-transform: capitalize;">${value}</span>
            </div>
        `)
        .join('');

    const svgDisplay = svgText
        ? `<div style="text-align: center; margin: 20px 0;">${svgText}</div>`
        : `<div style="text-align: center; font-size: 4rem; margin: 20px 0;">🐵</div>`;

    const content = `
        ${svgDisplay}
        <div style="margin: 20px 0;">
            <h4 style="color: var(--primary); margin-bottom: 10px; font-family: 'Press Start 2P', cursive; font-size: 0.8rem;">Evolution Story</h4>
            <p style="color: var(--text-secondary); line-height: 1.6;">${entry.story || 'No story available'}</p>
        </div>
        <div style="margin: 20px 0;">
            <h4 style="color: var(--primary); margin-bottom: 10px; font-family: 'Press Start 2P', cursive; font-size: 0.8rem;">Stats</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                <div><span style="color: var(--text-muted);">Generation:</span> <span style="color: var(--primary);">${entry.generation}</span></div>
                <div><span style="color: var(--text-muted);">Rarity:</span> <span style="color: var(--primary);">${(entry.rarity_score || 0).toFixed(1)}%</span></div>
                <div><span style="color: var(--text-muted);">Mutations:</span> <span style="color: var(--primary);">${entry.mutation_count || 0}</span></div>
                <div style="grid-column: 1 / -1;"><span style="color: var(--text-muted);">DNA:</span> <span style="color: var(--primary); font-size: 0.8rem; font-family: monospace;">${entry.dna_hash || 'N/A'}</span></div>
            </div>
        </div>
        <div style="margin: 20px 0;">
            <h4 style="color: var(--primary); margin-bottom: 10px; font-family: 'Press Start 2P', cursive; font-size: 0.8rem;">Traits</h4>
            <div style="font-size: 0.9rem;">
                ${traitsHtml}
            </div>
        </div>
    `;

    openModal(content, dateStr, null);
}

function createEvolutionItem(filename, svgText, generation) {
    const item = document.createElement('div');
    item.className = 'evolution-item slide-in';
    item.style.animationDelay = `${generation * 0.05}s`;

    // Extract date from filename (format: YYYY-MM-DD_HH-MM_monkey.svg)
    const match = filename.match(/(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})/);
    const dateStr = match ? `${match[1]} ${match[2].replace('-', ':')}` : filename;

    item.innerHTML = `
        <div class="evolution-thumbnail">
            ${svgText}
        </div>
        <div class="evolution-date">${dateStr}</div>
        <div class="evolution-gen">Gen ${generation}</div>
    `;

    item.addEventListener('click', () => openModal(svgText, dateStr));

    return item;
}

// Modal Functions
function openModal(svgText, title) {
    const modal = document.getElementById('svg-modal');
    const container = document.getElementById('modal-svg-container');

    container.innerHTML = `
        <div>
            <h3 style="color: var(--primary); text-align: center; margin-bottom: var(--spacing-md); font-family: 'Press Start 2P', cursive; font-size: var(--font-sm);">
                ${title}
            </h3>
            ${svgText}
        </div>
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('svg-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('svg-modal');
    if (e.target === modal) {
        closeModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// GitHub Token Management
function saveGitHubToken() {
    const input = document.getElementById('github-token');
    const token = input.value.trim();

    if (!token) {
        alert('Please enter a valid token');
        return;
    }

    localStorage.setItem('github_token', token);
    input.value = '';
    input.type = 'password';

    updateCommunityStatus('active', 'Token saved');
    setTimeout(() => updateCommunityStatus('', 'Idle'), 2000);
}

function clearGitHubToken() {
    localStorage.removeItem('github_token');
    document.getElementById('github-token').value = '';
    updateCommunityStatus('', 'Token cleared');
    setTimeout(() => updateCommunityStatus('', 'Idle'), 2000);
}

function getGitHubToken() {
    return localStorage.getItem('github_token') || null;
}

function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    panel.classList.toggle('expanded');
}

// Update community status indicator
function updateCommunityStatus(state, text) {
    const statusDot = document.querySelector('#community-status .status-dot');
    const statusText = document.getElementById('community-status-text');

    statusDot.className = 'status-dot';
    if (state) statusDot.classList.add(state);
    statusText.textContent = text;
}

// Enhanced Community Data Loading with GitHub API
async function loadCommunityDataDynamic() {
    const grid = document.getElementById('community-grid');
    updateCommunityStatus('loading', 'Scanning...');

    grid.innerHTML = `
        <div class="loading-spinner">
            <p>SCANNING GITHUB NETWORK...</p>
        </div>
    `;

    try {
        const token = getGitHubToken();
        const headers = {
            'Accept': 'application/vnd.github.v3+json'
        };

        if (token) {
            headers['Authorization'] = `token ${token}`;
        }

        // Determine current repo
        const repoName = await detectCurrentRepo();

        if (!repoName) {
            throw new Error('Could not determine repository');
        }

        // Fetch repo info
        const repoResponse = await fetch(`https://api.github.com/repos/${repoName}`, { headers });
        if (!repoResponse.ok) throw new Error('Failed to fetch repo info');
        const repo = await repoResponse.json();

        // Determine root repo (if this is a fork, get parent)
        const rootRepo = repo.fork && repo.parent ? repo.parent.full_name : repoName;

        // Fetch forks
        const forksResponse = await fetch(`https://api.github.com/repos/${rootRepo}/forks?per_page=30`, { headers });
        if (!forksResponse.ok) throw new Error('Failed to fetch forks');
        const forks = await forksResponse.json();

        // Add root repo to the list
        const allRepos = [{ ...repo, is_root: true, full_name: rootRepo }, ...forks];

        // Fetch monkey data for each fork
        const monkeyData = await Promise.allSettled(
            allRepos.slice(0, 15).map(fork => fetchMonkeyData(fork, headers))
        );

        const validMonkeys = monkeyData
            .filter(result => result.status === 'fulfilled' && result.value)
            .map(result => result.value);

        if (validMonkeys.length === 0) {
            grid.innerHTML = '<div class="nes-container is-dark"><p>No monkeys found in the network.</p></div>';
            updateCommunityStatus('', 'No results');
            return;
        }

        renderCommunityGrid(validMonkeys);
        updateCommunityStatus('active', `Found ${validMonkeys.length} monkeys`);

    } catch (error) {
        console.error('Community scan error:', error);

        // Fallback to static JSON
        try {
            const response = await fetch('community_data.json');
            if (response.ok) {
                const data = await response.json();
                if (data.forks && data.forks.length > 0) {
                    renderCommunityGrid(data.forks);
                    updateCommunityStatus('', 'Using cached data');
                    return;
                }
            }
        } catch { }

        grid.innerHTML = `
            <div class="nes-container is-dark">
                <p style="color: var(--secondary);">Scan failed: ${error.message}</p>
                <p style="font-size: var(--font-sm); color: var(--text-muted); margin-top: var(--spacing-sm);">
                    ${error.message.includes('rate limit') ? 'API rate limit exceeded. Try adding a GitHub token.' : 'Check your connection and try again.'}
                </p>
            </div>
        `;
        updateCommunityStatus('error', 'Scan failed');
    }
}

async function detectCurrentRepo() {
    // Try to detect from meta tags or use default
    const metaRepo = document.querySelector('meta[name="github-repo"]');
    if (metaRepo) return metaRepo.content;

    // Default to forkZoo/forkMonkey
    return 'forkZoo/forkMonkey';
}

async function fetchMonkeyData(fork, headers) {
    try {
        // Fetch stats.json
        const statsResponse = await fetch(
            `https://api.github.com/repos/${fork.full_name}/contents/monkey_data/stats.json`,
            { headers }
        );

        if (!statsResponse.ok) return null;

        const statsData = await statsResponse.json();
        const stats = JSON.parse(atob(statsData.content));

        // Try to fetch SVG
        let svg = null;
        try {
            const svgResponse = await fetch(
                `https://api.github.com/repos/${fork.full_name}/contents/monkey_data/monkey.svg`,
                { headers }
            );
            if (svgResponse.ok) {
                const svgData = await svgResponse.json();
                svg = atob(svgData.content);
            }
        } catch { }

        return {
            owner: fork.owner.login,
            repo: fork.name,
            url: fork.html_url,
            is_root: fork.is_root || false,
            monkey_stats: stats,
            monkey_svg: svg
        };
    } catch (error) {
        return null;
    }
}

// Override the original loadCommunityData to use dynamic version
window.loadCommunityData = loadCommunityDataDynamic;
window.loadEvolutionTimeline = loadEvolutionTimeline;
window.toggleSettings = toggleSettings;
window.saveGitHubToken = saveGitHubToken;
window.clearGitHubToken = clearGitHubToken;
window.closeModal = closeModal;
