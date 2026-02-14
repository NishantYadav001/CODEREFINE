(function() {
    // Security: Redirect logged-in users away from public pages
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    const path = window.location.pathname;
    const publicPages = ['/login', '/signup', '/landing', '/'];
    
    if (!window.skipAuthRedirect && token && publicPages.some(p => path === p || (path !== '/' && path.endsWith(p)))) {
        window.location.replace('/app');
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
})();