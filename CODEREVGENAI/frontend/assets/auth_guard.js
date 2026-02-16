/**
 * AuthGuard - Handles Frontend Authentication, Role Checks, and Navbar Rendering
 */

import { Components } from './components.js';

const AuthGuard = {
    tokenKey: 'access_token',
    userKey: 'user_role',
    
    // Decode JWT to get payload (simple implementation)
    parseJwt(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (e) {
            return null;
        }
    },

    isAuthenticated() {
        return !!localStorage.getItem(this.tokenKey);
    },

    getUserRole() {
        const token = localStorage.getItem(this.tokenKey);
        if (!token) return 'guest';
        const payload = this.parseJwt(token);
        return payload ? (payload.role || 'user') : 'guest';
    },

    // 2. The ProtectedRoute Component (Wrapper Logic)
    ProtectedRoute(requiredRole = null) {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }

        if (requiredRole) {
            const currentRole = this.getUserRole();
            if (currentRole === 'admin') return; // Admin bypass
            if (currentRole !== requiredRole) {
                // Redirect to Unauthorized (403)
                window.location.href = '/unauthorized';
                return false;
            }
        }
        return true;
    },

    // Navbar Logic
    renderNavbar() {
        const navContainer = document.getElementById('navbar-links'); // Ensure your HTML has this ID
        if (!navContainer) return;

        const role = this.getUserRole();
        let links = '';

        // Common Links
        links += `<li><a href="/">Home</a></li>`;

        if (role === 'guest') {
            // Guest View
            links += `
                <li><a href="/login">Login</a></li>
                <li><a href="/signup">Register</a></li>
            `;
        } else {
            // Authenticated User View
            links += `
                <li><a href="/dashboard">Dashboard</a></li>
                <li><a href="/profile">Profile</a></li>
            `;

            // Admin View
            if (role === 'admin') {
                links += `
                    <li><a href="/admin">Admin Panel</a></li>
                `;
            }

            links += `<li><a href="#" onclick="AuthGuard.logout()">Logout</a></li>`;
        }

        navContainer.innerHTML = links;
    },

    logout() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem('username');
        window.location.href = '/login';
    },

    // 1. Route Definitions & Logic
    handleRouting() {
        const path = window.location.pathname;
        const isAuth = this.isAuthenticated();

        // Explicitly allow /generate for everyone
        if (path.startsWith('/generate')) return;

        // Public Routes: Redirect to Dashboard if Logged In
        // Requested: /, /login, /register
        const publicRoutes = ['/', '/login', '/register', '/signup', '/landing'];
        if (publicRoutes.includes(path) && isAuth) {
            window.location.href = '/dashboard';
            return;
        }

        // Admin Routes: Only accessible if user.role === 'admin'
        // Requested: /admin, /admin/users, /admin/analytics
        if (path.startsWith('/admin')) {
            this.ProtectedRoute('admin');
            return;
        }

        // User Routes: Redirect Guest to /login
        // Requested: /dashboard, /profile, /settings
        const userRoutes = ['/dashboard', '/profile', '/settings'];
        if (userRoutes.includes(path)) {
            this.ProtectedRoute();
            return;
        }
    }
};

// Auto-run on load
document.addEventListener('DOMContentLoaded', () => {
    AuthGuard.handleRouting();
    AuthGuard.renderNavbar();
});