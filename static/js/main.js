// SpeakUp AI - Main Client Engine & Dashboard Controls

document.addEventListener('DOMContentLoaded', () => {
    initAppNavigation();
    initClickOutsideListeners();
    initSplashScreen();
});

function initSplashScreen() {
    const splash = document.getElementById('splashScreen');
    if (!splash) return;

    try {
        if (sessionStorage.getItem('speakup_splash_shown')) {
            // Already displayed once during this session - remove from DOM immediately without showing
            if (splash.parentNode) splash.parentNode.removeChild(splash);
            return;
        }
        // First app open: record that splash has been shown for this session
        sessionStorage.setItem('speakup_splash_shown', 'true');
    } catch (e) {
        // Fallback in case of restricted browser iframe/privacy settings
    }

    // Display splash screen for 5.5 seconds (5 to 6 sec) on initial app open, then smoothly fade out
    setTimeout(() => {
        splash.classList.add('fade-out');
        setTimeout(() => {
            if (splash.parentNode) splash.parentNode.removeChild(splash);
        }, 600);
    }, 5500);
}

function initAppNavigation() {
    // Escape key closes modals and dropdowns
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeSidebar();
            closeProfileDropdown();
            closeProfileModal();
            closeAuthModal();
        }
    });
}

// ----------------------------------------------------
// MOBILE SIDEBAR CONTROLS
// ----------------------------------------------------
function openSidebar() {
    const sidebar = document.getElementById('appSidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (sidebar) sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    const sidebar = document.getElementById('appSidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('open');
    document.body.style.overflow = '';
}

// ----------------------------------------------------
// PROFILE DROPDOWN MENU AT BOTTOM OF SIDEBAR
// ----------------------------------------------------
function toggleProfileDropdown(event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    const dropdown = document.getElementById('profileDropdown');
    const trigger = document.getElementById('sidebarProfileTrigger');
    if (!dropdown) return;

    const isOpen = dropdown.classList.contains('open');
    if (isOpen) {
        closeProfileDropdown();
    } else {
        dropdown.classList.add('open');
        dropdown.setAttribute('aria-hidden', 'false');
        if (trigger) trigger.classList.add('active');
    }
}

function closeProfileDropdown() {
    const dropdown = document.getElementById('profileDropdown');
    const trigger = document.getElementById('sidebarProfileTrigger');
    if (dropdown) {
        dropdown.classList.remove('open');
        dropdown.setAttribute('aria-hidden', 'true');
    }
    if (trigger) trigger.classList.remove('active');
}

function initClickOutsideListeners() {
    document.addEventListener('click', (event) => {
        const sidebar = document.getElementById('appSidebar');
        const hamburgerBtn = document.getElementById('hamburgerMenuBtn');
        const mobileBtn = document.getElementById('mobileMenuBtn');
        if (sidebar && sidebar.classList.contains('open')) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggle = (hamburgerBtn && hamburgerBtn.contains(event.target)) || (mobileBtn && mobileBtn.contains(event.target));
            if (!isClickInsideSidebar && !isClickOnToggle) {
                closeSidebar();
            }
        }

        const dropdown = document.getElementById('profileDropdown');
        const trigger = document.getElementById('sidebarProfileTrigger');
        if (dropdown && dropdown.classList.contains('open')) {
            if (!dropdown.contains(event.target) && !trigger.contains(event.target)) {
                closeProfileDropdown();
            }
        }
    });
}

// ----------------------------------------------------
// PROFILE & ACCOUNT MODAL (FULL SETTINGS)
// ----------------------------------------------------
function openProfileModal(tab = 'profile') {
    closeProfileDropdown();
    const modal = document.getElementById('profileAccountModal');
    if (modal) {
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
        switchProfileModalTab(tab);
    }
}

function closeProfileModal() {
    const modal = document.getElementById('profileAccountModal');
    if (modal) {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }
    const notice = document.getElementById('profileModalNotice');
    if (notice) notice.style.display = 'none';
}

function switchProfileModalTab(tabName) {
    const tabs = ['profile', 'avatar', 'password', 'settings'];
    tabs.forEach(t => {
        const btn = document.getElementById(`tabBtn${t.charAt(0).toUpperCase() + t.slice(1)}`);
        const pane = document.getElementById(`pane${t.charAt(0).toUpperCase() + t.slice(1)}`);
        if (btn) btn.classList.toggle('active', t === tabName);
        if (pane) pane.classList.toggle('active', t === tabName);
    });

    const notice = document.getElementById('profileModalNotice');
    if (notice) notice.style.display = 'none';

    if (tabName === 'settings') {
        checkSettingsStatus();
    }
}

function showModalNotice(message, isError = false) {
    const notice = document.getElementById('profileModalNotice');
    if (!notice) return;
    notice.style.display = 'block';
    notice.className = isError ? 'alert-box alert-danger' : 'alert-box alert-success';
    notice.textContent = message;
}

