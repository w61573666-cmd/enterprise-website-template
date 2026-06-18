/* ============================================
   HENGSHENG MARBLE S&T - Main JavaScript
   Navigation, Language Switch, Animations
   Version: 2026-04-23-7
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Navbar Scroll Effect ----------
  const navbar = document.querySelector('.navbar');
  const handleScroll = () => {
    if (window.scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // ---------- Mobile Menu Toggle ----------
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  // Create mobile overlay if not exists
  let overlay = document.querySelector('.nav-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'nav-overlay';
    document.body.appendChild(overlay);
  }

  function closeMobileMenu() {
    if (navToggle) navToggle.classList.remove('active');
    if (navLinks) navLinks.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    // Collapse all expanded dropdowns
    if (navLinks) {
      navLinks.querySelectorAll('.nav-dropdown.mobile-open').forEach(dd => {
        dd.classList.remove('mobile-open');
      });
    }
  }

  function openMobileMenu() {
    if (navToggle) navToggle.classList.add('active');
    if (navLinks) navLinks.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  if (navToggle) {
    navToggle.addEventListener('click', () => {
      if (navLinks.classList.contains('open')) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });
  }

  // Close on overlay click
  overlay.addEventListener('click', closeMobileMenu);

  // Mobile dropdown toggle (tap to expand/collapse)
  if (navLinks) {
    navLinks.querySelectorAll('.nav-dropdown > a').forEach(trigger => {
      trigger.addEventListener('click', function(e) {
        // Only intercept on mobile/tablet (when hamburger is visible)
        if (window.innerWidth > 900) return;
        e.preventDefault();
        e.stopPropagation();
        const dropdown = this.closest('.nav-dropdown');
        // Close other dropdowns
        navLinks.querySelectorAll('.nav-dropdown.mobile-open').forEach(dd => {
          if (dd !== dropdown) dd.classList.remove('mobile-open');
        });
        dropdown.classList.toggle('mobile-open');
      });
    });

    // Close menu on regular nav link click (not dropdown triggers)
    navLinks.querySelectorAll('a:not(.nav-dropdown > a):not(.lang-switch a):not(.mega-panel-link):not(.dropdown-item)').forEach(link => {
      link.addEventListener('click', () => {
        closeMobileMenu();
      });
    });
    // Also close on mega-panel-link and dropdown-item clicks
    navLinks.querySelectorAll('.mega-panel-link, .dropdown-item').forEach(link => {
      link.addEventListener('click', () => {
        closeMobileMenu();
      });
    });
  }

  // ---------- Products & Projects Mega-Panel 3×3 Collapse / Expand ----------
  // Both products and projects dropdowns: show 9 items (3×3), hide extras,
  // click view-all link to expand.
  // Handles: .mega-panel-link (flat grid) and .mega-module-link (grouped grid)
  (function initMegaPanelCollapse() {
    var isEn = /\/en\//.test(window.location.pathname);

    function applyCollapse(dropdown, allLinks, viewAllA) {
      if (allLinks.length <= 9) return;
      // Hide items 10+ by display:none (avoids nth-child issues with grouped grids)
      var hidden = [];
      for (var i = 9; i < allLinks.length; i++) {
        allLinks[i].style.display = 'none';
        hidden.push(allLinks[i]);
      }
      if (!viewAllA) return;
      viewAllA.removeAttribute('href');
      viewAllA.style.cursor = 'pointer';
      var expanded = false;
      var orig = (viewAllA.textContent || '').replace(/^\s*→\s*/, '').trim();
      var openLabel = '→ ' + orig;
      var closeLabel = isEn ? 'Collapse ▲' : (orig + ' ▲');
      viewAllA.textContent = openLabel;
      viewAllA.addEventListener('click', function(e) {
        e.preventDefault(); e.stopPropagation();
        expanded = !expanded;
        hidden.forEach(function(l) { l.style.display = expanded ? '' : 'none'; });
        viewAllA.textContent = expanded ? closeLabel : openLabel;
      });
    }

    // --- Pattern A: .nav-dropdown > mega-panel > mega-panel-link (most pages) ---
    document.querySelectorAll('.nav-dropdown').forEach(function(dd) {
      var a = dd.querySelector(':scope > a');
      if (!a) return;
      var href = a.getAttribute('href') || '';
      var isProducts = /products\.html/i.test(href);
      var isProjects = /projects\.html/i.test(href);
      if (!isProducts && !isProjects) return;
      var links = dd.querySelectorAll('.mega-panel-link');
      var viewAll = dd.querySelector('.mega-panel-viewall a');
      applyCollapse(dd, links, viewAll);
    });

    // --- Pattern B: mega-panel-v2 (products.html only) ---
    var megaV2 = document.querySelector('.mega-panel-v2');
    if (megaV2) {
      var links = megaV2.querySelectorAll('.mega-module-link');
      var viewAllRow = megaV2.querySelector('.mega-panel-viewall');
      if (!viewAllRow && links.length > 9) {
        viewAllRow = document.createElement('div');
        viewAllRow.className = 'mega-panel-viewall';
        viewAllRow.style.cssText = 'text-align:center;padding-top:16px;margin-top:8px;border-top:1px solid rgba(255,255,255,0.1);';
        var va = document.createElement('a');
        va.href = '#';
        va.textContent = isEn ? '→ View All Series' : '→ 瀏覽全部石材系列';
        viewAllRow.appendChild(va);
        megaV2.querySelector('.mega-panel-v2-inner').appendChild(viewAllRow);
      }
      applyCollapse(megaV2, links, viewAllRow ? viewAllRow.querySelector('a') : null);
    }
  })();

  // ---------- Series Card Click Handler (All versions) ----------
  // Handles both Chinese (.series-card-link) and English (a.series-overview-card) cards
  // Capture phase to beat lightbox handler; CSS touch-action:manipulation removes 300ms delay
  function handleSeriesCardClick(e) {
    var link = e.target.closest('a.series-card-link, a.series-overview-card');
    if (!link) return;
    var href = link.getAttribute('href');
    if (!href || !href.startsWith('#')) return;
    var target = document.querySelector(href);
    if (!target) return;
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    // Close mobile menu only if it's open (check navToggle state)
    if (navToggle && navToggle.classList.contains('active')) {
      closeMobileMenu();
    }
    // Immediate scroll, no delay - more reliable across browsers
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  document.addEventListener('click', handleSeriesCardClick, true);

  // ---------- Scroll Animations (Intersection Observer) ----------
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

/* [REMOVED DEAD] Product Filter — no .filter-btn or .product-card in HTML */


/* [KEPT] Contact Form — alert-based, keep for basic functionality */

  // ---------- Smooth scroll for anchor links ----------
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      // Skip series cards (handled by dedicated handler above)
      if (this.classList.contains('series-card-link') || this.classList.contains('series-overview-card')) return;
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        // Close mobile menu and dropdowns before scrolling
        closeMobileMenu();
        document.querySelectorAll('.nav-dropdown').forEach(dd => dd.classList.remove('mobile-open'));
        // Small delay to let menu close before scroll starts
        setTimeout(() => {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 50);
      }
    });
  });

});

