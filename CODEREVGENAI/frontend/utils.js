export const get = (id) => document.getElementById(id);

export const showToast = (message, type = 'info', duration = 3000) => {
    const container = get('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, duration);
};

export const setClick = (id, handler) => {
    const el = get(id);
    if (el) {
        el.addEventListener('click', async (e) => {
            if (e && e.preventDefault) e.preventDefault();
            try {
                await handler(e);
            } catch (err) {
                console.error(`Error in ${id} handler:`, err);
                showToast(`Error: ${err.message}`, 'error');
            }
        });
    }
};

export const setChange = (id, handler) => {
    const el = get(id);
    if (el) {
        el.addEventListener('change', async (e) => {
            try {
                await handler(e);
            } catch (err) {
                console.error(`Error in ${id} handler:`, err);
            }
        });
    }
};