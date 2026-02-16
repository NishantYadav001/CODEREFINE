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

export const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
};

export const setLoading = (id, isLoading, text = null) => {
    const el = get(id);
    if (!el) return;
    
    if (isLoading) {
        el.dataset.originalContent = el.innerHTML;
        el.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> ${text || ''}`;
        el.disabled = true;
        el.classList.add('opacity-70', 'cursor-not-allowed');
    } else {
        el.innerHTML = el.dataset.originalContent || el.innerHTML;
        el.disabled = false;
        el.classList.remove('opacity-70', 'cursor-not-allowed');
    }
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