// ---------- Fade In Up Animation Keyframe ----------
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(style);

// ── Universal Image Click-to-Zoom (Event Delegation) ──────────────────────
// Uses event delegation on document so clicks work even when overlays/pseudo-elements block direct binding

document.addEventListener('DOMContentLoaded', function() {

  // ── Collect all zoomable image sources on the page ──
  function getAllZoomableImages() {
    var results = [];
    // A) <img> tags in content areas
    document.querySelectorAll('#main-content img, .hero img, .section-padding img, .trust-bar img, .about-preview img, .products-page img, .stone-card-img img, .product-cat-image img, .gallery-item img, .masonry-item img, .card-img img, .masonry-img img').forEach(function(img) {
      if (!img.src || img.src.indexOf('data:') === 0) return;
      if (img.src.indexOf('logo-hsst') !== -1) return;
      if (isExcluded(img)) return;
      if (img.naturalWidth > 0 && img.naturalWidth < 80) return;
      results.push({ src: img.src, alt: img.alt || 'Image' });
    });
    // B) Background-image elements
    document.querySelectorAll('.scenario-card-bg, .news-card-image .bg, .about-image, .project-card, .featured-project-card .card-bg').forEach(function(el) {
      var bgSrc = getBgSrc(el);
      if (bgSrc) results.push({ src: bgSrc, alt: el.getAttribute('aria-label') || 'Image' });
    });
    return results;
  }

  function isExcluded(el) {
    var excludeSelectors = '.nav-logo, .mega-panel-icon, .partner-logo, .cert-badge, footer, nav, .nav-overlay, .stone-card-zoom, [class*="icon"], [class*="badge"], img[alt="HSST"]';
    return el.closest(excludeSelectors) !== null;
  }

  function getBgSrc(el) {
    var bgMatch = (el.style.backgroundImage || getComputedStyle(el).backgroundImage || '').match(/url\(['"]?([^'"]+)['"]?\)/);
    return bgMatch ? bgMatch[1] : null;
  }

  // ── Lightbox ──
  function openImageLightbox(src, alt) {
    var allImgs = getAllZoomableImages();
    var currentIndex = allImgs.findIndex(function(item) { return item.src === src || item.src.replace(/\?.*/, '') === src.replace(/\?.*/, ''); });
    if (currentIndex < 0) currentIndex = 0;

    var modal = document.createElement('div');
    modal.className = 'image-modal active';
    modal.dataset.index = currentIndex;
    modal.innerHTML =
      '<div class="image-modal-overlay"></div>' +
      '<div class="image-modal-content" style="max-width:92vw;max-height:90vh;">' +
        '<button class="image-modal-prev" style="position:absolute;left:16px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.9);border:none;border-radius:50%;width:44px;height:44px;cursor:pointer;font-size:1.2rem;z-index:10;display:' + (allImgs.length > 1 ? 'flex' : 'none') + ';align-items:center;justify-content:center;">&#8592;</button>' +
        '<button class="image-modal-next" style="position:absolute;right:16px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.9);border:none;border-radius:50%;width:44px;height:44px;cursor:pointer;font-size:1.2rem;z-index:10;display:' + (allImgs.length > 1 ? 'flex' : 'none') + ';align-items:center;justify-content:center;">&#8594;</button>' +
        '<button class="image-modal-close" style="position:absolute;top:16px;right:16px;background:#fff;border:none;border-radius:50%;width:44px;height:44px;cursor:pointer;color:#1A1A2E;font-size:1.3rem;font-weight:700;z-index:10;box-shadow:0 2px 8px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;">✕</button>' +
        '<img src="' + src + '" alt="' + alt + '" style="max-width:88vw;max-height:82vh;object-fit:contain;border-radius:8px;">' +
        '<div style="text-align:center;color:rgba(255,255,255,0.7);font-size:0.8rem;margin-top:8px;">' + alt + '</div>' +
      '</div>';
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';

    var imgEl = modal.querySelector('img');
    var prevBtn = modal.querySelector('.image-modal-prev');
    var nextBtn = modal.querySelector('.image-modal-next');

    function close() { modal.remove(); document.body.style.overflow = ''; }
    modal.querySelector('.image-modal-close').onclick = close;
    modal.querySelector('.image-modal-overlay').onclick = close;

    function navigate(dir) {
      var idx = parseInt(modal.dataset.index) + dir;
      if (idx < 0) idx = allImgs.length - 1;
      if (idx >= allImgs.length) idx = 0;
      modal.dataset.index = idx;
      imgEl.src = allImgs[idx].src;
      imgEl.alt = allImgs[idx].alt || '';
    }
    if (prevBtn) prevBtn.onclick = function() { navigate(-1); };
    if (nextBtn) nextBtn.onclick = function() { navigate(1); };

    function onKey(e) {
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') navigate(-1);
      if (e.key === 'ArrowRight') navigate(1);
    }
    document.addEventListener('keydown', onKey);
    modal._removeKey = function() { document.removeEventListener('keydown', onKey); };
  }

  // Expose globally for other code
  window.openImageLightbox = openImageLightbox;

  // ── Event Delegation: catch ALL clicks on the document ──
  document.addEventListener('click', function(e) {
    // Don't intercept clicks inside lightbox
    if (e.target.closest('.image-modal')) return;

    // Don't intercept nav/footer clicks
    if (e.target.closest('nav, footer, .nav-overlay, .nav-toggle, .lang-switch, .mega-panel')) return;

    // Don't intercept button/link clicks (we only want image clicks)
    if (e.target.closest('a:not(.series-card-link):not(.series-overview-card):not(.scenario-card):not(.stone-card):not(.gallery-item):not(.masonry-item):not(.featured-project-card), button, .btn, .nav-toggle')) return;

    var src = null;
    var alt = 'Image';

    // 1) Direct <img> click
    var img = e.target.closest('img');
    if (img && !isExcluded(img)) {
      if (img.src && img.src.indexOf('data:') !== 0 && img.src.indexOf('logo-hsst') === -1) {
        if (!img.naturalWidth || img.naturalWidth >= 80) {
          src = img.src;
          alt = img.alt || 'Image';
        }
      }
    }

    // 2) Click on container with background-image
    if (!src) {
      var bgSelectors = '.scenario-card-bg, .news-card-image .bg, .about-image, .project-card, .featured-project-card .card-bg';
      var bgEl = e.target.closest(bgSelectors);
      if (bgEl) {
        src = getBgSrc(bgEl);
        alt = bgEl.getAttribute('aria-label') || 'Image';
      }
    }

    // 3) Click on .scenario-card → get background from .scenario-card-bg
    if (!src) {
      var card = e.target.closest('.scenario-card');
      if (card) {
        var bg = card.querySelector('.scenario-card-bg');
        if (bg) {
          src = getBgSrc(bg);
          alt = card.querySelector('h3') ? card.querySelector('h3').textContent : 'Image';
        }
      }
    }

    // 4) Click on .stone-card or .stone-card-img → get inner <img>
    if (!src) {
      var stoneCard = e.target.closest('.stone-card, .stone-card-img');
      if (stoneCard) {
        var sImg = stoneCard.querySelector('img');
        if (sImg && !isExcluded(sImg)) {
          src = sImg.src;
          alt = sImg.alt || 'Stone Sample';
        }
      }
    }

    // 5) Click on .featured-project-card → get background from .card-bg
    if (!src) {
      var fpc = e.target.closest('.featured-project-card');
      if (fpc) {
        var cbg = fpc.querySelector('.card-bg');
        if (cbg) {
          src = getBgSrc(cbg);
          alt = 'Project Case';
        }
      }
    }

    // 6) Gallery / masonry items
    if (!src) {
      var galItem = e.target.closest('.gallery-item, .masonry-item');
      if (galItem) {
        var gImg = galItem.querySelector('img');
        if (gImg) {
          src = gImg.src;
          alt = gImg.alt || 'Image';
        }
      }
    }

    // If we found an image, open lightbox
    if (src) {
      e.preventDefault();
      e.stopPropagation();
      openImageLightbox(src, alt);
    }
  }, true); // capture phase to catch before overlay stops propagation

  // ── Set cursor: zoom-in on all zoomable images ──
  function setCursors() {
    document.querySelectorAll('#main-content img, .hero img, .section-padding img, .about-preview img, .stone-card-img img, .product-cat-image img, .gallery-item img, .masonry-item img').forEach(function(img) {
      if (isExcluded(img)) return;
      if (img.src && img.src.indexOf('data:') !== 0 && img.src.indexOf('logo-hsst') === -1) {
        if (!img.naturalWidth || img.naturalWidth >= 80) {
          img.style.cursor = 'zoom-in';
        }
      }
    });
    document.querySelectorAll('.scenario-card-bg, .about-image, .featured-project-card, .gallery-item, .masonry-item, .stone-card, .stone-card-img, .scenario-card').forEach(function(el) {
      el.style.cursor = 'zoom-in';
    });
  }
  setCursors();
  // Re-apply after AOS animations might change things
  setTimeout(setCursors, 1500);
});

