const Navbar = (function() {
    const navbarEl = document.getElementById('navbar');

    const navLinks = [
        { path: '/index.html', label: '首页' },
        { path: '/about/', label: '关于' },
        { path: '/projects/', label: '项目表' },
        { path: '/blog/', label: '博客' },
        { path: '/docs/', label: '文档' }
    ];

    function getTheme() {
        const saved = localStorage.getItem('keybonk-theme');
        if (saved === 'light' || saved === 'dark') {
            return saved;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const searchIcon = document.querySelector('.search-icon');
        const toggleIcon = document.querySelector('.theme-toggle-icon');
        const menuIcon = document.querySelector('.menu-icon');
        if (searchIcon) {
            searchIcon.src = '/imgs/UI/' + (theme === 'dark' ? 'search_dark.png' : 'search.png');
        }
        if (toggleIcon) {
            toggleIcon.src = '/imgs/UI/' + (theme === 'dark' ? 'light_mood.png' : 'dark_mood.png');
        }
        if (menuIcon) {
            menuIcon.src = '/imgs/UI/' + (theme === 'dark' ? 'menu_dark.png' : 'menu.png');
        }
		const lightStyle = document.getElementById('hljs-light');
		const darkStyle = document.getElementById('hljs-dark');
		if (lightStyle && darkStyle) {
			if (theme === 'dark') {
				lightStyle.disabled = true;
				darkStyle.disabled = false;
			} else {
				lightStyle.disabled = false;
				darkStyle.disabled = true;
			}
		}
    }

    function normalizePath(path) {
        let p = path.replace(/\\/g, '/');
        if (p === '/' || p === '') {
            return '/index.html';
        }
        if (!p.startsWith('/')) {
            p = '/' + p;
        }
        if (p.endsWith('/')) {
            p = p.slice(0, -1);
        }
        return p;
    }

    function getCurrentPage() {
        return normalizePath(window.location.pathname);
    }

    function renderMobileMenu(currentPage) {
        const theme = getTheme();
        const searchIconSrc = theme === 'dark' ? 'search_dark.png' : 'search.png';
        const linksHtml = navLinks.map(link => {
            const normalizedLink = normalizePath(link.path);
            const isActive = currentPage === normalizedLink || 
                           (normalizedLink !== '/index.html' && currentPage.startsWith(normalizedLink + '/'));
            return `
                <li>
                    <a href="${link.path}" class="${isActive ? 'active' : ''}" onclick="Navbar.closeMobileMenu()">
                        ${link.label}
                    </a>
                </li>
            `;
        }).join('');

        return `
            <div class="mobile-menu-overlay" id="mobileMenuOverlay"></div>
            <ul class="mobile-menu" id="mobileMenu">
                <li class="mobile-search">
                    <div class="search-box">
                        <input type="text" placeholder="搜索..." />
                        <img src="/imgs/UI/${searchIconSrc}" class="search-icon" alt="搜索" />
                    </div>
                </li>
                ${linksHtml}
            </ul>
        `;
    }

    function render(currentPage) {
        const theme = getTheme();
        const searchIconSrc = theme === 'dark' ? 'search_dark.png' : 'search.png';
        const toggleIconSrc = theme === 'dark' ? 'light_mood.png' : 'dark_mood.png';
        const menuIconSrc = theme === 'dark' ? 'menu_dark.png' : 'menu.png';
        const linksHtml = navLinks.map(link => {
            const normalizedLink = normalizePath(link.path);
            const isActive = currentPage === normalizedLink || 
                           (normalizedLink !== '/index.html' && currentPage.startsWith(normalizedLink + '/'));
            return `
                <li>
                    <a href="${link.path}" class="${isActive ? 'active' : ''}">
                        ${link.label}
                    </a>
                </li>
            `;
        }).join('');

        navbarEl.innerHTML = `
            <div class="navbar-container">
                <div class="navbar-brand">
                    <a href="/index.html">
                        <img src="/imgs/icon.png" alt="KeyBonk Logo" class="navbar-logo">
                        KeyBonk
                    </a>
                </div>
                <ul class="navbar-links">
                    ${linksHtml}
                </ul>
                <div class="navbar-right">
                    <div class="search-box">
                        <input type="text" placeholder="搜索..." />
                        <img src="/imgs/UI/${searchIconSrc}" class="search-icon" alt="搜索" />
                    </div>
                    <a href="https://github.com/keyBonk-org" target="_blank" class="github-link" title="GitHub">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                    </a>
                    <button class="theme-toggle" id="themeToggle" title="切换主题">
                        <img src="/imgs/UI/${toggleIconSrc}" class="theme-toggle-icon" alt="切换主题" />
                    </button>
                    <button class="menu-toggle" id="menuToggle" title="菜单">
                        <img src="/imgs/UI/${menuIconSrc}" class="menu-icon" alt="菜单" />
                    </button>
                </div>
            </div>
        `;

        applyTheme(theme);

        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                const current = document.documentElement.getAttribute('data-theme') || 'light';
                const next = current === 'dark' ? 'light' : 'dark';
                localStorage.setItem('keybonk-theme', next);
                applyTheme(next);
            });
        }

        const menuBtn = document.getElementById('menuToggle');
        if (menuBtn) {
            menuBtn.addEventListener('click', openMobileMenu);
        }
    }

    function openMobileMenu() {
        let overlay = document.getElementById('mobileMenuOverlay');
        let menu = document.getElementById('mobileMenu');

        if (!overlay) {
            const menuHtml = renderMobileMenu(getCurrentPage());
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = menuHtml;
            
            while (tempDiv.firstElementChild) {
                document.body.appendChild(tempDiv.firstElementChild);
            }

            overlay = document.getElementById('mobileMenuOverlay');
            menu = document.getElementById('mobileMenu');

            overlay.addEventListener('click', closeMobileMenu);
        }

        menu.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMobileMenu() {
        const overlay = document.getElementById('mobileMenuOverlay');
        const menu = document.getElementById('mobileMenu');

        if (menu) {
            menu.remove();
        }
        if (overlay) {
            overlay.remove();
        }
        document.body.style.overflow = '';
    }

    function toggle(show) {
        if (show) {
            navbarEl.style.display = 'block';
        } else {
            navbarEl.style.display = 'none';
        }
    }

    function init(options = {}) {
        const currentPage = options.page || getCurrentPage();
        const showNav = options.showNav !== false;

        const theme = getTheme();
        document.documentElement.setAttribute('data-theme', theme);

        if (showNav) {
            render(currentPage);
        }
        toggle(showNav);
        
        if (typeof Search !== 'undefined') {
            Search.init();
        }
    }

    return {
        init,
        toggle,
        render,
        closeMobileMenu
    };
})();
