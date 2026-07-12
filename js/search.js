const Search = (function() {
    let searchIndex = [];
    let isLoading = false;
    let searchInput = null;
    let resultsContainer = null;
    let debounceTimer = null;

    async function loadIndex() {
        if (searchIndex.length > 0) return;
        if (isLoading) return;
        
        isLoading = true;
        try {
            const response = await fetch('/js/search_index.json');
            if (response.ok) {
                searchIndex = await response.json();
            }
        } catch (e) {
            console.error('Failed to load search index:', e);
        } finally {
            isLoading = false;
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegExp(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function highlightMatch(text, query) {
        if (!text || !query) return escapeHtml(text || '');
        
        const escapedQuery = escapeRegExp(query);
        const regex = new RegExp(`(${escapedQuery})`, 'gi');
        return text.replace(regex, '<span class="search-match">$1</span>');
    }

    function getExcerptForHeading(content, headingText, query, maxLength = 150) {
        if (!content || !query) return '';
        
        const headingIndex = content.indexOf(headingText);
        if (headingIndex >= 0) {
            const start = headingIndex + headingText.length;
            
            const nextHeadingMatch = content.substring(start).match(/^[\s\S]*?(?=\s*(?:^#{1,4}\s+|\n#{1,4}\s+))/);
            let textAfterHeading;
            if (nextHeadingMatch) {
                textAfterHeading = nextHeadingMatch[0].trim();
            } else {
                textAfterHeading = content.substring(start).trim();
            }
            
            if (textAfterHeading) {
                return getExcerpt(textAfterHeading, query, maxLength);
            }
        }
        
        return getExcerpt(content, query, maxLength);
    }

    function getExcerpt(text, query, maxLength = 150) {
        if (!text || !query) return '';
        
        const q = query.toLowerCase();
        const lowerText = text.toLowerCase();
        const index = lowerText.indexOf(q);
        
        if (index >= 0) {
            const start = Math.max(0, index - 50);
            const end = Math.min(text.length, index + query.length + 100);
            let excerpt = text.substring(start, end);
            
            if (start > 0) excerpt = '...' + excerpt;
            if (end < text.length) excerpt = excerpt + '...';
            
            return highlightMatch(excerpt, query);
        }
        
        const trimmed = text.substring(0, maxLength);
        return trimmed + (text.length > maxLength ? '...' : '');
    }

    function getFullPathLabel(type, fullPath) {
        const typeLabels = {
            'docs': '文档',
            'blog': '博客'
        };
        
        const parts = fullPath.split('/').filter(p => p);
        if (parts.length === 0) return typeLabels[type] || type;
        
        return typeLabels[type] + ' > ' + parts.join(' > ');
    }

    function search(query) {
        if (!query || query.trim().length < 1) return [];
        
        const q = query.toLowerCase().trim();
        const results = [];
        
        for (const item of searchIndex) {
            const titleMatch = item.title.toLowerCase().includes(q);
            const textMatch = item.plain_text.toLowerCase().includes(q);
            
            if (!titleMatch && !textMatch) continue;
            
            const headingResults = [];
            if (item.headings) {
                for (const heading of item.headings) {
                    if (heading.text.toLowerCase().includes(q)) {
                        const headingContent = item.heading_contents && item.heading_contents[heading.text] ? item.heading_contents[heading.text] : '';
                        headingResults.push({
                            title: heading.text,
                            url: item.url + '#' + heading.text.toLowerCase().replace(/\s+/g, '-'),
                            excerpt: headingContent ? getExcerpt(headingContent, q) : getExcerpt(item.plain_text, q),
                            path_label: getFullPathLabel(item.type, item.full_path),
                            score: 3 + (4 - heading.level)
                        });
                    }
                }
            }
            
            if (headingResults.length > 0) {
                results.push(...headingResults);
            } else {
                results.push({
                    title: item.title,
                    url: item.url,
                    excerpt: getExcerpt(item.plain_text, q),
                    path_label: getFullPathLabel(item.type, item.full_path),
                    score: titleMatch ? 2 : 1
                });
            }
        }
        
        return results.sort((a, b) => b.score - a.score).slice(0, 15);
    }

    function renderResults(results) {
        if (!resultsContainer) return;
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="search-no-results">未找到匹配结果</div>';
            resultsContainer.classList.add('active');
            return;
        }
        
        let html = '';
        let currentPath = '';
        const query = searchInput ? searchInput.value : '';
        
        for (let i = 0; i < results.length; i++) {
            const item = results[i];
            
            if (item.path_label !== currentPath) {
                html += `<div class="search-prefix">${item.path_label}</div>`;
                currentPath = item.path_label;
            }
            
            html += `
                <li>
                    <a href="${item.url}" class="${i === 0 ? 'search-active' : ''}" data-index="${i}">
                        <div class="search-title">${highlightMatch(item.title, query)}</div>
                        ${item.excerpt ? `<div class="search-excerpt">${item.excerpt}</div>` : ''}
                    </a>
                </li>
            `;
        }
        
        resultsContainer.innerHTML = html;
        resultsContainer.classList.add('active');
    }

    function hideResults() {
        if (resultsContainer) {
            resultsContainer.classList.remove('active');
        }
    }

    function getNextLi(currentLi) {
        let next = currentLi.nextElementSibling;
        while (next && next.tagName !== 'LI') {
            next = next.nextElementSibling;
        }
        return next;
    }

    function getPrevLi(currentLi) {
        let prev = currentLi.previousElementSibling;
        while (prev && prev.tagName !== 'LI') {
            prev = prev.previousElementSibling;
        }
        return prev;
    }

    async function handleSearch(e) {
        const query = e.target.value;
        
        if (debounceTimer) clearTimeout(debounceTimer);
        
        debounceTimer = setTimeout(async () => {
            await loadIndex();
            const results = search(query);
            renderResults(results);
        }, 200);
    }

    function init() {
        searchInput = document.querySelector('.search-box input');
        if (!searchInput) return;
        
        const searchBox = searchInput.parentElement;
        resultsContainer = document.createElement('ul');
        resultsContainer.className = 'search-results';
        resultsContainer.setAttribute('aria-label', '搜索结果');
        searchBox.appendChild(resultsContainer);
        
        searchInput.addEventListener('input', handleSearch);
        
        document.addEventListener('click', (e) => {
            if (!searchBox.contains(e.target)) {
                hideResults();
            }
        });
        
        searchInput.addEventListener('keydown', (e) => {
            if (!resultsContainer || !resultsContainer.classList.contains('active')) return;
            
            const activeLink = resultsContainer.querySelector('.search-active');
            const items = resultsContainer.querySelectorAll('li');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (activeLink) {
                    activeLink.classList.remove('search-active');
                    const currentLi = activeLink.parentElement;
                    const nextLi = getNextLi(currentLi);
                    if (nextLi) {
                        nextLi.querySelector('a').classList.add('search-active');
                    } else {
                        items[0].querySelector('a').classList.add('search-active');
                    }
                } else if (items.length > 0) {
                    items[0].querySelector('a').classList.add('search-active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (activeLink) {
                    activeLink.classList.remove('search-active');
                    const currentLi = activeLink.parentElement;
                    const prevLi = getPrevLi(currentLi);
                    if (prevLi) {
                        prevLi.querySelector('a').classList.add('search-active');
                    } else {
                        items[items.length - 1].querySelector('a').classList.add('search-active');
                    }
                } else if (items.length > 0) {
                    items[items.length - 1].querySelector('a').classList.add('search-active');
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                const active = resultsContainer.querySelector('.search-active');
                if (active) {
                    active.click();
                } else if (items.length > 0) {
                    items[0].querySelector('a').click();
                }
            } else if (e.key === 'Escape') {
                hideResults();
            }
        });
    }

    return {
        init,
        search
    };
})();