// ═══════════════════════════════════════════
// P2: 动画与交互增强
// ═══════════════════════════════════════════

// ── 初始化 AOS ──
(function initAOS() {
  var script = document.createElement('script');
  script.src = 'https://unpkg.com/aos@2.3.4/dist/aos.js';
  script.onload = function() { AOS.init({ duration: 700, easing: 'ease-out-cubic', once: true, offset: 60, disable: 'phone' }); };
  document.head.appendChild(script);
})();

// ── 数字计数动画 ──
function animateCounter(el, target, suffix, duration) {
  if (el.dataset.animated) return;
  el.dataset.animated = 'true';
  var start = 0;
  var step = target / (duration / 16);
  var tick = function() {
    start += step;
    if (start >= target) {
      el.textContent = target + (suffix || '');
      el.classList.remove('counting');
      el.classList.add('counted');
      var parent = el.closest('.stat-item, .trust-item');
      if (parent) parent.classList.add('counted');
    } else {
      el.textContent = Math.floor(start) + (suffix || '');
      requestAnimationFrame(tick);
    }
  };
  el.classList.add('counting');
  requestAnimationFrame(tick);
}

// ── IntersectionObserver：数字计数触发 ──
var counterObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      var el = entry.target;
      var text = el.textContent.trim();
      var suffix = text.replace(/[\d.-]/g, '');
      var target = parseInt(text, 10);
      if (!isNaN(target)) animateCounter(el, target, suffix, 1800);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-number, .trust-number').forEach(function(el) {
  counterObserver.observe(el);
});

