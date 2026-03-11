/**
 * ════════════════════════════════════════════════════════════════════
 * CODEREFINE - Routing Utilities & Helpers
 * ════════════════════════════════════════════════════════════════════
 * 
 * Helper functions for:
 * - Route guards
 * - Permission checking
 * - Navigation rendering
 * - Access control
 */

/**
 * Check if user can access a route
 * @param {string} routeName - Route name to check
 * @param {object} user - User object
 * @returns {boolean} Can access route
 */
function canAccessRoute(routeName, user = window.router?.currentUser) {
    if (!user) return false;
    return window.router?.canAccessRoute(routeName) || false;
}

/**
 * Get all accessible routes for current user
 * @returns {object} Map of accessible routes
 */
function getAccessibleRoutes() {
    return window.router?.getAvailableRoutes() || {};
}

/**
 * Check if current user is admin
 * @returns {boolean}
 */
function isAdmin() {
    return window.router?.isAdmin() || false;
}

/**
 * Check if current user is authenticated
 * @returns {boolean}
 */
function isAuthenticated() {
    return window.router?.isAuthenticated() || false;
}

/**
 * Get current user role
 * @returns {string} User role (guest, user, admin)
 */
function getUserRole() {
    return window.router?.getRole() || 'guest';
}

/**
 * Navigate to route with permission check
 * @param {string} routeName - Route to navigate to
 * @returns {boolean} Navigation success
 */
function navigateTo(routeName) {
    if (window.router?.canAccessRoute(routeName)) {
        window.router.navigate(routeName);
        return true;
    }
    console.warn('❌ Access denied to route:', routeName);
    return false;
}

/**
 * Render element only if user has access
 * @param {Element} element - Element to conditionally render
 * @param {string} requiredRole - Required role (user, admin)
 */
function showIfRole(element, requiredRole) {
    const userRole = getUserRole();
    
    if (Array.isArray(requiredRole)) {
        element.style.display = requiredRole.includes(userRole) ? '' : 'none';
    } else {
        element.style.display = userRole === requiredRole ? '' : 'none';
    }
}

/**
 * Render element only if authenticated
 * @param {Element} element - Element to conditionally render
 * @param {boolean} requireAuth - Should require authentication
 */
function showIfAuthenticated(element, requireAuth = true) {
    element.style.display = isAuthenticated() === requireAuth ? '' : 'none';
}

/**
 * Show element for specific routes only
 * @param {Element} element - Element to conditionally render
 * @param {string|string[]} routeNames - Route name(s)
 */
function showIfRoute(element, routeNames) {
    if (typeof routeNames === 'string') {
        routeNames = [routeNames];
    }
    
    const currentRoute = window.router?.currentRoute;
    element.style.display = routeNames.includes(currentRoute) ? '' : 'none';
}

/**
 * Disable element if user doesn't have permission
 * @param {Element} element - Element to potentially disable
 * @param {string} requiredRole - Required role
 */
function disableIfNoRole(element, requiredRole) {
    const userRole = getUserRole();
    const hasAccess = userRole === requiredRole || userRole === 'admin';
    
    element.disabled = !hasAccess;
    element.classList.toggle('disabled', !hasAccess);
    
    if (!hasAccess) {
        element.title = `Requires ${requiredRole} role`;
    }
}

/**
 * Create navigation button for route
 * @param {string} routeName - Route name
 * @param {string} label - Button label
 * @param {string} icon - Icon name (optional)
 * @returns {Element} Navigation button
 */
function createNavButton(routeName, label, icon = '') {
    const button = document.createElement('a');
    button.href = '#';
    button.dataset.route = routeName;
    button.className = 'nav-link';
    button.textContent = label;
    
    if (icon) {
        const iconEl = document.createElement('i');
        iconEl.className = `icon icon-${icon}`;
        button.insertBefore(iconEl, button.firstChild);
    }
    
    return button;
}

/**
 * Build navigation menu for user
 * @param {string} role - User role
 * @returns {string} HTML for navigation menu
 */
function buildNavigation(role = 'guest') {
    const menuConfig = NAVIGATION_MENUS[role] || NAVIGATION_MENUS.guest;
    
    return menuConfig.map(item => {
        const isDivider = item.divider ? ' divider' : '';
        return `
            <a href="#" data-route="${item.route}" 
               class="nav-item${isDivider}"
               title="${ROUTES[item.route]?.title}">
                <i class="icon" data-icon="${item.icon}"></i>
                <span class="label">${item.name}</span>
            </a>
        `;
    }).join('');
}

/**
 * Check and enforce access control
 * - Redirect if not authenticated
 * - Redirect if role doesn't match
 * - Show access denied message
 */
function enforceRouteAccess(routeName, options = {}) {
    const {
        onAccessDenied = () => window.location.href = '/landing.html',
        onUnauthenticated = () => window.location.href = '/login.html'
    } = options;

    const route = ROUTES[routeName];
    if (!route) return false;

    // Check authentication
    if (route.requiresAuth && !isAuthenticated()) {
        onUnauthenticated();
        return false;
    }

    // Check role
    if (route.roles && !route.roles.includes(getUserRole())) {
        onAccessDenied();
        return false;
    }

    return true;
}

/**
 * Create breadcrumb navigation
 * @returns {string} HTML for breadcrumbs
 */
function getBreadcrumbs() {
    const route = window.router?.currentRoute;
    const routeConfig = ROUTES[route];

    return `
        <nav class="breadcrumbs">
            <a href="#" data-route="landing">Home</a>
            ${route && route !== 'landing' ? `
                <span class="separator">/</span>
                <span class="current">${routeConfig?.title || route}</span>
            ` : ''}
        </nav>
    `;
}

/**
 * Get route metadata
 * @param {string} routeName - Route name
 * @returns {object} Route configuration
 */
function getRouteInfo(routeName) {
    return ROUTES[routeName] || null;
}

/**
 * Add permission guard to element
 * @param {Element} element - Element to guard
 * @param {string} permission - Required permission
 * @param {function} callback - Callback if access denied
 */
function addPermissionGuard(element, permission, callback) {
    if (!hasPermission(permission)) {
        element.style.display = 'none';
        element.dataset.hidden = 'permission-denied';
        
        if (callback) {
            callback(element, permission);
        }
    }
}

/**
 * Check if user has specific permission
 * @param {string} permission - Permission to check
 * @returns {boolean}
 */
function hasPermission(permission) {
    const role = getUserRole();
    const permissions = {
        'guest': [],
        'user': ['can_review', 'can_read', 'can_generate', 'can_save'],
        'admin': ['can_review', 'can_read', 'can_generate', 'can_save', 'can_manage', 'can_delete']
    };
    
    return permissions[role]?.includes(permission) || false;
}

// ════════════════════════════════════════════════════════════════════
// EXPORT FUNCTIONS
// ════════════════════════════════════════════════════════════════════

window.routingUtils = {
    canAccessRoute,
    getAccessibleRoutes,
    isAdmin,
    isAuthenticated,
    getUserRole,
    navigateTo,
    showIfRole,
    showIfAuthenticated,
    showIfRoute,
    disableIfNoRole,
    createNavButton,
    buildNavigation,
    enforceRouteAccess,
    getBreadcrumbs,
    getRouteInfo,
    addPermissionGuard,
    hasPermission
};
