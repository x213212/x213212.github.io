(() => {
  const documentRoot = document.documentElement;
  documentRoot.classList.add('js');

  const storage = {
    get(key) {
      try { return localStorage.getItem(key); } catch (_error) { return null; }
    },
    set(key, value) {
      try { localStorage.setItem(key, value); } catch (_error) { /* Browser privacy mode. */ }
    }
  };

  const applyTheme = (theme) => {
    const next = theme === 'light' ? 'light' : 'dark';
    documentRoot.dataset.theme = next;
    storage.set('coding-orz-theme', next);
    const label = document.querySelector('[data-theme-label]');
    const toggle = document.querySelector('[data-theme-toggle]');
    const icon = document.querySelector('[data-theme-icon]');
    const action = next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    if (label) label.textContent = next === 'dark' ? 'Light' : 'Dark';
    if (icon) icon.textContent = next === 'dark' ? '☼' : '☾';
    if (toggle) {
      toggle.setAttribute('aria-label', action);
      toggle.setAttribute('title', action);
    }
  };

  applyTheme(documentRoot.dataset.theme || storage.get('coding-orz-theme') || 'dark');
  document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
    applyTheme(documentRoot.dataset.theme === 'dark' ? 'light' : 'dark');
  });

  const compactSidebar = window.matchMedia('(max-width: 1050px)');
  const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
  const sidebar = document.querySelector('#site-sidebar');
  const sidebarScrim = document.querySelector('[data-sidebar-scrim]');
  const sidebarPanels = [...document.querySelectorAll('[data-panel]')];
  const setSidebar = (open) => {
    const visible = compactSidebar.matches ? open : true;
    document.body.classList.toggle('sidebar-open', visible);
    sidebarToggle?.setAttribute('aria-expanded', visible ? 'true' : 'false');
    const label = visible ? 'Close sidebar' : 'Open sidebar';
    sidebarToggle?.setAttribute('aria-label', label);
    sidebarToggle?.setAttribute('title', label);
    if (sidebar) {
      const hidden = compactSidebar.matches && !visible;
      sidebar.setAttribute('aria-hidden', hidden ? 'true' : 'false');
      sidebar.inert = hidden;
    }
    sidebarScrim?.setAttribute('aria-hidden', visible && compactSidebar.matches ? 'false' : 'true');
  };
  const updateSidebarMode = () => {
    sidebarPanels.forEach((panel) => { panel.open = true; });
    setSidebar(compactSidebar.matches ? storage.get('coding-orz-sidebar') === 'open' : true);
  };
  updateSidebarMode();
  compactSidebar.addEventListener?.('change', updateSidebarMode);
  sidebarToggle?.addEventListener('click', () => {
    const next = !document.body.classList.contains('sidebar-open');
    setSidebar(next);
    if (compactSidebar.matches) storage.set('coding-orz-sidebar', next ? 'open' : 'closed');
  });
  sidebarScrim?.addEventListener('click', () => {
    if (!compactSidebar.matches) return;
    setSidebar(false);
    storage.set('coding-orz-sidebar', 'closed');
    sidebarToggle?.focus();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !compactSidebar.matches || !document.body.classList.contains('sidebar-open')) return;
    setSidebar(false);
    storage.set('coding-orz-sidebar', 'closed');
    sidebarToggle?.focus();
  });

  const archiveToggle = document.querySelector('[data-archive-toggle]');
  const archiveNodes = [...document.querySelectorAll('#archive-tree details')];
  const syncArchiveToggle = () => {
    if (!archiveToggle || !archiveNodes.length) return;
    const allOpen = archiveNodes.every((node) => node.open);
    archiveToggle.textContent = allOpen ? 'Collapse all' : 'Expand all';
    archiveToggle.setAttribute('aria-label', archiveToggle.textContent + ' archive years and months');
  };
  archiveToggle?.addEventListener('click', () => {
    const shouldOpen = !archiveNodes.every((node) => node.open);
    archiveNodes.forEach((node) => { node.open = shouldOpen; });
    syncArchiveToggle();
  });
  archiveNodes.forEach((node) => node.addEventListener('toggle', syncArchiveToggle));
  syncArchiveToggle();

  const hero = document.querySelector('[data-ambient]');
  if (hero && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    hero.addEventListener('pointermove', (event) => {
      const box = hero.getBoundingClientRect();
      const x = ((event.clientX - box.left) / box.width - .5) * 18;
      const y = ((event.clientY - box.top) / box.height - .5) * 14;
      hero.style.setProperty('--ambient-x', x.toFixed(1) + 'px');
      hero.style.setProperty('--ambient-y', y.toFixed(1) + 'px');
    });
    hero.addEventListener('pointerleave', () => {
      hero.style.setProperty('--ambient-x', '0px');
      hero.style.setProperty('--ambient-y', '0px');
    });
  }

  const searchRoot = document.querySelector('[data-search]');
  if (!searchRoot) return;

  const input = searchRoot.querySelector('input');
  const status = searchRoot.querySelector('.search-status');
  const results = searchRoot.querySelector('.search-results');
  let entries = [];
  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[character]));

  const show = () => {
    const query = input.value.trim().toLocaleLowerCase();
    if (!query) {
      status.textContent = 'Enter a term to search all 379 posts.';
      results.innerHTML = '';
      return;
    }
    const terms = query.split(/\s+/).filter(Boolean);
    const matched = entries.filter((entry) => {
      const haystack = (entry.title + ' ' + entry.tags.join(' ') + ' ' + entry.text).toLocaleLowerCase();
      return terms.every((term) => haystack.includes(term));
    }).slice(0, 50);
    const count = matched.length + (matched.length === 50 ? '+' : '');
    status.textContent = count + ' result' + (matched.length === 1 ? '' : 's') + ' found.';
    results.innerHTML = matched.map((entry) => (
      '<article class="search-result">' +
        '<div class="search-result__meta">' + escapeHtml(entry.date) + ' · ' +
          entry.tags.map((tag) => '#' + escapeHtml(tag)).join(' ') +
        '</div>' +
        '<h2><a href="../' + escapeHtml(entry.route) + '">' + escapeHtml(entry.title) + '</a></h2>' +
        '<p>' + escapeHtml(entry.text) + '</p>' +
      '</article>'
    )).join('');
  };

  fetch('../assets/search-index.json')
    .then((response) => response.ok ? response.json() : Promise.reject(new Error(response.statusText)))
    .then((data) => {
      entries = data;
      status.textContent = 'Enter a term to search all 379 posts.';
      input.disabled = false;
      const preset = new URLSearchParams(window.location.search).get('q');
      if (preset) {
        input.value = preset;
        show();
      }
    })
    .catch(() => { status.textContent = 'Search index could not be loaded. Please refresh the page.'; });

  input.disabled = true;
  input.addEventListener('input', show);
})();

