# CODEREFINE - Comprehensive Routing & Navigation Guide

**Version**: 2.0.0  
**Date**: February 19, 2026  
**Status**: ✅ Complete Routing System

---

## Table of Contents
1. [Overview](#overview)
2. [User Types & Access](#user-types--access)
3. [Route Structure](#route-structure)
4. [Backend Routing](#backend-routing)
5. [Frontend Routing](#frontend-routing)
6. [Access Control](#access-control)
7. [Navigation Flow](#navigation-flow)
8. [Implementation Examples](#implementation-examples)
9. [API Endpoints](#api-endpoints)

---

## Overview

CODEREFINE implements a comprehensive role-based routing system that provides different experiences for three user types:

```
┌─────────────────────────────────────────────────┐
│         CODEREFINE ROUTING ARCHITECTURE         │
├─────────────────────────────────────────────────┤
│ Guest User (No Auth)                            │
│ ├─ Landing Page                                 │
│ ├─ Login Page                                   │
│ ├─ Sign Up Page                                 │
│ └─ Help/Documentation                           │
├─────────────────────────────────────────────────┤
│ Authorized User (JWT Token Required)            │
│ ├─ Main Application                             │
│ ├─ Dashboard & Analytics                        │
│ ├─ Generate & Refactor                          │
│ ├─ Batch Processing                             │
│ ├─ Collaboration                                │
│ ├─ Reports                                      │
│ ├─ Profile Management                           │
│ └─ User Settings                                │
├─────────────────────────────────────────────────┤
│ Admin User (JWT Token + Admin Role)             │
│ ├─ All User Routes                              │
│ ├─ Admin Panel                                  │
│ ├─ System Status                                │
│ ├─ User Management                              │
│ ├─ Audit Logs                                   │
│ ├─ System Configuration                         │
│ └─ Infrastructure Monitoring                    │
└─────────────────────────────────────────────────┘
```

---

## User Types & Access

### 1. Guest User 👤

**Authentication**: None required  
**Characteristics**:
- No login needed
- Limited feature access
- Daily request limit: 5
- Rate limited for fair usage
- Demo/trial experience

**Access**:
- Landing page
- Login/Sign up pages
- Help documentation
- Limited code review (3 requests)
- Cannot save code
- Cannot generate code

**Pages Accessible**:
```
/ or /landing.html          Landing/Home page
/login.html                 Login form
/signup.html                Registration form
/help.html                  Documentation
/404.html                   Error pages
```

### 2. Authorized User 👨‍💻

**Authentication**: JWT Token in Authorization header  
**Characteristics**:
- Full authentication required
- Complete feature access
- Daily request limit: 100
- Storage: 100 MB
- Premium features

**Access**:
- All guest routes
- Code review (unlimited)
- Code generation
- Auto-refactoring
- Batch processing
- File upload (up to 5MB)
- Project history
- Collaboration features
- Report generation
- User dashboard
- Settings & preferences

**Pages Accessible**:
```
/index.html or /app         Main application
/dashboard.html             Statistics & analytics
/generate.html              Code generation
/batch.html                 Bulk file processing
/collab.html                Team collaboration
/reports.html               Report generation & export
/profile.html               User profile management
/settings.html              User preferences
```

### 3. Admin User 👨‍💼

**Authentication**: JWT Token + Admin Role  
**Characteristics**:
- Full system access
- User management capabilities
- System configuration
- Audit log access
- Unlimited resources

**Access**:
- All authorized user routes
- User management (CRUD)
- System configuration
- Audit logs & monitoring
- API key management
- Maintenance mode
- System health dashboard
- Analytics & reports
- Database management

**Pages Accessible**:
```
(All user routes) +
/admin.html                 Admin panel
/status.html                System status
```

---

## Route Structure

### File Organization

#### Backend Routes Configuration
```
backend/
├── routes_config.py         # Route definitions & permissions
├── dependencies.py          # Authentication & RBAC middleware
├── main.py                  # API endpoints
└── [router modules]         # (Future: split from main.py)
```

#### Frontend Routes Configuration
```
frontend/
├── router.js                # Main routing logic
├── routing-utils.js         # Helper functions
├── index.html               # SPA container
├── [pages]/
│   ├── landing.html         # Welcome page
│   ├── login.html           # Authentication
│   ├── signup.html          # Registration
│   ├── index.html (app)     # Main tool
│   ├── dashboard.html       # Analytics
│   ├── admin.html           # Admin panel
│   └── [other pages]
└── [assets]/
    └── [static files]
```

---

## Backend Routing

### Route Configuration (routes_config.py)

```python
# Route definition structure
GUEST_ROUTES = {
    'landing': {
        'path': '/landing.html',
        'title': 'Welcome to CodeRefine',
        'requires_auth': False,
        'rate_limited': True,
        'daily_limit': 5
    }
}

USER_ROUTES = {
    'app': {
        'path': '/index.html',
        'title': 'Code Review Tool',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['review', 'generate', 'run', 'refactor']
    }
}

ADMIN_ROUTES = {
    'admin': {
        'path': '/admin.html',
        'title': 'Admin Panel',
        'requires_auth': True,
        'required_role': 'admin',
        'features': ['user_management', 'system_settings']
    }
}
```

### API Endpoints by Role

#### Public Endpoints (No Auth)
```
POST   /api/auth/login                      User login
POST   /api/auth/signup                     User registration
GET    /api/health                          Health check
GET    /api/routes/config                   Get route config (new)
```

#### User Endpoints (Authenticated)
```
POST   /api/code/review                     Code review
POST   /api/code/generate                   Generate code
POST   /api/code/refactor                   Refactor code
GET    /api/user/profile                    Get profile
PUT    /api/user/profile                    Update profile
GET    /api/user/history                    Get code history
POST   /api/user/logout                     Logout
```

#### Admin Endpoints (Admin Only)
```
GET    /api/admin/users                     List users
POST   /api/admin/users                     Create user
DELETE /api/admin/users/{id}                Delete user
GET    /api/admin/dashboard                 Admin dashboard
GET    /api/admin/audit-logs                Audit logs
PUT    /api/admin/settings                  System settings
```

### Authentication Middleware

```python
# Enhanced dependency injection

# Check current user
@get_current_user
async def my_endpoint(user: dict = Depends(get_current_user)):
    pass

# Admin only
@get_current_admin
async def admin_endpoint(user: dict = Depends(get_current_admin)):
    pass

# Require specific role
@require_role('user')
async def user_endpoint(user: dict = Depends(require_role('user'))):
    pass

# Multiple roles
@require_any_role('user', 'moderator')
async def endpoint(user: dict = Depends(require_any_role('user', 'moderator'))):
    pass

# Check permission
@require_permission('can_review')
async def review(user: dict = Depends(require_permission('can_review'))):
    pass
```

---

## Frontend Routing

### Router Class (router.js)

```javascript
// Initialize router
window.router = new Router();

// Router provides:
// - Route validation
// - Authentication checks
// - Role-based access control
// - Navigation management
// - Event system

// Key methods:
router.navigate(routeName)              // Navigate to route
router.login(userData, token)           // Login user
router.logout()                         // Logout user
router.isAuthenticated()                // Check auth status
router.isAdmin()                        // Check admin status
router.getRole()                        // Get user role
router.canAccessRoute(routeName)        // Check route access
router.getAvailableRoutes()             // Get all accessible routes
```

### Route Definitions (router.js)

```javascript
const ROUTES = {
    // Public routes
    landing: {
        path: '/landing.html',
        title: 'Welcome to CodeRefine',
        requiresAuth: false,
        public: true
    },
    
    // Protected routes
    app: {
        path: '/index.html',
        title: 'Code Review Tool',
        requiresAuth: true,
        roles: ['user', 'admin']
    },
    
    // Admin only
    admin: {
        path: '/admin.html',
        title: 'Admin Panel',
        requiresAuth: true,
        roles: ['admin']
    }
};
```

### Navigation Menus (router.js)

```javascript
const NAVIGATION_MENUS = {
    guest: [
        { name: 'Home', route: 'landing' },
        { name: 'Login', route: 'login' },
        { name: 'Sign Up', route: 'signup' },
        { name: 'Help', route: 'help' }
    ],
    
    user: [
        { name: 'App', route: 'app' },
        { name: 'Dashboard', route: 'dashboard' },
        { name: 'Generate', route: 'generate' },
        { name: 'Profile', route: 'profile' },
        { name: 'Settings', route: 'settings' }
    ],
    
    admin: [
        { name: 'App', route: 'app' },
        { name: 'Dashboard', route: 'dashboard' },
        { name: 'Admin', route: 'admin' },
        { name: 'System Status', route: 'status' },
        { name: 'Settings', route: 'settings' }
    ]
};
```

---

## Access Control

### Role-Based Access Control (RBAC)

```javascript
// Permission matrix
const PERMISSION_MATRIX = {
    'guest': {
        'routes': ['landing', 'login', 'signup', 'help'],
        'can_review': false,
        'can_generate': false,
        'daily_requests': 5
    },
    'user': {
        'routes': ['app', 'dashboard', 'profile', ...],
        'can_review': true,
        'can_generate': true,
        'daily_requests': 100,
        'storage': 100
    },
    'admin': {
        'routes': [all routes],
        'can_manage_users': true,
        'can_manage_system': true,
        'daily_requests': -1  // unlimited
    }
};
```

### Frontend Guards (routing-utils.js)

```javascript
// Check role-based access
showIfRole(element, 'admin')              // Show only for admin
showIfAuthenticated(element)              // Show if logged in
showIfRoute(element, 'dashboard')         // Show on specific route
disableIfNoRole(element, 'user')          // Disable without role

// Check permissions
hasPermission('can_review')               // Has permission?
isAdmin()                                 // Is admin?
isAuthenticated()                         // Is logged in?
canAccessRoute('admin')                   // Can access route?
```

---

## Navigation Flow

### Guest User Flow
```
Landing Page
    ↓
[Demo] or [Login] or [Sign Up]
    ↓
(Limited 5 requests per day)
    ↓
Can try: Code Review (limited)
Cannot: Generate, Save, Batch, etc
    ↓
Prompt to Sign Up
```

### User Registration Flow
```
Sign Up →
  Validate Email →
  Create Account →
  Generate JWT Token →
  Redirect to App →
  Full Access
```

### Login Flow
```
Landing / Login Page
    ↓
Enter Credentials
    ↓
Backend Validates
    ↓
Generate JWT Token
    ↓
Store in localStorage
    ↓
Redirect to /app
    ↓
Router loads authenticated menu
    ↓
Full user features available
```

### Admin Access Flow
```
Login with Admin Account
    ↓
Backend Returns role: 'admin'
    ↓
JWT contains admin role
    ↓
Frontend Router detects admin
    ↓
Shows Admin Menu Items
    ↓
Admin Panel accessible at /admin
    ↓
All management features enabled
```

### Page Transition Flow
```
User navigates in UI
    ↓
Router.navigate(routeName)
    ↓
Check authentication (if required)
    ↓
Check role authorization
    ↓
Load route if permitted
    ↓
Emit 'routeChange' event
    ↓
Update page title & nav menu
    ↓
(In future: Load page content dynamically)
```

---

## Implementation Examples

### Example 1: Protected Admin-Only Button

**HTML**:
```html
<button id="admin-button" data-route="admin">
    Admin Panel
</button>
```

**JavaScript**:
```javascript
const button = document.getElementById('admin-button');
button.addEventListener('click', () => {
    if (router.canAccessRoute('admin')) {
        router.navigate('admin');
    } else {
        showToast('Admin access required', 'error');
    }
});

// OR conditionally hide
showIfRole(button, 'admin');
```

### Example 2: Conditional Navigation Menu

```javascript
// Render menu based on role
const menu = buildNavigation(router.getRole());
document.getElementById('nav-container').innerHTML = menu;

// Re-render on login
window.addEventListener('login', (e) => {
    const menu = buildNavigation(e.detail.role);
    document.getElementById('nav-container').innerHTML = menu;
});
```

### Example 3: Route Guard in Page

```javascript
// Enforce access control on page load
if (!enforceRouteAccess('dashboard')) {
    // User doesn't have access
    // Will redirect automatically
}

// Custom handling
if (!enforceRouteAccess('admin', {
    onAccessDenied: () => {
        showToast('You must be an admin', 'error');
        router.navigate('app');
    }
})) {
    // Handle denied access
}
```

### Example 4: Conditional Features

```javascript
// Show feature only if user can use it
const generateButton = document.getElementById('generate-btn');
showIfRole(generateButton, ['user', 'admin']);

// Disable without permission
const reviewButton = document.getElementById('review-btn');
disableIfNoRole(reviewButton, 'user');

// Show upgrade prompt for guests
const upgradePrompt = document.getElementById('upgrade-prompt');
showIfRole(upgradePrompt, 'guest');
```

---

## API Endpoints

### New Endpoint: Get Route Configuration

```
GET /api/routes/config
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "routes": { ...all accessible routes... },
        "navigation": [ ...menu items... ],
        "permissions": { ...user permissions... },
        "role": "user",
        "username": "john_doe"
    }
}
```

### New Endpoint: Check Route Access

```
POST /api/routes/check
Authorization: Bearer <token>

Body:
{
    "route": "admin"
}

Response:
{
    "success": true,
    "can_access": false,
    "required_role": "admin",
    "current_role": "user"
}
```

---

## Benefits of This Routing System

### 1. **Security**
- ✅ JWT-based authentication
- ✅ Role-based access control
- ✅ Rate limiting for guests
- ✅ Protected API endpoints
- ✅ Secure session management

### 2. **User Experience**
- ✅ Seamless navigation
- ✅ Context-aware menus
- ✅ Clear access restrictions
- ✅ Smart redirects
- ✅ Guest trial experience

### 3. **Maintainability**
- ✅ Centralized route definitions
- ✅ Consistent RBAC patterns
- ✅ Easy to add new routes
- ✅ Clear role permissions
- ✅ Audit trail support

### 4. **Scalability**
- ✅ Support for new roles
- ✅ Dynamic permissions
- ✅ Multi-tenant ready
- ✅ Role hierarchy support
- ✅ Custom permission system

---

## Future Enhancements

### Phase 1: SPA Implementation
- [ ] Dynamic page loading (no full refresh)
- [ ] State persistence
- [ ] Back button support
- [ ] URL-based navigation

### Phase 2: Advanced Features
- [ ] Route transitions/animations
- [ ] Breadcrumb navigation
- [ ] Role hierarchies
- [ ] Dynamic permissions

### Phase 3: Advanced Security
- [ ] Session management
- [ ] Activity tracking
- [ ] Geo-blocking
- [ ] 2FA support

---

## Testing Routes

### Manual Testing Checklist

**Guest Access**:
- [ ] Access landing page without auth
- [ ] Try to access /app (should redirect to login)
- [ ] Try to access /admin (should redirect to login)
- [ ] Can access help page

**User Access**:
- [ ] Login with user account
- [ ] Access /app successfully
- [ ] Access dashboard
- [ ] Cannot access /admin (should see 403)
- [ ] Logout works correctly

**Admin Access**:
- [ ] Login with admin account
- [ ] Access all user routes
- [ ] Access /admin panel
- [ ] Access system status
- [ ] Full permissions granted

---

## File Configuration Reference

| File | Type | Purpose |
|------|------|---------|
| `routes_config.py` | Backend | Route definitions & permissions |
| `dependencies.py` | Backend | Auth & RBAC middleware |
| `router.js` | Frontend | Main routing logic |
| `routing-utils.js` | Frontend | Helper functions |
| `main.py` | Backend | API endpoints (extend) |

---

**Document Version**: 2.0.0  
**Last Updated**: February 19, 2026  
**Status**: ✅ Complete - Ready for Implementation
