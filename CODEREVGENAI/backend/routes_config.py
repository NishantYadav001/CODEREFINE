# ════════════════════════════════════════════════════════════════════
# CODEREFINE - Role-Based Routing Configuration
# ════════════════════════════════════════════════════════════════════
"""
Routing Strategy:
- Guest: Limited access, no authentication required
- User: Authenticated, full access to features
- Admin: Super user, access to admin panel + all features
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTE DEFINITIONS BY USER TYPE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ┌─────────────────────────────────────────────────────────────┐
# │ GUEST ROUTES - No Authentication Required                   │
# └─────────────────────────────────────────────────────────────┘
GUEST_ROUTES = {
    'landing': {
        'path': '/landing.html',
        'title': 'Welcome to CodeRefine',
        'icon': 'home',
        'requires_auth': False,
        'rate_limited': True,
        'daily_limit': 5
    },
    'login': {
        'path': '/login.html',
        'title': 'Login',
        'icon': 'login',
        'requires_auth': False,
        'rate_limited': False
    },
    'signup': {
        'path': '/signup.html',
        'title': 'Sign Up',
        'icon': 'user-plus',
        'requires_auth': False,
        'rate_limited': False
    },
    'help': {
        'path': '/help.html',
        'title': 'Help & Documentation',
        'icon': 'question-circle',
        'requires_auth': False,
        'rate_limited': False
    }
}

# ┌─────────────────────────────────────────────────────────────┐
# │ USER ROUTES - Authentication Required                       │
# └─────────────────────────────────────────────────────────────┘
USER_ROUTES = {
    'app': {
        'path': '/index.html',
        'title': 'Code Review Tool',
        'icon': 'code',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['review', 'generate', 'run', 'refactor']
    },
    'dashboard': {
        'path': '/dashboard.html',
        'title': 'My Dashboard',
        'icon': 'chart-line',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['analytics', 'statistics', 'history']
    },
    'profile': {
        'path': '/profile.html',
        'title': 'My Profile',
        'icon': 'user-circle',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['edit_profile', 'change_password', 'api_keys']
    },
    'settings': {
        'path': '/settings.html',
        'title': 'Settings',
        'icon': 'cog',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['theme', 'notifications', 'preferences']
    },
    'generate': {
        'path': '/generate.html',
        'title': 'Code Generation',
        'icon': 'zap',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['generate', 'customize']
    },
    'batch': {
        'path': '/batch.html',
        'title': 'Batch Processing',
        'icon': 'upload',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['bulk_review', 'csv_import']
    },
    'collab': {
        'path': '/collab.html',
        'title': 'Collaboration',
        'icon': 'share-2',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['share', 'team', 'comments']
    },
    'reports': {
        'path': '/reports.html',
        'title': 'Reports',
        'icon': 'file-text',
        'requires_auth': True,
        'required_role': 'user',
        'features': ['generate_report', 'export', 'schedule']
    }
}

# ┌─────────────────────────────────────────────────────────────┐
# │ ADMIN ROUTES - Admin Only                                   │
# └─────────────────────────────────────────────────────────────┘
ADMIN_ROUTES = {
    'admin': {
        'path': '/admin.html',
        'title': 'Admin Panel',
        'icon': 'shield-admin',
        'requires_auth': True,
        'required_role': 'admin',
        'features': [
            'user_management',
            'system_settings',
            'analytics',
            'audit_logs',
            'api_keys',
            'maintenance'
        ]
    },
    'status': {
        'path': '/status.html',
        'title': 'System Status',
        'icon': 'activity',
        'requires_auth': True,
        'required_role': 'admin',
        'features': ['system_health', 'disk_usage', 'memory']
    }
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMBINED ROUTE MAPPINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# All routes
ALL_ROUTES = {**GUEST_ROUTES, **USER_ROUTES, **ADMIN_ROUTES}

# Route groups by authentication
PUBLIC_ROUTES = list(GUEST_ROUTES.keys())
PROTECTED_ROUTES = list(USER_ROUTES.keys()) + list(ADMIN_ROUTES.keys())
ADMIN_ONLY_ROUTES = list(ADMIN_ROUTES.keys())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PERMISSION MATRIX
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERMISSION_MATRIX = {
    'guest': {
        'routes': PUBLIC_ROUTES,
        'can_review': False,
        'can_generate': False,
        'can_save': False,
        'daily_requests': 5,
        'storage': 0
    },
    'user': {
        'routes': PUBLIC_ROUTES + list(USER_ROUTES.keys()),
        'can_review': True,
        'can_generate': True,
        'can_save': True,
        'daily_requests': 100,
        'storage': 100,  # MB
        'features': ['batch', 'collab', 'reports']
    },
    'admin': {
        'routes': list(ALL_ROUTES.keys()),
        'can_review': True,
        'can_generate': True,
        'can_save': True,
        'can_manage_users': True,
        'can_manage_system': True,
        'can_view_audit': True,
        'daily_requests': -1,  # Unlimited
        'storage': -1  # Unlimited
    }
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NAVIGATION STRUCTURE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NAVIGATION_MENUS = {
    'guest': [
        {'name': 'Home', 'route': 'landing', 'icon': 'home'},
        {'name': 'Login', 'route': 'login', 'icon': 'login'},
        {'name': 'Sign Up', 'route': 'signup', 'icon': 'user-plus'},
        {'name': 'Help', 'route': 'help', 'icon': 'question-circle'}
    ],
    'user': [
        {'name': 'App', 'route': 'app', 'icon': 'code'},
        {'name': 'Dashboard', 'route': 'dashboard', 'icon': 'chart-line'},
        {'name': 'Profile', 'route': 'profile', 'icon': 'user-circle'},
        {'name': 'Settings', 'route': 'settings', 'icon': 'cog'},
        {'name': 'Generate', 'route': 'generate', 'icon': 'zap'},
        {'name': 'Batch', 'route': 'batch', 'icon': 'upload'},
        {'name': 'Collaborate', 'route': 'collab', 'icon': 'share-2'},
        {'name': 'Reports', 'route': 'reports', 'icon': 'file-text'}
    ],
    'admin': [
        {'name': 'App', 'route': 'app', 'icon': 'code'},
        {'name': 'Dashboard', 'route': 'dashboard', 'icon': 'chart-line'},
        {'name': 'Admin Panel', 'route': 'admin', 'icon': 'shield-admin', 'divider_before': True},
        {'name': 'System Status', 'route': 'status', 'icon': 'activity'},
        {'name': 'Profile', 'route': 'profile', 'icon': 'user-circle', 'divider_before': True},
        {'name': 'Settings', 'route': 'settings', 'icon': 'cog'}
    ]
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API ENDPOINTS BY USER TYPE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API_ENDPOINTS = {
    'public': [
        'POST /api/auth/login',
        'POST /api/auth/signup',
        'GET /api/health'
    ],
    'user': [
        'POST /api/code/review',
        'POST /api/code/generate',
        'POST /api/code/refactor',
        'GET /api/user/profile',
        'PUT /api/user/profile',
        'GET /api/user/history'
    ],
    'admin': [
        'GET /api/admin/users',
        'POST /api/admin/users',
        'DELETE /api/admin/users/{id}',
        'GET /api/admin/dashboard',
        'GET /api/admin/audit-logs',
        'PUT /api/admin/settings'
    ]
}

# ════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def get_routes_for_role(role: str) -> dict:
    """Get all accessible routes for a given role"""
    return {k: v for k, v in ALL_ROUTES.items() if k in PERMISSION_MATRIX[role]['routes']}

def can_access_route(route: str, role: str) -> bool:
    """Check if a role can access a specific route"""
    if role not in PERMISSION_MATRIX:
        role = 'guest'
    return route in PERMISSION_MATRIX[role].get('routes', [])

def get_navigation_for_role(role: str) -> list:
    """Get navigation menu for a given role"""
    return NAVIGATION_MENUS.get(role, NAVIGATION_MENUS.get('guest', []))

def get_default_route(role: str) -> str:
    """Get default landing route for a role"""
    defaults = {
        'guest': '/landing.html',
        'user': '/index.html',
        'admin': '/admin.html'
    }
    return defaults.get(role, '/landing.html')

# ════════════════════════════════════════════════════════════════════
