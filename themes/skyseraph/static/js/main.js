// Mobile nav toggle
(function() {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function() {
      links.classList.toggle('open');
    });
  }

  // Active nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(function(link) {
    const href = link.getAttribute('href');
    if (href === '/' ? currentPath === '/' : currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });
})();

// Language toggle (ZH / EN)
(function() {
  const btn = document.getElementById('langToggle');
  if (!btn) return;

  const STORAGE_KEY = 'preferred-lang';
  let current = localStorage.getItem(STORAGE_KEY) || 'zh';

  function applyLang(lang) {
    document.querySelectorAll('.lang-zh').forEach(function(el) {
      el.style.display = lang === 'zh' ? '' : 'none';
    });
    document.querySelectorAll('.lang-en').forEach(function(el) {
      el.style.display = lang === 'en' ? '' : 'none';
    });
    btn.textContent = lang === 'zh' ? 'EN' : 'ZH';
    btn.setAttribute('aria-label', lang === 'zh' ? '切换为英文' : '切换为中文');
    localStorage.setItem(STORAGE_KEY, lang);
    current = lang;
  }

  btn.addEventListener('click', function() {
    applyLang(current === 'zh' ? 'en' : 'zh');
  });

  // Apply on page load
  applyLang(current);
})();

// TOC active heading highlight (IntersectionObserver)
(function() {
  const tocLinks = document.querySelectorAll('.toc-sidebar .toc a');
  if (!tocLinks.length) return;

  // Build map: anchor id → toc link element
  const linkMap = {};
  tocLinks.forEach(function(a) {
    const id = decodeURIComponent(a.getAttribute('href').replace(/^#/, ''));
    linkMap[id] = a;
  });

  const headings = document.querySelectorAll('.prose h2, .prose h3, .prose h4');
  if (!headings.length) return;

  let activeId = null;

  function setActive(id) {
    if (id === activeId) return;
    if (activeId && linkMap[activeId]) linkMap[activeId].classList.remove('toc-active');
    activeId = id;
    if (id && linkMap[id]) {
      linkMap[id].classList.add('toc-active');
      // Scroll TOC sidebar to keep active link visible
      const sidebar = document.querySelector('.toc-sidebar');
      const activeEl = linkMap[id];
      if (sidebar && activeEl) {
        const sTop = sidebar.scrollTop;
        const sH = sidebar.clientHeight;
        const eTop = activeEl.offsetTop;
        const eH = activeEl.clientHeight;
        if (eTop < sTop || eTop + eH > sTop + sH) {
          sidebar.scrollTop = eTop - sH / 2;
        }
      }
    }
  }

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        setActive(entry.target.id);
      }
    });
  }, {
    rootMargin: '-' + (56 + 24) + 'px 0px -60% 0px',
    threshold: 0
  });

  headings.forEach(function(h) { if (h.id) observer.observe(h); });
})();