// ----------------------------------------------------
// AVATAR PRESET SELECTION & CUSTOM AVATAR
// ----------------------------------------------------
async function selectPresetAvatar(avatarEmoji) {
    await updateProfileDetails({ avatar: avatarEmoji });
}

async function applyCustomAvatar() {
    const input = document.getElementById('customAvatarInput');
    const val = input ? input.value.trim() : '';
    if (!val) {
        showToast('Please enter an emoji or 2 letters.', 'warning');
        return;
    }
    await updateProfileDetails({ avatar: val });
}

// ----------------------------------------------------
// EDIT PROFILE (NAME & EMAIL)
// ----------------------------------------------------
async function handleProfileUpdateSubmit(event) {
    event.preventDefault();
    const name = (document.getElementById('profileFullName').value || '').trim();
    const email = (document.getElementById('profileEmail').value || '').trim();
    const btn = document.getElementById('saveProfileBtn');

    if (!name || !email) {
        showModalNotice('Please fill in both name and email.', true);
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Saving...';
    }

    await updateProfileDetails({ name, email });

    if (btn) {
        btn.disabled = false;
        btn.textContent = 'Save Profile';
    }
}

async function updateProfileDetails(payload) {
    try {
        const res = await fetch('/api/user/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            const user = data.user;
            // Update UI elements across the page
            updateUIAfterProfileSave(user);
            showModalNotice('Profile updated successfully!', false);
            showToast('Profile updated!', 'success');
        } else {
            showModalNotice(data.error || 'Failed to update profile.', true);
            showToast(data.error || 'Update failed', 'error');
        }
    } catch (err) {
        showModalNotice('Connection error. Please try again.', true);
        showToast('Connection error', 'error');
    }
}

function updateUIAfterProfileSave(user) {
    const avatar = user.avatar || user.name.slice(0, 2).toUpperCase();

    // Sidebar
    const sName = document.getElementById('sidebarUserName');
    const sEmail = document.getElementById('sidebarUserEmail');
    const sAvatar = document.getElementById('sidebarAvatarPill');
    if (sName) sName.textContent = user.name;
    if (sEmail) sEmail.textContent = user.email;
    if (sAvatar) sAvatar.textContent = avatar;

    // Popover
    const pName = document.getElementById('popoverName');
    const pEmail = document.getElementById('popoverEmail');
    const pAvatar = document.getElementById('popoverAvatar');
    if (pName) pName.textContent = user.name;
    if (pEmail) pEmail.textContent = user.email;
    if (pAvatar) pAvatar.textContent = avatar;

    // Topbar
    const tName = document.getElementById('topbarName');
    const tAvatar = document.getElementById('topbarAvatar');
    if (tName) tName.textContent = user.name.split(' ')[0];
    if (tAvatar) tAvatar.textContent = avatar;

    // Modal
    const mHeadName = document.getElementById('modalHeadingName');
    const mHeadEmail = document.getElementById('modalHeadingEmail');
    const mLargeAvatar = document.getElementById('modalLargeAvatar');
    if (mHeadName) mHeadName.textContent = user.name;
    if (mHeadEmail) mHeadEmail.textContent = user.email;
    if (mLargeAvatar) mLargeAvatar.textContent = avatar;

    // Inputs
    const inName = document.getElementById('profileFullName');
    const inEmail = document.getElementById('profileEmail');
    if (inName) inName.value = user.name;
    if (inEmail) inEmail.value = user.email;
}

// ----------------------------------------------------
// CHANGE PASSWORD
// ----------------------------------------------------
async function handlePasswordChangeSubmit(event) {
    event.preventDefault();
    const current_password = document.getElementById('currentPassword').value;
    const new_password = document.getElementById('newPassword').value;
    const confirm_password = document.getElementById('confirmPassword').value;
    const btn = document.getElementById('savePasswordBtn');

    if (new_password !== confirm_password) {
        showModalNotice('New passwords do not match. Please verify.', true);
        return;
    }

    if (new_password.length < 4) {
        showModalNotice('New password must be at least 4 characters long.', true);
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Updating...';
    }

    try {
        const res = await fetch('/api/user/password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current_password, new_password, confirm_password })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showModalNotice('Password updated successfully!', false);
            showToast('Password changed successfully!', 'success');
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
        } else {
            showModalNotice(data.error || 'Failed to update password.', true);
            showToast(data.error || 'Password update failed.', 'error');
        }
    } catch (err) {
        showModalNotice('Connection error. Please try again.', true);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Update Password';
        }
    }
}

