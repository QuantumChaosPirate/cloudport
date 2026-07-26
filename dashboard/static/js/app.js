window.addEventListener('load', () => {
    document.getElementById('login-btn').addEventListener('click', login);
});

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
// ── File Variables ─────────────────────────────────────────────────────────
let selectedFileId = null;

// ── Load Files ─────────────────────────────────────────────────────────────
async function loadMyFiles() {
    try {
        const response = await apiRequest('/files/');
        const files = await response.json();
        renderFiles(files, 'my-files-list');
    } catch (error) {
        console.error('Failed to load files:', error);
    }
}

async function loadSharedFiles() {
    try {
        const response = await apiRequest('/files/shared');
        const files = await response.json();
        renderFiles(files, 'shared-files-list', true);
    } catch (error) {
        console.error('Failed to load shared files:', error);
    }
}

async function loadApprovals() {
    try {
        const response = await apiRequest('/files/pending');
        const files = await response.json();
        renderApprovals(files);
    } catch (error) {
        console.error('Failed to load approvals:', error);
    }
}

// ── Render Files ───────────────────────────────────────────────────────────
function renderFiles(files, containerId, isShared = false) {
    const container = document.getElementById(containerId);

    if (files.length === 0) {
        container.innerHTML = '<p class="empty-state">No files here yet.</p>';
        return;
    }

    container.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-info">
                <span class="file-name">${file.filename}</span>
                <span class="file-meta">${formatBytes(file.file_size)} · ${file.content_type} · ${file.status}</span>
            </div>
            <div class="file-actions">
                <button class="btn-small btn-download" onclick="downloadFile('${file.object_key}')">Download</button>
                ${!isShared ? `<button class="btn-small btn-share" onclick="openShareModal(${file.id})">Share</button>` : ''}
                ${!isShared ? `<button class="btn-small btn-delete" onclick="deleteFile(${file.id})">Delete</button>` : ''}
            </div>
        </div>
    `).join('');
}

function renderApprovals(files) {
    const container = document.getElementById('approvals-list');

    if (files.length === 0) {
        container.innerHTML = '<p class="empty-state">No pending approvals.</p>';
        return;
    }

    container.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-info">
                <span class="file-name">${file.filename}</span>
                <span class="file-meta">${formatBytes(file.file_size)} · ${file.content_type}</span>
            </div>
            <div class="file-actions">
                <button class="btn-small btn-approve" onclick="approveFile(${file.id}, true)">Approve</button>
                <button class="btn-small btn-reject" onclick="approveFile(${file.id}, false)">Reject</button>
            </div>
        </div>
    `).join('');
}

// ── Upload ─────────────────────────────────────────────────────────────────
function showUploadModal() {
    document.getElementById('upload-modal').style.display = 'flex';
}

function closeUploadModal() {
    document.getElementById('upload-modal').style.display = 'none';
    document.getElementById('upload-file-input').value = '';
    document.getElementById('upload-progress-container').style.display = 'none';
    document.getElementById('upload-progress-bar').style.width = '0%';
}

