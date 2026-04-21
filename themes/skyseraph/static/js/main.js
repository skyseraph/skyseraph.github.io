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
