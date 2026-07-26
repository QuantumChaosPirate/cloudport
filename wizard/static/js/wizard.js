// ── State ──────────────────────────────────────────────────────────────────
// Tracks the current step and selected storage size
let currentStep = 1;
const totalSteps = 6;
let selectedStorageBytes = null;

// ── Step Navigation ────────────────────────────────────────────────────────

// Move to the next step after validating the current one
function nextStep() {
    if (!validateStep(currentStep)) return;
    goToStep(currentStep + 1);
}

// Move back to the previous step
function prevStep() {
    goToStep(currentStep - 1);
}

// Show a specific step and update the progress bar
function goToStep(stepNumber) {
    // Hide current step
    document.getElementById(`step-${currentStep}`).classList.remove('active');
    document.getElementById(`step-indicator-${currentStep}`).classList.remove('active');

    // Mark current step as completed if moving forward
    if (stepNumber > currentStep) {
        document.getElementById(`step-indicator-${currentStep}`).classList.add('completed');
    } else {
        // Remove completed if going back
        document.getElementById(`step-indicator-${stepNumber}`).classList.remove('completed');
    }

    // Show new step
    currentStep = stepNumber;
    document.getElementById(`step-${currentStep}`).classList.add('active');
    document.getElementById(`step-indicator-${currentStep}`).classList.add('active');
}

// ── Validation ─────────────────────────────────────────────────────────────

// Validate each step before allowing the user to proceed
function validateStep(step) {
    hideError();

    if (step === 3) {
        const domain = document.getElementById('domain').value.trim();
        const email = document.getElementById('email').value.trim();

        if (!domain) {
            showError('Please enter a domain name.');
            return false;
        }
        if (!email || !email.includes('@')) {
            showError('Please enter a valid email address.');
            return false;
        }
    }

    if (step === 4) {
        if (!selectedStorageBytes) {
            showError('Please select a storage plan.');
            return false;
        }
    }

    if (step === 5) {
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('owner-email').value.trim();
        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirm-password').value;
        const jellyfinPassword = document.getElementById('jellyfin-password').value;

        if (!username) {
            showError('Please enter a username.');
            return false;
        }
        if (!email || !email.includes('@')) {
            showError('Please enter a valid email address.');
            return false;
        }
        if (password.length < 8) {
            showError('Password must be at least 8 characters.');
            return false;
        }
        if (password !== confirm) {
            showError('Passwords do not match.');
            return false;
        }
        if (!jellyfinPassword) {
            showError('Please enter a Jellyfin password.');
            return false;
        }
    }

    return true;
}

// ── Storage Selection ──────────────────────────────────────────────────────

// Highlight selected storage option and store the value
function selectStorage(element, bytes) {
    // Remove selected class from all options
    document.querySelectorAll('.storage-option').forEach(option => {
        option.classList.remove('selected');
    });
    // Add selected class to clicked option
    element.classList.add('selected');
    selectedStorageBytes = bytes;
}

// ── Setup Submission ───────────────────────────────────────────────────────

// Collect all form data and send to the FastAPI backend
async function submitSetup() {
    if (!validateStep(5)) return;

    const setupData = {
        const setupData = {
        azure_account_name: document.getElementById('azure-account-name').value.trim(),
        azure_connection_string: document.getElementById('azure-connection-string').value.trim(),
        domain: document.getElementById('domain').value.trim(),
        email: document.getElementById('email').value.trim(),
        storage_quota_bytes: selectedStorageBytes,
        username: document.getElementById('username').value.trim(),
        owner_email: document.getElementById('owner-email').value.trim(),
        password: document.getElementById('password').value,
        jellyfin_password: document.getElementById('jellyfin-password').value,
    };

    try {
        const response = await fetch('/wizard/setup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(setupData)
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || 'Setup failed. Please try again.');
            return;
        }

        // Setup successful — move to done step
        goToStep(5);

    } catch (error) {
        showError('Could not connect to the server. Please try again.');
    }
}

// ── Error Handling ─────────────────────────────────────────────────────────

function showError(message) {
    const errorBox = document.getElementById('error-box');
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorBox.style.display = 'block';
}

function hideError() {
    document.getElementById('error-box').style.display = 'none';
}