// ----------------------------------------------------
// AI SETTINGS STATUS & SAVE KEY
// ----------------------------------------------------
async function checkSettingsStatus() {
    try {
        const res = await fetch('/api/settings/status');
        const data = await res.json();
        const badge = document.getElementById('modalProviderBadge');
        if (badge) {
            if (data.configured) {
                badge.className = 'badge-status-online';
                badge.textContent = `${data.active_provider.toUpperCase()} Connected (${data.masked_key})`;
            } else {
                badge.className = 'badge-status-offline';
                badge.textContent = 'Offline Engine (No Key)';
            }
        }
    } catch (e) {
        console.error(e);
    }
}

async function saveSettingsKey() {
    const input = document.getElementById('settingsApiKey');
    const api_key = input ? input.value.trim() : '';
    if (!api_key) {
        showModalNotice('API key cannot be empty.', true);
        return;
    }

    try {
        const res = await fetch('/api/settings/key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            showModalNotice(data.message, false);
            showToast(data.message, 'success');
            input.value = '';
            checkSettingsStatus();
        } else {
            showModalNotice(data.error || 'Failed to verify key.', true);
        }
    } catch (e) {
        showModalNotice('Connection error verifying key.', true);
    }
}

// ----------------------------------------------------
// TOAST NOTIFICATIONS
// ----------------------------------------------------
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3800);
}

// ----------------------------------------------------
// TEXT-TO-SPEECH WORD AUDIO PRONUNCIATION
// ----------------------------------------------------
function playWordAudio(word) {
    if (!('speechSynthesis' in window)) {
        showToast('Audio speech is not supported in this browser.', 'warning');
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1.0;

    window.speechSynthesis.speak(utterance);
    showToast(`Pronouncing: "${word}" 🔊`);
}

// ----------------------------------------------------
// GUEST AUTH MODAL (LOGIN & REGISTER)
// ----------------------------------------------------
let authModalMode = 'login';

function openAuthModal(mode = 'login') {
    const modal = document.getElementById('authModal');
    if (modal) {
        setAuthModalMode(mode);
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
    }
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }
}

function setAuthModalMode(mode) {
    authModalMode = mode;
    const title = document.getElementById('authModalTitle');
    const subtitle = document.getElementById('authModalSubtitle');
    const nameGroup = document.getElementById('authNameGroup');
    const submitBtn = document.getElementById('authSubmitBtn');
    const togglePrompt = document.getElementById('authTogglePrompt');
    const toggleBtn = document.getElementById('authToggleBtn');
    const errorDiv = document.getElementById('authModalError');

    if (errorDiv) errorDiv.style.display = 'none';

    if (authModalMode === 'register') {
        if (title) title.textContent = 'Create Student Account';
        if (subtitle) subtitle.textContent = 'Register to track your conversation history and interview scores.';
        if (nameGroup) nameGroup.style.display = 'block';
        if (submitBtn) submitBtn.textContent = 'Create Account & Enter';
        if (togglePrompt) togglePrompt.textContent = 'Already have an account?';
        if (toggleBtn) toggleBtn.textContent = 'Sign In here';
    } else {
        if (title) title.textContent = 'Student Sign In';
        if (subtitle) subtitle.textContent = 'Sign in to view your practice statistics and saved words.';
        if (nameGroup) nameGroup.style.display = 'none';
        if (submitBtn) submitBtn.textContent = 'Sign In to Dashboard';
        if (togglePrompt) togglePrompt.textContent = "Don't have an account yet?";
        if (toggleBtn) toggleBtn.textContent = 'Create Account';
    }
}

function toggleAuthModalMode() {
    const nextMode = authModalMode === 'login' ? 'register' : 'login';
    setAuthModalMode(nextMode);
}

async function handleAuthSubmit(event) {
    event.preventDefault();
    const errorDiv = document.getElementById('authModalError');
    const submitBtn = document.getElementById('authSubmitBtn');
    const email = (document.getElementById('studentEmail').value || '').trim();
    const password = document.getElementById('studentPassword').value || '';
    const nameInput = document.getElementById('studentName');
    const name = nameInput ? nameInput.value.trim() : '';

    if (errorDiv) errorDiv.style.display = 'none';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
    }

    const endpoint = authModalMode === 'register' ? '/register' : '/login';
    const payload = authModalMode === 'register' ? { name, email, password } : { email, password };

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            closeAuthModal();
            const welcomeName = data.user && data.user.name ? data.user.name : 'Student';
            showToast(authModalMode === 'register' ? `Welcome, ${welcomeName}! Account created.` : `Welcome back, ${welcomeName}!`, 'success');
            setTimeout(() => {
                window.location.href = data.redirect || '/dashboard';
            }, 600);
        } else {
            if (errorDiv) {
                errorDiv.textContent = data.error || 'Authentication failed. Please verify your details.';
                errorDiv.style.display = 'block';
            }
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = authModalMode === 'register' ? 'Create Account & Enter' : 'Sign In to Dashboard';
            }
        }
    } catch (err) {
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.style.display = 'block';
        }
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = authModalMode === 'register' ? 'Create Account & Enter' : 'Sign In to Dashboard';
        }
    }
}
