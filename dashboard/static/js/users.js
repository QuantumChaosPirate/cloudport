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