async function uploadFile() {
    const fileInput = document.getElementById('upload-file-input');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file.');
        return;
    }

    try {
        // Step 1 — Get presigned URL
        document.getElementById('upload-progress-container').style.display = 'block';
        document.getElementById('upload-progress-text').textContent = 'Requesting upload URL...';

        const urlResponse = await apiRequest('/storage/presigned-upload', {
            method: 'POST',
            body: JSON.stringify({
                filename: file.name,
                content_type: file.type || 'application/octet-stream'
            })
        });

        const { upload_url, object_key } = await urlResponse.json();

        // Step 2 — Upload directly to Azure
        document.getElementById('upload-progress-text').textContent = 'Uploading to storage...';
        document.getElementById('upload-progress-bar').style.width = '50%';

        await fetch(upload_url, {
            method: 'PUT',
            headers: {
                'Content-Type': file.type || 'application/octet-stream',
                'x-ms-blob-type': 'BlockBlob'
            },
            body: file
        });

        // Step 3 — Trigger scan
        document.getElementById('upload-progress-text').textContent = 'Scanning for malware...';
        document.getElementById('upload-progress-bar').style.width = '75%';

        const scanResponse = await fetch(`/storage/scan/${object_key}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        document.getElementById('upload-progress-bar').style.width = '100%';

        if (!scanResponse.ok) {
            const error = await scanResponse.json();
            alert(`Upload failed: ${error.detail}`);
            closeUploadModal();
            return;
        }

        document.getElementById('upload-progress-text').textContent = 'Upload complete!';

        setTimeout(() => {
            closeUploadModal();
            loadMyFiles();
        }, 1000);

    } catch (error) {
        alert('Upload failed. Please try again.');
        closeUploadModal();
    }
}

// ── Download ───────────────────────────────────────────────────────────────
async function downloadFile(objectKey) {
    try {
        const response = await apiRequest(`/storage/presigned-download/${objectKey}`);
        const { download_url } = await response.json();
        window.open(download_url, '_blank');
    } catch (error) {
        alert('Could not generate download link.');
    }
}

// ── Share ──────────────────────────────────────────────────────────────────
function openShareModal(fileId) {
    selectedFileId = fileId;
    document.getElementById('share-modal').style.display = 'flex';
}

function closeShareModal() {
    document.getElementById('share-modal').style.display = 'none';
    selectedFileId = null;
}

async function shareFile() {
    const userId = document.getElementById('share-user-id').value;
    const permission = document.getElementById('share-permission').value;

    if (!userId) {
        alert('Please enter a user ID.');
        return;
    }

    try {
        await apiRequest(`/files/${selectedFileId}/share`, {
            method: 'POST',
            body: JSON.stringify({
                user_id: parseInt(userId),
                permission: permission
            })
        });

        closeShareModal();
        alert('File shared successfully.');
    } catch (error) {
        alert('Failed to share file.');
    }
}

// ── Delete ─────────────────────────────────────────────────────────────────
async function deleteFile(fileId) {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
        await apiRequest(`/files/${fileId}`, { method: 'DELETE' });
        loadMyFiles();
    } catch (error) {
        alert('Failed to delete file.');
    }
}

// ── Approve ────────────────────────────────────────────────────────────────
async function approveFile(fileId, approved) {
    try {
        await apiRequest(`/files/${fileId}/approve`, {
            method: 'PATCH',
            body: JSON.stringify({ approved })
        });
        loadApprovals();
    } catch (error) {
        alert('Failed to process approval.');
    }
}
// ── Load Users ─────────────────────────────────────────────────────────────
async function loadUsers() {
    try {
        const response = await apiRequest('/users/');
        const users = await response.json();
        renderUsers(users);
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

// ── Render Users ───────────────────────────────────────────────────────────
function renderUsers(users) {
    const container = document.getElementById('user-list');

    if (users.length === 0) {
        container.innerHTML = '<p class="empty-state">No users found.</p>';
        return;
    }

    container.innerHTML = users.map(user => `
        <div class="user-item">
            <div class="user-details">
                <span class="user-name">${user.username} ${user.role === 'owner' ? '👑' : ''}</span>
                <span class="user-email">${user.email}</span>
                <span class="user-quota">${formatBytes(user.storage_used_bytes)} / ${formatBytes(user.storage_quota_bytes)}</span>
            </div>
            <div class="user-actions">
                <span class="role-badge">${user.role}</span>
                ${currentUser.role === 'owner' && user.role !== 'owner' ? `
                    <button class="btn-small btn-share" onclick="toggleApproval(${user.id}, ${!user.requires_upload_approval})">
                        ${user.requires_upload_approval ? 'Disable Approval' : 'Enable Approval'}
                    </button>
                    <button class="btn-small ${user.is_active ? 'btn-delete' : 'btn-approve'}" 
                        onclick="toggleActive(${user.id}, ${!user.is_active})">
                        ${user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// ── Toggle Upload Approval ─────────────────────────────────────────────────
async function toggleApproval(userId, requiresApproval) {
    try {
        await apiRequest(`/users/${userId}/upload-approval`, {
            method: 'PATCH',
            body: JSON.stringify({ requires_upload_approval: requiresApproval })
        });
        loadUsers();
    } catch (error) {
        alert('Failed to update upload approval setting.');
    }
}

// ── Toggle Active Status ───────────────────────────────────────────────────
async function toggleActive(userId, isActive) {
    const action = isActive ? 'activate' : 'deactivate';
    if (!confirm(`Are you sure you want to ${action} this account?`)) return;

    try {
        await apiRequest(`/users/${userId}/active?is_active=${isActive}`, {
            method: 'PATCH'
        });
        loadUsers();
    } catch (error) {
        alert('Failed to update account status.');
    }
}
// ── Storage Utilities ──────────────────────────────────────────────────────

// Refresh storage usage display
async function refreshStorageUsage() {
    try {
        const response = await apiRequest('/users/me');
        const user = await response.json();

        const used = user.storage_used_bytes;
        const quota = user.storage_quota_bytes;
        const percent = Math.round((used / quota) * 100);

        document.getElementById('storage-bar').style.width = `${percent}%`;
        document.getElementById('storage-text').textContent =
            `${formatBytes(used)} used of ${formatBytes(quota)} (${percent}%)`;

        // Warn if over 80%
        if (percent > 80) {
            document.getElementById('storage-bar').style.background = '#f59e0b';
        }

        // Critical if over 95%
        if (percent > 95) {
            document.getElementById('storage-bar').style.background = '#dc2626';
        }

    } catch (error) {
        console.error('Failed to refresh storage usage:', error);
    }
}

// Auto refresh storage every 60 seconds
setInterval(refreshStorageUsage, 60000);