// ── IntersectionObserver：stat-item/trust-item 入场动画 ──
var itemObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      var items = entry.target.querySelectorAll ? entry.target.querySelectorAll('.stat-item, .trust-item') : [entry.target];
      items.forEach(function(item, i) {
        setTimeout(function() { item.classList.add('counted'); }, i * 150);
      });
      itemObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });

document.querySelectorAll('.about-stats, .trust-items, .trust-bar').forEach(function(el) {
  itemObserver.observe(el);
});

// WhatsApp Dual Protocol - Desktop: web.whatsapp.com, Mobile: wa.me (deep link)
(function() {
  var isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || 
                 ('ontouchstart' in window) || 
                 (navigator.maxTouchPoints > 0);
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href*="wa.me"], a[href*="web.whatsapp.com"]').forEach(function(link) {
      link.addEventListener('click', function(e) {
        var phone = '+85255380525';
        if (isMobile) {
          link.href = 'https://wa.me/' + phone;
        } else {
          link.href = 'https://web.whatsapp.com/send?phone=' + phone;
        }
      }, true);
    });
  });
})();

/* ── News Modal System ─────────────────────────────────────────────── */
(function () {
  var ACTIVE = 'active';

  function getOverlay() { return document.getElementById('news-modal-overlay'); }
  function getContent() { return document.getElementById('news-modal-content'); }

  function openNewsModal(id) {
    var ov = getOverlay(), co = getContent();
    if (!ov || !co) return;
    var tpl = document.getElementById('md-' + id);
    if (!tpl) return;
    co.innerHTML = tpl.innerHTML;
    ov.classList.add(ACTIVE);
    document.body.style.overflow = 'hidden';
    sessionStorage.setItem('newsModal', id);
  }

  function closeNewsModal(e) {
    if (e && e.target !== e.currentTarget) return;
    var ov = getOverlay();
    if (ov) ov.classList.remove(ACTIVE);
    document.body.style.overflow = '';
    sessionStorage.removeItem('newsModal');
  }

  window.openNewsModal = openNewsModal;
  window.closeNewsModal = closeNewsModal;

  document.addEventListener('DOMContentLoaded', function () {
    var ov = getOverlay();
    if (ov) {
      ov.addEventListener('click', closeNewsModal);
      var cb = ov.querySelector('.news-modal-close');
      if (cb) cb.addEventListener('click', function (e) { e.stopPropagation(); closeNewsModal(); });
    }
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { var o = getOverlay(); if (o && o.classList.contains(ACTIVE)) closeNewsModal(); }
    });

    /* Auto-open modal from URL param ?modal=modal-XX */
    var params = new URLSearchParams(window.location.search);
    var m = params.get('modal');
    if (m) setTimeout(function () { openNewsModal(m); }, 150);
  });

  /* Language switcher links are pre-set in HTML; verify and fix only if missing */
  function fixLangSwitcherHrefs() {
    var switcher = document.querySelector('.lang-switch');
    if (!switcher) return;
    
    var links = switcher.querySelectorAll('a');
    var currentPath = window.location.pathname;
    var isEnPage = currentPath.includes('/en/');
    
    // Determine page depth relative to site root
    // Root pages: /about.html, /index.html → depth 0
    // EN root pages: /en/about.html → depth 1 (inside en/)
    // CN subdirectory: /projects/airport.html → depth 1 (inside projects/)
    // EN subdirectory: /en/projects/airport.html → depth 2 (inside en/projects/)
    var pathParts = currentPath.replace(/^\/+|\/+$/g, '').split('/');
    var depth = pathParts.length - 1; // last element is the filename
    
    links.forEach(function(link) {
      var href = link.getAttribute('href');
      var text = link.textContent.trim().toUpperCase();
      if (!href) return;
      
      // Only fix if the href looks wrong (points to index.html as fallback)
      // Trust the HTML-provided hrefs which were manually verified
      // This function now only acts as a safety net for missing hrefs
      if (href === '' || href === '#' || href === 'index.html' || href === './index.html') {
        // Rebuild from current path
        var fileName = pathParts[pathParts.length - 1];
        if (isEnPage && text === 'TC') {
          // Go up from en/ to root
          var upPrefix = depth === 1 ? '../' : '../../';
          if (depth === 1) {
            link.setAttribute('href', upPrefix + fileName);
          } else {
            // EN subdirectory: /en/projects/airport.html → TC = ../../projects/airport.html
            var dir = pathParts[pathParts.length - 2];
            link.setAttribute('href', upPrefix + dir + '/' + fileName);
          }
        } else if (!isEnPage && text === 'EN') {
          // Go into en/ directory
          if (depth === 0) {
            link.setAttribute('href', 'en/' + fileName);
          } else {
            // CN subdirectory: /projects/airport.html → EN = ../en/projects/airport.html
            var dir2 = pathParts[pathParts.length - 2];
            link.setAttribute('href', '../en/' + dir2 + '/' + fileName);
          }
        }
      }
    });
  }

  /* Persist modal state through language switch */
  function patchLangSwitcher() {
    fixLangSwitcherHrefs();
    
    var links = document.querySelectorAll('.lang-switch a');
    links.forEach(function (link) {
      link.addEventListener('click', function (e) {
        var cur = sessionStorage.getItem('newsModal');
        if (!cur) return;
        e.preventDefault();
        var href = link.getAttribute('href');
        if (!href) return;
        href = href.replace(/([?&])modal=[^&]+/g, '');
        href = href.replace(/&{2,}/g, '&');
        href = href.replace(/\?&/g, '?');
        var sep = href.includes('?') ? '&' : '?';
        window.location.href = href + sep + 'modal=' + cur;
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patchLangSwitcher);
  } else {
    patchLangSwitcher();
  }
})();


// WhatsApp link fix: desktop uses web.whatsapp.com, mobile keeps wa.me
(function() {
  var isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  if (isMobile) return;
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href*="wa.me"]').forEach(function(link) {
      var href = link.getAttribute('href');
      var phone = href.replace(/wa\.me\/|web\.whatsapp\.com\/send\?phone=/gi, '').replace(/[^0-9+]/g, '');
      if (phone) {
        link.setAttribute('href', 'https://web.whatsapp.com/send?phone=' + phone);
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      }
    });
  });
})();


