/**
 * ════════════════════════════════════════════════════════════════════
 * CODEREFINE - Frontend Router System
 * ════════════════════════════════════════════════════════════════════
 * 
 * Handles:
 * - Page routing by user role (Guest, User, Admin)
 * - Navigation menu rendering
 * - Route protection and redirects
 * - Dynamic page loading
 * - State management
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ROUTE DEFINITIONS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const ROUTES = {
    // ┌─────────────────────────────────────────┐
    // │ PUBLIC ROUTES - No Authentication       │
    // └─────────────────────────────────────────┘
    landing: {
        path: '/landing.html',
        title: 'Welcome to CodeRefine',
        icon: 'home',
        requiresAuth: false,
        public: true
    },
    login: {
        path: '/login.html',
        title: 'Login',
        icon: 'log-in',
        requiresAuth: false,
        public: true
    },
    signup: {
        path: '/signup.html',
        title: 'Sign Up',
        icon: 'user-plus',
        requiresAuth: false,
        public: true
    },
    help: {
        path: '/help.html',
        title: 'Help & Documentation',
        icon: 'help-circle',
        requiresAuth: false,
        public: true
    },
    notFound: {
        path: '/404.html',
        title: '404 - Not Found',
        requiresAuth: false,
        public: true
    },
    
    // ┌─────────────────────────────────────────┐
    // │ USER ROUTES - Authentication Required   │
    // └─────────────────────────────────────────┘
    app: {
        path: '/index.html',
        title: 'Code Review Tool',
        icon: 'code',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    dashboard: {
        path: '/dashboard.html',
        title: 'Dashboard',
        icon: 'bar-chart-2',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    profile: {
        path: '/profile.html',
        title: 'Profile',
        icon: 'user',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    settings: {
        path: '/settings.html',
        title: 'Settings',
        icon: 'settings',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    generate: {
        path: '/generate.html',
        title: 'Generate',
        icon: 'zap',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    batch: {
        path: '/batch.html',
        title: 'Batch Processing',
        icon: 'upload',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    collab: {
        path: '/collab.html',
        title: 'Collaboration',
        icon: 'share-2',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    reports: {
        path: '/reports.html',
        title: 'Reports',
        icon: 'file-text',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    
    // ┌─────────────────────────────────────────┐
    // │ ADMIN ROUTES - Admin Only               │
    // └─────────────────────────────────────────┘
    admin: {
        path: '/admin.html',
        title: 'Admin Panel',
        icon: 'shield',
        requiresAuth: true,
        roles: ['admin']
    },
    status: {
        path: '/status.html',
        title: 'System Status',
        icon: 'activity',
        requiresAuth: true,
        roles: ['admin']
    }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// NAVIGATOR MENUS BY ROLE
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const NAVIGATION_MENUS = {
    guest: [
        { name: 'Home', route: 'landing', icon: 'home' },
        { name: 'Login', route: 'login', icon: 'log-in' },
        { name: 'Sign Up', route: 'signup', icon: 'user-plus' },
        { name: 'Help', route: 'help', icon: 'help-circle' }
    ],
    user: [
        { name: 'App', route: 'app', icon: 'code' },
        { name: 'Dashboard', route: 'dashboard', icon: 'bar-chart-2' },
        { name: 'Generate', route: 'generate', icon: 'zap' },
        { name: 'Batch', route: 'batch', icon: 'upload' },
        { name: 'Collaborate', route: 'collab', icon: 'share-2' },
        { name: 'Reports', route: 'reports', icon: 'file-text' },
        { name: 'Profile', route: 'profile', icon: 'user', divider: true },
        { name: 'Settings', route: 'settings', icon: 'settings' }
    ],
    admin: [
        { name: 'App', route: 'app', icon: 'code' },
        { name: 'Dashboard', route: 'dashboard', icon: 'bar-chart-2' },
        { name: 'Admin', route: 'admin', icon: 'shield', divider: true },
        { name: 'System Status', route: 'status', icon: 'activity' },
        { name: 'Profile', route: 'profile', icon: 'user', divider: true },
        { name: 'Settings', route: 'settings', icon: 'settings' }
    ]
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ROUTER CLASS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Router {
    constructor() {
        this.currentRoute = null;
        this.currentUser = null;
        this.history = [];
        this.init();
    }

    /**
     * Initialize router
     * - Check authentication
     * - Setup event listeners
     * - Handle initial route
     */
    init() {
        this.checkAuth();
        this.setupEventListeners();
        this.handleInitialRoute();
        this.renderNavigation();
    }

    /**
     * Check if user is authenticated
     * - Read from localStorage
     * - Validate token (optional)
     */
    checkAuth() {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');

        if (token && userData) {
            try {
                this.currentUser = JSON.parse(userData);
                console.log('✅ User authenticated:', this.currentUser);
            } catch (e) {
                console.error('❌ Invalid user data:', e);
                this.logout();
            }
        } else {
            this.currentUser = { role: 'guest', username: 'guest' };
            console.log('👤 Guest user');
        }
    }

    /**
     * Setup navigation click handlers
     */
    setupEventListeners() {
        // Handle history back/forward
        window.addEventListener('popstate', () => {
            this.handleRoute(window.location.pathname);
        });

        // Handle navigation clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('[data-route]');
            if (link) {
                e.preventDefault();
                const route = link.dataset.route;
                this.navigate(route);
            }
        });
    }

    /**
     * Navigate to route with validation
     */
    navigate(routeName) {
        const route = ROUTES[routeName];

        if (!route) {
            console.warn('❌ Route not found:', routeName);
            this.navigate('notFound');
            return;
        }

        // Check authentication
        if (route.requiresAuth && !this.isAuthenticated()) {
            console.warn('🔒 Route requires authentication');
            this.navigate('login');
            return;
        }

        // Check role access
        if (route.roles && !route.roles.includes(this.currentUser.role)) {
            console.warn('🚫 Access denied for role:', this.currentUser.role);
            this.navigate('notFound');
            return;
        }

        this.loadRoute(routeName, route);
    }

    /**
     * Load and render route
     */
    loadRoute(routeName, route) {
        this.currentRoute = routeName;
        this.history.push(routeName);

        // Update page title
        document.title = `${route.title} | CodeRefine`;

        // Update active navigation
        this.updateActiveNav(routeName);

        // Emit custom event
        window.dispatchEvent(new CustomEvent('routeChange', {
            detail: { route: routeName, routeConfig: route, user: this.currentUser }
        }));

        console.log('📄 Navigated to:', routeName);
    }

    /**
     * Handle route from URL
     */
    handleRoute(pathname) {
        // Extract route name from path
        const routeName = Object.keys(ROUTES).find(name => {
            return ROUTES[name].path === pathname || 
                   pathname.includes(ROUTES[name].path.replace('/', ''));
        });

        if (routeName) {
            this.navigate(routeName);
        } else {
            this.navigate('notFound');
        }
    }

    /**
     * Handle initial page load
     */
    handleInitialRoute() {
        const pathname = window.location.pathname || '/';
        
        if (pathname === '/' || pathname === '') {
            // Redirect based on user role
            const defaultRoute = this.isAuthenticated() ? 'app' : 'landing';
            this.navigate(defaultRoute);
        } else {
            this.handleRoute(pathname);
        }
    }

    /**
     * Render navigation menu based on user role
     */
    renderNavigation() {
        const navContainer = document.getElementById('nav-menu');
        if (!navContainer) return;

        const role = this.currentUser.role;
        const menu = NAVIGATION_MENUS[role] || NAVIGATION_MENUS.guest;

        navContainer.innerHTML = menu.map(item => `
            <a href="#" data-route="${item.route}" 
               class="nav-item ${item.divider ? 'divider' : ''}"
               title="${ROUTES[item.route]?.title}">
                <i class="icon" data-icon="${item.icon}"></i>
                <span>${item.name}</span>
            </a>
        `).join('');

        this.attachNavListeners();
    }

    /**
     * Attach click listeners to nav items
     */
    attachNavListeners() {
        document.querySelectorAll('[data-route]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigate(link.dataset.route);
            });
        });
    }

    /**
     * Update active navigation indicator
     */
    updateActiveNav(routeName) {
        document.querySelectorAll('[data-route]').forEach(link => {
            link.classList.toggle('active', link.dataset.route === routeName);
        });
    }

    /**
     * Login user
     */
    login(userData, token) {
        this.currentUser = userData;
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('token', token);
        
        this.renderNavigation();
        this.navigate('app');
        
        console.log('✅ Login successful:', userData);
    }

    /**
     * Logout user
     */
    logout() {
        this.currentUser = { role: 'guest', username: 'guest' };
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        
        this.renderNavigation();
        this.navigate('landing');
        
        console.log('👋 Logout successful');
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return this.currentUser && this.currentUser.role !== 'guest';
    }

    /**
     * Check if user is admin
     */
    isAdmin() {
        return this.isAuthenticated() && this.currentUser.role === 'admin';
    }

    /**
     * Get current user role
     */
    getRole() {
        return this.currentUser?.role || 'guest';
    }

    /**
     * Get navigation menu for current user role
     */
    getNavigation() {
        const role = this.getRole();
        return NAVIGATION_MENUS[role] || NAVIGATION_MENUS.guest;
    }

    /**
     * Check if user can access route
     */
    canAccessRoute(routeName) {
        const route = ROUTES[routeName];
        if (!route) return false;
        
        if (route.requiresAuth && !this.isAuthenticated()) return false;
        if (route.roles && !route.roles.includes(this.getRole())) return false;
        
        return true;
    }

    /**
     * Get available routes for user
     */
    getAvailableRoutes() {
        return Object.entries(ROUTES)
            .filter(([name, route]) => this.canAccessRoute(name))
            .reduce((acc, [name, route]) => {
                acc[name] = route;
                return acc;
            }, {});
    }
}

// ════════════════════════════════════════════════════════════════════
// INITIALIZE ROUTER
// ════════════════════════════════════════════════════════════════════

// Create global router instance
window.router = new Router();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Router, ROUTES, NAVIGATION_MENUS };
}
