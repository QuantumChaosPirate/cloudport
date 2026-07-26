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
