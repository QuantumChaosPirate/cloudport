// ── State ──────────────────────────────────────────────────────────────────
let token = localStorage.getItem('cloudport_token');
let currentUser = null;

// ── Init ───────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        initDashboard();
    }
});

// ── Auth ───────────────────────────────────────────────────────────────────
async function login() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
        showLoginError('Please enter your username and password.');
        return;
    }

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        const data = await response.json();

        if (!response.ok) {
            showLoginError(data.detail || 'Login failed.');
            return;
        }

        token = data.access_token;
        localStorage.setItem('cloudport_token', token);
        initDashboard();

    } catch (error) {
        showLoginError('Could not connect to the server.');
    }
}

function logout() {
    localStorage.removeItem('cloudport_token');
    token = null;
    currentUser = null;
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('login-screen').style.display = 'flex';
}

function showLoginError(message) {
    const box = document.getElementById('login-error');
    document.getElementById('login-error-message').textContent = message;
    box.style.display = 'block';
}

// ── Dashboard Init ─────────────────────────────────────────────────────────
async function initDashboard() {
    try {
        const response = await fetch('/users/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            logout();
            return;
        }

        currentUser = await response.json();

        // Show dashboard, hide login
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('dashboard').style.display = 'flex';

        // Set user info in sidebar
        document.getElementById('sidebar-username').textContent = currentUser.username;
        document.getElementById('sidebar-role').textContent = currentUser.role;

        // Hide admin sections for non-admin users
        if (currentUser.role === 'user' || currentUser.role === 'child') {
            document.getElementById('nav-users').style.display = 'none';
            document.getElementById('nav-approvals').style.display = 'none';
        }

        // Load home section data
        loadHomeSection();
        loadMyFiles();

    } catch (error) {
        logout();
    }
}

// ── Navigation ─────────────────────────────────────────────────────────────
function showSection(name) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    // Show selected section
    document.getElementById(`section-${name}`).classList.add('active');
    event.target.closest('.nav-item').classList.add('active');

    // Load section data
    if (name === 'files') loadMyFiles();
    if (name === 'users') loadUsers();
    if (name === 'approvals') loadApprovals();
}

// ── Home Section ───────────────────────────────────────────────────────────
function loadHomeSection() {
    // Storage bar
    const used = currentUser.storage_used_bytes;
    const quota = currentUser.storage_quota_bytes;
    const percent = Math.round((used / quota) * 100);

    document.getElementById('storage-bar').style.width = `${percent}%`;
    document.getElementById('storage-text').textContent =
        `${formatBytes(used)} used of ${formatBytes(quota)} (${percent}%)`;

    // Change bar colour if over 80%
    if (percent > 80) {
        document.getElementById('storage-bar').style.background = '#dc2626';
    }

    // Health check
    checkHealth();

    // Hide Grafana link for non-admin users
    if (currentUser.role === 'user' || currentUser.role === 'child') {
        document.getElementById('link-monitoring').style.display = 'none';
    }
}

async function checkHealth() {
    try {
        const response = await fetch('/health/');
        const data = await response.json();
        document.getElementById('health-api').textContent = data.status === 'healthy' ? 'Online' : 'Issues detected';
        document.getElementById('health-dot-db').classList.add('green');
        document.getElementById('health-db').textContent = 'Online';
    } catch {
        document.getElementById('health-api').textContent = 'Offline';
    }
}

// ── Tab Switching ──────────────────────────────────────────────────────────
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');

    if (tabName === 'shared-files') loadSharedFiles();
}

// ── Utilities ──────────────────────────────────────────────────────────────
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(endpoint, {
        ...options,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    return response;
}

// Allow Enter key on login form
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && document.getElementById('login-screen').style.display !== 'none') {
        login();
    }
});
