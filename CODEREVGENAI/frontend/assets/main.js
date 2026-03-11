const qs = (sel) => document.querySelector(sel);

const getAuth = () => ({
    token: localStorage.getItem('auth_token') || '',
    username: localStorage.getItem('auth_username') || '',
    role: localStorage.getItem('auth_role') || 'user'
});

const setAuth = ({ token, username, role }) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_username', username);
    localStorage.setItem('auth_role', role || 'user');
};

const clearAuth = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_username');
    localStorage.removeItem('auth_role');
};

const setMessage = (el, text, type) => {
    if (!el) return;
    el.textContent = text;
    el.className = `alert ${type === 'success' ? 'alert-success' : 'alert-error'}`;
};

const apiPost = async (url, body, token = '') => {
    const res = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(body)
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const detail = data.detail || 'Request failed';
        throw new Error(detail);
    }
    return data;
};

const mapUserType = (role) => {
    if (role === 'admin') return 'enterprise';
    return 'developer';
};

const requireAuth = () => {
    const { token } = getAuth();
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
};

const initLanding = () => {
    const { token } = getAuth();
    const appLink = qs('[data-app-link]');
    if (token && appLink) {
        appLink.classList.remove('hidden');
    }
};

const initLogin = () => {
    const form = qs('#login-form');
    const msg = qs('#login-msg');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        setMessage(msg, '', 'success');

        const username = qs('#login-username').value.trim();
        const password = qs('#login-password').value.trim();
        if (!username || !password) {
            setMessage(msg, 'Username and password are required.', 'error');
            return;
        }

        try {
            const data = await apiPost('/api/login', { username, password });
            setAuth({ token: data.token, username: data.username, role: data.role });
            window.location.href = '/app';
        } catch (err) {
            setMessage(msg, err.message, 'error');
        }
    });
};

const initSignup = () => {
    const form = qs('#signup-form');
    const msg = qs('#signup-msg');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        setMessage(msg, '', 'success');

        const username = qs('#signup-username').value.trim();
        const email = qs('#signup-email').value.trim();
        const password = qs('#signup-password').value.trim();
        if (!username || !email || !password) {
            setMessage(msg, 'All fields are required.', 'error');
            return;
        }

        try {
            await apiPost('/api/signup', { username, email, password });
            setMessage(msg, 'Account created. Redirecting to login...', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 900);
        } catch (err) {
            setMessage(msg, err.message, 'error');
        }
    });
};

const initApp = () => {
    if (!requireAuth()) return;

    const { username, role } = getAuth();
    const userLabel = qs('#user-label');
    if (userLabel) {
        userLabel.textContent = `${username} (${role})`;
    }

    const codeInput = qs('#code-input');
    const output = qs('#fix-output');
    const msg = qs('#fix-msg');

    const fixBtn = qs('#fix-btn');
    const clearBtn = qs('#clear-btn');
    const copyBtn = qs('#copy-btn');

    if (fixBtn) {
        fixBtn.addEventListener('click', async () => {
            setMessage(msg, '', 'success');
            if (!codeInput || !output) return;
            const code = codeInput.value.trim();
            if (!code) {
                setMessage(msg, 'Paste code to fix first.', 'error');
                return;
            }
            output.textContent = 'Fixing code...';
            try {
                const data = await apiPost('/api/rewrite', {
                    code,
                    user_type: mapUserType(role),
                    username
                });
                output.textContent = data.rewritten_code || 'No output returned.';
            } catch (err) {
                output.textContent = '';
                setMessage(msg, err.message, 'error');
            }
        });
    }

    if (clearBtn && codeInput && output) {
        clearBtn.addEventListener('click', () => {
            codeInput.value = '';
            output.textContent = '';
            setMessage(msg, '', 'success');
        });
    }

    if (copyBtn && output) {
        copyBtn.addEventListener('click', async () => {
            const text = output.textContent.trim();
            if (!text) return;
            await navigator.clipboard.writeText(text);
            setMessage(msg, 'Copied to clipboard.', 'success');
        });
    }

    const logoutBtn = qs('[data-logout]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            clearAuth();
            window.location.href = '/';
        });
    }
};

const initGenerate = () => {
    if (!requireAuth()) return;

    const { username, role } = getAuth();
    const userLabel = qs('#user-label');
    if (userLabel) {
        userLabel.textContent = `${username} (${role})`;
    }

    const promptInput = qs('#prompt-input');
    const langSelect = qs('#language-select');
    const output = qs('#generate-output');
    const msg = qs('#generate-msg');
    const generateBtn = qs('#generate-btn');

    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            setMessage(msg, '', 'success');
            if (!promptInput || !output) return;
            const prompt = promptInput.value.trim();
            if (!prompt) {
                setMessage(msg, 'Enter a prompt first.', 'error');
                return;
            }
            output.textContent = 'Generating code...';
            try {
                const data = await apiPost('/api/generate', {
                    prompt,
                    language: langSelect ? langSelect.value : 'python',
                    role: mapUserType(role),
                    username
                });
                output.textContent = data.generated_code || 'No output returned.';
            } catch (err) {
                output.textContent = '';
                setMessage(msg, err.message, 'error');
            }
        });
    }

    const logoutBtn = qs('[data-logout]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            clearAuth();
            window.location.href = '/';
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.getAttribute('data-page');
    if (page === 'landing') initLanding();
    if (page === 'login') initLogin();
    if (page === 'signup') initSignup();
    if (page === 'app') initApp();
    if (page === 'generate') initGenerate();

    const logoutLinks = document.querySelectorAll('[data-logout]');
    logoutLinks.forEach((btn) => {
        btn.addEventListener('click', () => {
            clearAuth();
            window.location.href = '/';
        });
    });
});