/* One-click copy for code blocks. The button is rendered at build time, so this
   only wires up the behaviour and reports the result back on the button. */
(() => {
  const buttons = document.querySelectorAll('[data-copy]');
  if (!buttons.length) return;

  const write = async (text) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.cssText = 'position:fixed;top:-1000px;opacity:0';
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    area.remove();
  };

  buttons.forEach((button) => {
    button.addEventListener('click', async () => {
      const code = button.closest('.code-block')?.querySelector('pre');
      if (!code) return;
      const label = button.textContent;
      try {
        await write(code.innerText.replace(/\n$/, ''));
        button.textContent = 'Copied';
        button.setAttribute('data-copied', '');
      } catch (_error) {
        button.textContent = 'Press Ctrl+C';
      }
      window.setTimeout(() => {
        button.textContent = label;
        button.removeAttribute('data-copied');
      }, 1600);
    });
  });
})();

/* Home-page filtering. GitHub Pages serves static files only, so the filter runs
   in the browser against the same index the search page uses. The server-rendered
   list stays untouched until the reader actually filters, which keeps the page
   working without JavaScript and keeps the index off the critical path. */
(() => {
  const form = document.querySelector('[data-post-filter]');
  const list = document.querySelector('[data-post-list]');
  if (!form || !list) return;

  const query = form.querySelector('[data-filter-query]');
  const topic = form.querySelector('[data-filter-topic]');
  const year = form.querySelector('[data-filter-year]');
  const reset = form.querySelector('[data-filter-reset]');
  const status = form.querySelector('[data-filter-status]');
  const pager = document.querySelector('[data-pagination]');
  const original = list.innerHTML;
  const MAX = 60;

  let entries = null;
  let loading = null;

  form.hidden = false;
  form.addEventListener('submit', (event) => event.preventDefault());

  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[character]));

  const card = (entry) => {
    const summary = entry.text.length > 190 ? entry.text.slice(0, 190).trimEnd() + '…' : entry.text;
    const categories = entry.categories.length
      ? '<div class="post-categories">' +
          entry.categories.map((name) => '<span class="category">' + escapeHtml(name) + '</span>').join('') +
        '</div>'
      : '';
    const thumbnail = entry.thumb
      ? '<a class="post-card__thumbnail" href="' + escapeHtml(entry.route) + '" tabindex="-1" aria-hidden="true">' +
          '<img src="' + escapeHtml(entry.thumb) + '" alt="" loading="lazy" decoding="async">' +
        '</a>'
      : '';
    return '<article class="post-card">' +
      '<div class="post-card__body">' +
        '<div class="post-card__meta"><time datetime="' + escapeHtml(entry.iso) + '">' + escapeHtml(entry.date) + '</time></div>' +
        '<h2><a href="' + escapeHtml(entry.route) + '">' + escapeHtml(entry.title) + '</a></h2>' +
        '<p>' + escapeHtml(summary) + '</p>' +
        categories +
      '</div>' + thumbnail +
    '</article>';
  };

  const restore = () => {
    list.innerHTML = original;
    if (pager) pager.hidden = false;
    if (reset) reset.hidden = true;
    status.textContent = '';
    document.dispatchEvent(new CustomEvent('postlist:changed'));
  };

  const apply = () => {
    const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const wantedTopic = topic.value;
    const wantedYear = year.value;
    if (!terms.length && !wantedTopic && !wantedYear) {
      restore();
      return;
    }
    const matched = entries.filter((entry) => {
      if (wantedTopic && !entry.categories.includes(wantedTopic)) return false;
      if (wantedYear && entry.iso.slice(0, 4) !== wantedYear) return false;
      if (!terms.length) return true;
      const haystack = (entry.title + ' ' + entry.tags.join(' ') + ' ' + entry.categories.join(' ') + ' ' + entry.text).toLocaleLowerCase();
      return terms.every((term) => haystack.includes(term));
    });
    if (pager) pager.hidden = true;
    if (reset) reset.hidden = false;
    const shown = matched.slice(0, MAX);
    list.innerHTML = shown.length
      ? shown.map(card).join('')
      : '<p class="post-filter__empty">No post matches this filter.</p>';
    status.textContent = matched.length
      ? matched.length + ' post' + (matched.length === 1 ? '' : 's') +
        (matched.length > MAX ? ' · showing first ' + MAX : '')
      : 'No match.';
    document.dispatchEvent(new CustomEvent('postlist:changed'));
  };

  const load = () => {
    if (entries) return Promise.resolve();
    if (!loading) {
      status.textContent = 'Loading index…';
      loading = fetch('assets/search-index.json')
        .then((response) => (response.ok ? response.json() : Promise.reject(new Error(response.statusText))))
        .then((data) => { entries = data; })
        .catch(() => {
          status.textContent = 'Filter index could not be loaded.';
          return Promise.reject(new Error('index'));
        });
    }
    return loading;
  };

  const run = () => { load().then(apply, () => {}); };

  let timer = 0;
  query.addEventListener('input', () => {
    window.clearTimeout(timer);
    timer = window.setTimeout(run, 140);
  });
  topic.addEventListener('change', run);
  year.addEventListener('change', run);
  reset?.addEventListener('click', () => {
    query.value = '';
    topic.value = '';
    year.value = '';
    restore();
  });
})();

