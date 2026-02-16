(function() {
    // --- 1. GLOBAL AUTH & ROUTING STATE ---
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    const username = localStorage.getItem('username') || sessionStorage.getItem('username');
    const role = localStorage.getItem('role') || sessionStorage.getItem('role');
    const path = window.location.pathname;
    
    const isGuest = !token || username === 'Guest';
    const isAdmin = role === 'admin';

    // Route Definitions
    const authPages = ['/login', '/signup'];
    const adminPages = ['/admin', '/batch', '/reports'];
    const protectedPages = ['/profile', '/settings', '/collab', '/generate'];

    // --- 2. STRICT ROUTE GUARDING ---
    // Prevent flickering by handling redirects immediately
    if (!window.skipAuthRedirect) {
        // A. Guest Access Control
        if (isGuest) {
            // Guests cannot access Admin or Protected User pages
            if (adminPages.some(p => path.includes(p)) || protectedPages.some(p => path.includes(p))) {
                // Allow /app for Guest demo if needed, otherwise redirect
                if (!path.includes('/app')) {
                    window.location.replace('/login');
                }
            }
        }
        // B. User Access Control
        else {
            // Regular Users cannot access Admin pages
            if (!isAdmin && adminPages.some(p => path.includes(p))) {
                window.location.replace('/app'); // Redirect to Dashboard
            }
            
            // Logged-in Users shouldn't see Login/Signup pages (Allow Landing Page)
            if (authPages.some(p => path === p || path.endsWith(p))) {
                window.location.replace(isAdmin ? '/admin' : '/app');
            }
        }
    }

    // Global Logout Function
    window.logout = function() {
        localStorage.clear();
        sessionStorage.clear();
        window.location.replace('/login');
    }

    const themeToggle = document.getElementById('theme-toggle');
    
    const getPreferredTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) return savedTheme;
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    };

    const setTheme = (theme) => {
        const isLight = theme === 'light';
        if (isLight) {
            document.body.classList.add('light-mode');
        } else {
            document.body.classList.remove('light-mode');
        }
        
        if (themeToggle) {
            themeToggle.innerHTML = isLight 
                ? '<i class="fas fa-sun text-yellow-500"></i>' 
                : '<i class="fas fa-moon text-yellow-400"></i>';
        }
        
        localStorage.setItem('theme', theme);
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    };
    
    window.applyTheme = setTheme;

    setTheme(getPreferredTheme());

    if (themeToggle) {
        themeToggle.onclick = () => {
            const isLight = document.body.classList.contains('light-mode');
            const newTheme = isLight ? 'dark' : 'light';
            setTheme(newTheme);
        };
    }

    // --- 3. DYNAMIC UI & NAVBAR SYNC ---
    const updateUI = () => {
        // Navbar Elements
        const guestNav = document.getElementById('guest-nav');
        const userNav = document.getElementById('user-nav');
        const adminNav = document.getElementById('admin-nav'); // Potential admin specific nav
        
        // Reset Visibility
        if (guestNav) guestNav.classList.add('hidden');
        if (userNav) userNav.classList.add('hidden');
        if (adminNav) adminNav.classList.add('hidden');

        // Apply Role-Based State
        if (isGuest) {
            if (guestNav) guestNav.classList.remove('hidden');
        } else {
            // Show User Nav for both User and Admin (Admin gets extras)
            if (userNav) {
                userNav.classList.remove('hidden');
                
                // Update User Info
                const nameDisplay = document.getElementById('nav-username');
                if (nameDisplay) nameDisplay.textContent = username || 'User';
                
                const avatar = document.getElementById('nav-avatar');
                if (avatar) avatar.src = `https://ui-avatars.com/api/?name=${username}&background=random&color=fff&background=0ea5e9`;
            }

            // Admin Specific UI Overrides
            if (isAdmin) {
                document.body.classList.add('admin-mode');
                
                // Inject Admin Links if they don't exist
                const navList = document.querySelector('#user-nav ul');
                if (navList && !document.getElementById('admin-link-inject')) {
                    const li = document.createElement('li');
                    li.id = 'admin-link-inject';
                    li.innerHTML = `<a href="/admin" class="text-red-400 hover:text-red-300 font-bold flex items-center gap-2"><i class="fas fa-shield-alt"></i> Admin Panel</a>`;
                    navList.prepend(li);
                }
            }
        }

        // --- 4. DYNAMIC PROFILE PAGE CONTENT ---
        if (path.includes('/profile')) {
            const profileContainer = document.getElementById('profile-content');
            if (profileContainer) {
                if (isAdmin) {
                    profileContainer.innerHTML = `
                        <div class="bg-slate-800 p-6 rounded-xl border border-red-900/50 shadow-lg">
                            <div class="flex items-center gap-4 mb-6 border-b border-slate-700 pb-4">
                                <div class="w-16 h-16 bg-red-900/30 rounded-full flex items-center justify-center text-red-400 text-2xl"><i class="fas fa-user-shield"></i></div>
                                <div><h2 class="text-2xl font-bold text-white">Administrator</h2><p class="text-red-400 text-sm">System Access Granted</p></div>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <button onclick="window.location.href='/admin'" class="p-4 bg-slate-700 hover:bg-slate-600 rounded-lg text-left transition-all"><i class="fas fa-tachometer-alt text-red-400 mr-2"></i> Open Dashboard</button>
                                <button onclick="window.location.href='/users'" class="p-4 bg-slate-700 hover:bg-slate-600 rounded-lg text-left transition-all"><i class="fas fa-users-cog text-red-400 mr-2"></i> User Management</button>
                            </div>
                        </div>`;
                } else {
                    profileContainer.innerHTML = `
                        <div class="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
                            <h2 class="text-2xl font-bold text-white mb-4">User Profile</h2>
                            <p class="text-slate-400">Welcome, ${username}. Manage your settings and history here.</p>
                        </div>`;
                }
            }
        }
    };

    // Inject Sign Up button on Login page
    if (path.includes('/login')) {
        const addSignUpBtn = () => {
            const form = document.querySelector('form');
            if (form && !document.getElementById('signup-link-container')) {
                const container = document.createElement('div');
                container.id = 'signup-link-container';
                container.className = 'mt-6 text-center border-t border-slate-700/50 pt-4';
                container.innerHTML = `
                    <p class="text-slate-400 text-sm mb-3">New to Code Refine?</p>
                    <a href="/signup" class="block w-full py-2.5 px-4 bg-slate-700/50 hover:bg-slate-700 text-white rounded-lg transition-all font-medium border border-slate-600 hover:border-slate-500">
                        <i class="fas fa-user-plus mr-2"></i>Create Account
                    </a>
                `;
                form.appendChild(container);
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addSignUpBtn);
        } else {
            addSignUpBtn();
        }
    }
})();