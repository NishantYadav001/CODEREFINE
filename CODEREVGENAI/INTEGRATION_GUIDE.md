# CODEREFINE - Integration Guide

**Version**: 1.0.0  
**Date**: February 19, 2026  
**Status**: ✅ Step-by-Step Implementation Guide

---

## Introduction

This guide walks you through integrating the new routing system into your existing CODEREFINE application. The routing system was built modularly to require minimal changes to your existing code while providing significant organizational improvements.

---

## Quick Start (5 Minutes)

### What's Been Created?

```
New Files:
✅ backend/routes_config.py       (200+ lines) - Route definitions
✅ backend/dependencies.py         (200+ lines) - Enhanced RBAC
✅ frontend/router.js              (350+ lines) - Frontend router
✅ frontend/routing-utils.js       (250+ lines) - UI utilities
✅ ROUTING.md                       (Complete documentation)
```

### What You Need to Do?

1. **Backend**: Update `main.py` to use new routing config
2. **Frontend**: Link new router files in HTML
3. **Test**: Verify routing works across all roles
4. **Deploy**: Push to production

---

## Phase 1: Backend Integration (✅ Easy)

### Step 1: Update main.py imports

**File**: `backend/main.py`

**Add at the top**:
```python
# Add these imports after existing imports
from routes_config import (
    GUEST_ROUTES, USER_ROUTES, ADMIN_ROUTES,
    PERMISSION_MATRIX, NAVIGATION_MENUS,
    get_routes_for_role, can_access_route, 
    get_navigation_for_role, get_default_route
)
```

**Location**: After your existing imports (lines 1-20)

**Before**:
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.cors import CORSMiddleware
# ... other imports ...
```

**After**:
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.cors import CORSMiddleware
# ... other imports ...

# Import new routing configuration
from routes_config import (
    GUEST_ROUTES, USER_ROUTES, ADMIN_ROUTES,
    PERMISSION_MATRIX, NAVIGATION_MENUS,
    get_routes_for_role, can_access_route, 
    get_navigation_for_role, get_default_route
)
```

### Step 2: Update dependencies usage in main.py

**Current Code** (Search in main.py):
```python
@app.post("/api/auth/login")
async def login(credentials: dict):
    # Current implementation
```

**New Code**:
```python
# Replace old auth check with new dependency
from dependencies import get_current_user, require_role

@app.post("/api/auth/login")
async def login(credentials: dict):
    # Now with enhanced JWT support
    # Logic remains the same
```

### Step 3: Add new route configuration endpoints

**Add to main.py** (after existing endpoints):
```python
# New endpoints for routing configuration
@app.get("/api/routes/config")
async def get_routes_config(user: dict = Depends(get_current_user)):
    """Get route configuration for authenticated user"""
    role = user.get("role", "guest")
    return {
        "success": True,
        "data": {
            "routes": get_routes_for_role(role),
            "navigation": get_navigation_for_role(role),
            "permissions": PERMISSION_MATRIX.get(role),
            "role": role,
            "username": user.get("username")
        }
    }

@app.post("/api/routes/check")
async def check_route_access(request: dict):
    """Check if current user can access route"""
    token = request.get("token")  # From Authorization header
    route = request.get("route")
    
    try:
        user = await get_current_user(token)
        role = user.get("role", "guest")
        
        can_access = can_access_route(route, role)
        return {
            "success": True,
            "can_access": can_access,
            "required_role": "admin" if route in ADMIN_ROUTES else "user",
            "current_role": role
        }
    except:
        return {
            "success": False,
            "can_access": False,
            "error": "Unauthorized"
        }

@app.get("/api/routes/navigation")
async def get_navigation(user: dict = Depends(get_optional_user)):
    """Get navigation menu for current user"""
    role = user.get("role", "guest") if user else "guest"
    navigation = get_navigation_for_role(role)
    
    return {
        "success": True,
        "navigation": navigation,
        "role": role
    }
```

### Step 4: Verify dependencies.py is in place

**Check**: Make sure `backend/dependencies.py` is already created with enhanced RBAC functions.

If not already done, the file should contain:
- `get_current_user()` - Validate JWT
- `get_optional_user()` - Allow guests
- `get_current_admin()` - Admin only
- `require_role()` - Factory for roles
- `require_permission()` - Check specific permissions

---

## Phase 2: Frontend Integration (✅ Medium)

### Step 1: Link router files in HTML

**File**: `frontend/index.html` (and other pages)

