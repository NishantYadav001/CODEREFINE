/**
 * BaseLayout & Layout Logic
 * Handles role-specific layout adjustments (Whitespace vs Data Density).
 */
const BaseLayout = {
    init() {
        // Wait for AuthGuard to be ready if needed, or check storage directly
        const role = this.getUserRole();
        this.applyLayout(role);
    },

    getUserRole() {
        // Helper to get role without depending on AuthGuard being fully loaded
        try {
            const token = localStorage.getItem('access_token');
            if (!token) return 'guest';
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
            return JSON.parse(jsonPayload).role || 'user';
        } catch (e) {
            return 'guest';
        }
    },

    applyLayout(role) {
        const body = document.body;
        
        // 4. Role-Specific UI Logic
        if (role === 'guest') {
            // Guest: Focus on Whitespace
            body.style.backgroundColor = '#FFFFFF'; // Pure White
            body.classList.add('layout-guest');
            // Ensure large typography for landing pages
            document.documentElement.style.setProperty('--content-max-width', '1200px');
        } else {
            // User/Admin: Focus on Data Density
            body.style.backgroundColor = role === 'admin' ? '#F3F4F6' : '#F9FAFB'; // Light Gray
            body.classList.add('layout-app');
            
            // Add a wrapper class for density if not present
            const main = document.querySelector('main');
            if (main) {
                main.classList.add('max-w-7xl', 'mx-auto', 'px-4', 'sm:px-6', 'lg:px-8', 'py-6');
            }
        }
    }
};

// Auto-init on load
document.addEventListener('DOMContentLoaded', () => {
    BaseLayout.init();
});