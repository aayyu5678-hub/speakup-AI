document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
});

function initMobileNav() {
    const btn = document.getElementById('mobileMenuBtn');
    const drawer = document.getElementById('mobileDrawer');

    if (btn && drawer) {
        btn.addEventListener('click', () => {
            const isOpen = drawer.classList.contains('open');
            if (isOpen) {
                drawer.classList.remove('open');
                btn.classList.remove('active');
                btn.setAttribute('aria-expanded', 'false');
            } else {
                drawer.classList.add('open');
                btn.classList.add('active');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    }
}

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

window.addEventListener('click', (event) => {
    const authModal = document.getElementById('authModal');
    if (event.target === authModal) closeAuthModal();
});

window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeAuthModal();
    }
});

function playWordAudio(word) {
    if (!('speechSynthesis' in window)) {
        showToast('Audio speech is not supported in this browser.');
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