**Add at the bottom before closing `</body>`**:
```html
    <!-- Add before closing </body> tag -->
    <script src="router.js"></script>
    <script src="routing-utils.js"></script>
    
    <script>
        // Initialize router on page load
        document.addEventListener('DOMContentLoaded', async () => {
            // Create router instance
            window.router = new Router();
            
            // Initialize routing
            await window.router.init();
            
            // Load initial page
            const currentPage = window.location.pathname;
            const routeName = Object.keys(window.router.routes).find(
                route => window.router.routes[route].path === currentPage
            );
            
            if (routeName) {
                window.router.navigate(routeName);
            }
        });
        
        // Listen for route changes
        window.addEventListener('routeChange', (e) => {
            console.log('Route changed to:', e.detail.route);
            // Update UI as needed
        });
    </script>
</body>
```

### Step 2: Update navigation menu

**File**: `frontend/index.html` (Update or create nav section)

**Old HTML**:
```html
<nav>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/login">Login</a></li>
        <!-- Static menu -->
    </ul>
</nav>
```

**New HTML**:
```html
<nav id="main-nav">
    <!-- This will be dynamically populated by router -->
    <ul id="nav-items"></ul>
</nav>

<script>
    // Render navigation after router initialization
    window.addEventListener('routeChange', () => {
        const navContainer = document.getElementById('nav-items');
        const navigation = window.roter.getNavigation();
        
        navContainer.innerHTML = navigation.map(item => 
            `<li><a href="#" onclick="window.router.navigate('${item.route}')">${item.name}</a></li>`
        ).join('');
    });
</script>
```

### Step 3: Add role-based visibility

**File**: Update HTML for admin and protected features

**Pattern**:
```html
<!-- Admin only button -->
<button id="admin-btn" style="display: none;">
    Admin Panel
</button>

<script>
    // Show/hide based on role
    window.routingUtils.showIfRole(
        document.getElementById('admin-btn'),
        'admin'
    );
</script>
```

**Common patterns**:
```html
<!-- Show only for authenticated users -->
<div id="user-menu" style="display: none;">
    <a href="#" onclick="window.router.navigate('profile')">Profile</a>
</div>

<!-- Show only for admins -->
<div id="admin-menu" style="display: none;">
    <a href="#" onclick="window.router.navigate('admin')">Admin Panel</a>
</div>

<!-- Disable without permission -->
<button id="generate-btn" disabled>Generate Code</button>

<script>
    window.routingUtils.showIfAuthenticated(
        document.getElementById('user-menu')
    );
    
    window.routingUtils.showIfRole(
        document.getElementById('admin-menu'),
        'admin'
    );
    
    window.routingUtils.disableIfNoRole(
        document.getElementById('generate-btn'),
        'user'
    );
</script>
```

---

## Phase 3: Frontend Page Linking (✅ Moderate)

### Step 1: Update All HTML Pages

**Add to every HTML file** (landing.html, login.html, admin.html, etc.):

```html
<!-- At the end of <head> -->
<script src="router.js"></script>
<script src="routing-utils.js"></script>

<!-- At the end of <body>, before closing tag -->
<script>
    document.addEventListener('DOMContentLoaded', async () => {
        // Initialize router
        window.router = new Router();
        await window.router.init();
        
        // Enforce access to this page
        // (Optional - only if you want strict access control)
        // await window.router.enforceRouteAccess('currentPageName');
    });
</script>
```

### Step 2: Update Navigation on Each Page

**Find navigation sections in each HTML file** and apply this pattern:

```html
<!-- Old: Static navbar -->
<nav class="navbar">
    <a href="index.html">App</a>
    <a href="dashboard.html">Dashboard</a>
    <a href="admin.html">Admin</a>
</nav>

<!-- New: Dynamic navbar -->
<nav class="navbar" id="main-nav"></nav>

<script>
    async function updateNavigation() {
        const role = window.router.getRole();
        const navigation = window.routingUtils.buildNavigation(role);
        document.getElementById('main-nav').innerHTML = navigation;
    }
    
    document.addEventListener('DOMContentLoaded', updateNavigation);
    window.addEventListener('login', updateNavigation);
    window.addEventListener('logout', updateNavigation);
</script>
```

### Step 3: Add Access Control to Protected Pages

**For pages requiring authentication** (dashboard.html, admin.html, etc.):

```html
<script>
    // Immediate check on page load
    document.addEventListener('DOMContentLoaded', async () => {
        const target = 'admin'; // or 'user', 'dashboard', etc.
        
        if (!window.router.canAccessRoute(target)) {
            // Redirect to login/home
            window.location.href = window.router.getDefaultRoute();
        }
    });
</script>
```

---

## Phase 4: Testing (✅ Easy)

### Test Checklist

#### Guest Access
- [ ] Can access landing page without login
- [ ] Cannot access protected routes (auto redirect)
- [ ] See guest navigation menu
- [ ] Request limit message appears (5 requests/day)
- [ ] "Sign Up" button visible

#### User Access
- [ ] Login works (credentials validated)
- [ ] JWT token stored in localStorage
- [ ] User navigation menu appears
- [ ] Can access all user routes
- [ ] Cannot access admin routes (403 error)
- [ ] Logout clears session