/* Visitor count. GoatCounter's counter endpoint is public, so the number can be
   fetched from the static page; GA4 cannot do this because its Data API needs a
   credential. The element stays hidden until a number actually arrives, so a
   blocked request or a disabled endpoint leaves no empty furniture behind. */
(() => {
  const box = document.querySelector('[data-visitor-count]');
  if (!box) return;
  const code = box.getAttribute('data-visitor-count');
  const total = box.querySelector('[data-visitor-total]');
  if (!code || !total) return;

  const format = (value) => Number(String(value).replace(/[^0-9]/g, '')).toLocaleString();

  fetch(`https://${code}.goatcounter.com/counter/TOTAL.json`)
    .then((response) => (response.ok ? response.json() : Promise.reject(new Error(String(response.status)))))
    .then((data) => {
      if (!data || data.count === undefined) return;
      const views = format(data.count);
      const people = data.count_unique !== undefined ? format(data.count_unique) : '';
      total.textContent = people ? `${views} views · ${people} visitors · ` : `${views} views · `;
      total.hidden = false;
    })
    .catch(() => { /* Counting is optional; never let it disturb the page. */ });
})();

/* Keep giscus in step with the site's own light/dark toggle. The comment box is
   a cross-origin iframe, so its theme can only be changed by postMessage - left
   alone it would stay on whatever it loaded with while the page around it flips. */
(() => {
  const frameSelector = 'iframe.giscus-frame';
  const themeFor = () => (document.documentElement.dataset.theme === 'light' ? 'light' : 'dark');

  const send = () => {
    const frame = document.querySelector(frameSelector);
    if (!frame?.contentWindow) return;
    frame.contentWindow.postMessage(
      { giscus: { setConfig: { theme: themeFor() } } },
      'https://giscus.app'
    );
  };

  if (!document.querySelector('script[src^="https://giscus.app"]')) return;

  // The iframe is injected asynchronously, so set the theme once it appears.
  const observer = new MutationObserver(() => {
    if (document.querySelector(frameSelector)) {
      send();
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

  new MutationObserver(send).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });
})();
