/**
 * Design System & Theme Configuration
 * Establishes global style tokens, typography, and component consistency.
 */
const DesignSystem = {
    tokens: {
        colors: {
            primary: '#4F46E5', // Deep Indigo
            primaryHover: '#4338CA',
            surfaceGuest: '#FFFFFF',
            surfaceUser: '#F9FAFB', // Light Gray for Dashboard
            surfaceAdmin: '#F3F4F6',
            textMain: '#111827',
            textMuted: '#6B7280',
            border: '#E5E7EB'
        },
        typography: {
            fontFamily: '"Inter", "Roboto", "Helvetica Neue", sans-serif',
        },
        spacing: {
            radius: '0.5rem', // 8px
            inputPadding: '0.5rem 0.75rem'
        }
    },

    injectGlobalStyles() {
        const styleId = 'code-refine-design-system';
        if (document.getElementById(styleId)) return;

        const css = `
            :root {
                --color-primary: ${this.tokens.colors.primary};
                --color-primary-hover: ${this.tokens.colors.primaryHover};
                --font-main: ${this.tokens.typography.fontFamily};
            }

            body {
                font-family: var(--font-main);
                color: ${this.tokens.colors.textMain};
                transition: background-color 0.3s ease;
            }

            /* 3. Component Consistency */
            .btn-primary {
                background-color: var(--color-primary);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: ${this.tokens.spacing.radius};
                font-weight: 500;
                transition: all 0.2s;
                border: none;
                cursor: pointer;
            }
            .btn-primary:hover { background-color: var(--color-primary-hover); }

            .input-std {
                border: 1px solid ${this.tokens.colors.border};
                border-radius: ${this.tokens.spacing.radius};
                padding: ${this.tokens.spacing.inputPadding};
                width: 100%;
                transition: ring 0.2s;
            }
            .input-std:focus {
                outline: none;
                border-color: var(--color-primary);
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            }

            .card-std {
                background: white;
                border-radius: 12px; /* Slightly larger for cards */
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); /* shadow-sm */
                border: 1px solid ${this.tokens.colors.border};
            }
            
            /* Dark Mode Overrides */
            body.dark-mode .card-std {
                background: #1F2937;
                border-color: #374151;
                color: #F3F4F6;
            }
            body.dark-mode .input-std {
                background: #374151;
                border-color: #4B5563;
                color: white;
            }
        `;

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = css;
        document.head.appendChild(style);
    }
};

(function() {
    // Security: Redirect logged-in users away from public pages
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    const path = window.location.pathname;
    const publicPages = ['/login', '/signup', '/landing', '/'];
    
    if (!window.skipAuthRedirect && token && publicPages.some(p => path === p || (path !== '/' && path.endsWith(p)))) {
        window.location.replace('/app');
    }

    const themeToggle = document.getElementById('theme-toggle');
    
    // Initialize Design System
    DesignSystem.injectGlobalStyles();

    const getPreferredTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) return savedTheme;
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    };

    const setTheme = (theme) => {
        const isLight = theme === 'light';
        if (isLight) {
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
        } else {
            document.body.classList.remove('light-mode');
            document.body.classList.add('dark-mode');
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