// ===== HSST Watermark: add company name to all content images & videos =====
(function() {
  var isEN = /^\/en/.test(window.location.pathname);
  var wmText = isEN ? 'HENGSHENG MARBLE S&T CO. LIMITED' : '恒生石材科技有限公司';

  // Skip these elements (logos, nav icons, footer, etc.)
  var skipSelectors = [
    '.nav-logo',
    '.mega-panel-icon',
    '.footer-logo',
    '.footer-brand',
    '.footer-social',
    '.trust-bar',
    '.whatsapp-float',
    'img[alt="HSST"]',
    '.contact-visit-map iframe',
    '.nav-center-title'
  ];

  function shouldSkip(el) {
    for (var i = 0; i < skipSelectors.length; i++) {
      try {
        if (el.matches(skipSelectors[i]) || el.closest(skipSelectors[i])) return true;
      } catch(e) {}
    }
    return false;
  }

  function ensureRelative(el) {
    var s = getComputedStyle(el);
    if (s.position === 'static') {
      el.style.position = 'relative';
    }
  }

  function addWM(container) {
    if (!container || container.querySelector(':scope > .hsst-wm')) return;
    ensureRelative(container);
    var d = document.createElement('div');
    d.className = 'hsst-wm';
    d.textContent = wmText;
    container.appendChild(d);
  }

  // Wrap a single <img> in a position:relative div and add watermark to the wrapper
  function wrapImgWithWM(img) {
    if (img.dataset.hsstWm || shouldSkip(img)) return;
    img.dataset.hsstWm = '1';
    var w = img.offsetWidth || img.naturalWidth || 0;
    var h = img.offsetHeight || img.naturalHeight || 0;
    if (w > 0 && w < 50) return;
    if (h > 0 && h < 50) return;

    var wrapper = document.createElement('div');
    wrapper.style.cssText = 'position:relative;overflow:hidden;border-radius:inherit;';
    // Preserve grid-column span for first-child in product-cat-image
    if (img === img.parentElement.firstElementChild) {
      wrapper.style.gridColumn = 'span 2';
    }
    img.parentNode.insertBefore(wrapper, img);
    wrapper.appendChild(img);
    addWM(wrapper);
  }

  function processImg(img) {
    if (img.dataset.hsstWm || shouldSkip(img)) return;
    img.dataset.hsstWm = '1';
    var w = img.offsetWidth || img.naturalWidth || 0;
    var h = img.offsetHeight || img.naturalHeight || 0;
    if (w > 0 && w < 50) return;
    if (h > 0 && h < 50) return;

    // Multi-image containers: wrap each image individually for per-image watermark
    var multiImgContainer =
      img.closest('.product-cat-image') ||
      null;
    if (multiImgContainer) {
      wrapImgWithWM(img);
      return;
    }

    // Single-image container types — add watermark to the container
    var container =
      img.closest('.stone-card-img') ||
      img.closest('.hero-grid-item') ||
      img.closest('.news-modal-img-wrap') ||
      img.closest('.about-video-wrap') ||
      img.closest('.contact-visit-map') ||
      img.closest('.case-card-img') ||
      null;

    if (container) {
      addWM(container);
      return;
    }

    // Fallback: add watermark to parent element
    var parent = img.parentElement;
    if (parent) addWM(parent);
  }

  function processVideo(v) {
    if (v.dataset.hsstWm || shouldSkip(v)) return;
    v.dataset.hsstWm = '1';

    var container =
      v.closest('.hero-grid-item') ||
      v.closest('.about-video-wrap') ||
      null;

    if (container) {
      addWM(container);
      return;
    }

    var parent = v.parentElement;
    if (parent) addWM(parent);
  }

  function processBgImages() {
    // News card background images
    document.querySelectorAll('.news-card-image').forEach(function(nc) {
      if (nc.querySelector(':scope > .hsst-wm')) return;
      addWM(nc);
    });
  }

  function processAll() {
    // Videos
    document.querySelectorAll('video').forEach(processVideo);

    // Images
    document.querySelectorAll('img').forEach(function(img) {
      if (img.complete) {
        processImg(img);
      } else {
        img.addEventListener('load', function() { processImg(img); });
      }
    });

    // Background-image elements
    processBgImages();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processAll);
  } else {
    processAll();
  }
})();
