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