#### Admin Access
- [ ] Admin login accepted
- [ ] Admin menu visible in navigation
- [ ] Can access admin routes
- [ ] User management features visible
- [ ] System status page accessible
- [ ] All user features still accessible

### Test Commands

**Terminal 1: Backend**
```powershell
cd backend
python main.py
# Should start on http://localhost:8000
```

**Browser Tests**:
```
# Test guest access
http://localhost:8000/landing.html       # ✅ Works
http://localhost:8000/app                # ❌ Redirects to login

# Test user access (logged in)
http://localhost:8000/app                # ✅ Works
http://localhost:8000/admin              # ❌ Access Denied

# Test admin access
http://localhost:8000/admin              # ✅ Works
http://localhost:8000/user-manage        # ✅ Works
```

---

## Phase 5: Deployment

### Pre-Deployment Checklist

- [ ] All routes tested locally
- [ ] No console errors
- [ ] Admin features inaccessible to users
- [ ] Guest limit enforced
- [ ] Logout clears cache
- [ ] JWT tokens valid

### Docker Deployment

**No changes needed!** Your existing Dockerfile works fine.

```bash
# Build
docker-compose build

# Run
docker-compose up
```

### Environment Variables

No new environment variables required. But verify these exist in `.env`:

```env
# Backend
FASTAPI_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=your-db-url
GROQ_API_KEY=your-groq-key

# Frontend
REACT_APP_API_URL=http://localhost:8000  (or your prod URL)
```

---

## Common Issues & Solutions

### Issue 1: Router not defined

**Problem**: `window.router is not defined`

**Solution**:
```html
<!-- Make sure router.js is linked -->
<script src="router.js"></script>
<script src="routing-utils.js"></script>

<!-- And initialized -->
<script>
    document.addEventListener('DOMContentLoaded', async () => {
        window.router = new Router();
        await window.router.init();
    });
</script>
```

### Issue 2: Authentication failing

**Problem**: Can't login, JWT not working

**Solution**:
1. Check `dependencies.py` is properly imported
2. Verify SECRET_KEY in `.env`
3. Check JWT token in browser console:
   ```javascript
   console.log(localStorage.getItem('token'));
   ```

### Issue 3: Routes not found

**Problem**: `Route not found in configuration`

**Solution**:
1. Verify route is defined in `routes_config.py`
2. Check spelling matches exactly
3. Update ROUTES in `router.js` if you added custom routes

### Issue 4: Admin routes showing for users

**Problem**: Users can see admin menu

**Solution**:
```javascript
// Wrong:
showIfRole(button, 'admin');  // No conditions!

// Right:
if (window.router.isAdmin()) {
    button.style.display = 'block';
}
```

---

## Rollback Procedure

If you need to revert to the old system:

```bash
# Restore old dependencies.py
git checkout HEAD -- backend/dependencies.py

# Remove new files
rm backend/routes_config.py
rm frontend/router.js
rm frontend/routing-utils.js

# Revert main.py changes
git checkout HEAD -- backend/main.py

# Restart services
docker-compose restart
```

---

## Next Steps

### Immediate (This Week)
1. Follow Phases 1-4 above
2. Test routing system
3. Fix any issues from test checklist
4. Deploy to staging

### Short Term (Next Week)
1. Monitor error logs
2. Gather user feedback
3. Fine-tune permission matrix
4. Optimize navigation

### Long Term (Next Month)
1. Implement SPA (dynamic page loading)
2. Add breadcrumb navigation
3. Implement route animations
4. Add advanced audit logging

---

## Useful Code Snippets

### Get Current User Info
```javascript
// In any JavaScript file
const role = window.router.getRole();
const isAdmin = window.router.isAdmin();
const isAuth = window.router.isAuthenticated();
```

### Navigate Programmatically
```javascript
// Navigate to another route
window.router.navigate('dashboard');

// With optional data
window.router.navigate('profile', { userId: 123 });

// Go back
history.back();
```

### Check Permissions
```javascript
// Can user do X?
if (window.routingUtils.hasPermission('can_review')) {
    // Enable review feature
}

// Can user access route?
if (window.routingUtils.canAccessRoute('admin')) {
    // Show admin button
}
```

### Build Dynamic Menus
```javascript
const role = window.router.getRole();
const menu = window.routingUtils.buildNavigation(role);
document.getElementById('nav').innerHTML = menu;
```

---

## Support & Questions

If you encounter issues not covered here:

1. Check `ROUTING.md` for detailed documentation
2. Review `router.js` comments for code-level docs
3. Check browser console for error messages
4. Verify all files are in correct locations

---

**Integration Guide Version**: 1.0.0  
**Last Updated**: February 19, 2026  
**Status**: ✅ Ready for Implementation
