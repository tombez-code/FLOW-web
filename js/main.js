/**
 * SkolaFlow - Main JavaScript
 * Replaces Webflow.js interactions: nav dropdowns, burger menu, animations
 */
(function() {
  'use strict';

  // ── Utility ──────────────────────────────────────────────────────────────
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  // ── Nav Dropdowns ────────────────────────────────────────────────────────
  function initDropdowns() {
    var dropdowns = $$('.nav-dropdown-link');
    var activeDropdown = null;
    var closeTimer = null;

    function cancelClose() {
      if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
    }

    function openDropdown(dd) {
      cancelClose();
      var block = dd.querySelector('.dropdown-block');
      var layout = dd.querySelector('.dropdown-layout');
      if (!block || !layout) return;

      // Instantly dismiss any previously open dropdown without animation
      if (activeDropdown && activeDropdown !== dd) {
        var prev = activeDropdown;
        var prevBlock = prev.querySelector('.dropdown-block');
        var prevLayout = prev.querySelector('.dropdown-layout');
        if (prevBlock && prevLayout) {
          prev.classList.remove('is-open');
          prevLayout.style.transition = 'none';
          prevLayout.style.opacity = '0';
          prevLayout.style.transform = 'translate3d(0px, 3rem, 0px) scale3d(0.8, 0.8, 1)';
          prevBlock.style.display = 'none';
        }
      }

      activeDropdown = dd;
      dd.classList.add('is-open');
      block.style.display = 'block';
      requestAnimationFrame(function() {
        layout.style.transition = 'transform 0.2s ease, opacity 0.2s ease';
        layout.style.transform = 'translate3d(0px, 0px, 0px) scale3d(1, 1, 1)';
        layout.style.opacity = '1';
      });
    }

    function closeDropdown(dd) {
      var block = dd.querySelector('.dropdown-block');
      var layout = dd.querySelector('.dropdown-layout');
      if (!block || !layout) return;
      dd.classList.remove('is-open');
      if (activeDropdown === dd) activeDropdown = null;
      layout.style.transition = 'transform 0.2s ease, opacity 0.2s ease';
      layout.style.transform = 'translate3d(0px, 3rem, 0px) scale3d(0.8, 0.8, 1)';
      layout.style.opacity = '0';
      setTimeout(function() {
        if (!dd.classList.contains('is-open')) block.style.display = 'none';
      }, 220);
    }

    function scheduleClose(dd) {
      cancelClose();
      closeTimer = setTimeout(function() {
        closeDropdown(dd);
        closeTimer = null;
      }, 120);
    }

    dropdowns.forEach(function(dd) {
      var layout = dd.querySelector('.dropdown-layout');

      // Open immediately when hovering the nav label row
      dd.addEventListener('mouseenter', function() { openDropdown(dd); });

      // Close with a short delay — cancelled if mouse enters another nav item
      dd.addEventListener('mouseleave', function(e) {
        // If moving into the dropdown layout itself, stay open
        var dest = e.relatedTarget;
        if (dest && layout && (dest === layout || layout.contains(dest))) return;
        scheduleClose(dd);
      });

      // Keep open while the mouse is inside the dropdown panel
      if (layout) {
        layout.addEventListener('mouseenter', function() { cancelClose(); });
        layout.addEventListener('mouseleave', function() { scheduleClose(dd); });
      }

      // Click/tap toggle (mobile + desktop)
      var label = dd.querySelector('.nav-dropdown-link-text');
      if (label) {
        label.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          if (dd.classList.contains('is-open')) {
            closeDropdown(dd);
          } else {
            openDropdown(dd);
          }
        });
      }
    });

    // Close on outside click
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.nav-dropdown-link')) {
        cancelClose();
        dropdowns.forEach(closeDropdown);
        activeDropdown = null;
      }
    });
  }

  // ── Burger / Aside Menu ──────────────────────────────────────────────────
  function initBurgerMenu() {
    var burgerBtn = $('.button-for-aside-menu');
    var asideMenu = $('.aside-menu');
    var menuClose = $('.menu-close');
    var menuLinks = $('.menu-links');
    var menuMainLinks = $('.menu-main-links');

    if (!burgerBtn || !asideMenu) return;

    var isOpen = false;

    function openMenu() {
      isOpen = true;
      asideMenu.style.display = 'block';
      document.body.style.overflow = 'hidden';

      requestAnimationFrame(function() {
        var bg = asideMenu.querySelector('.menu-background');
        if (bg) {
          bg.style.transition = 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
          bg.style.transform = 'translate3d(0%, 0px, 0px)';
        }
        if (menuClose) {
          menuClose.style.transition = 'opacity 0.3s ease 0.2s';
          menuClose.style.opacity = '1';
        }
        if (menuLinks) {
          menuLinks.style.transition = 'opacity 0.3s ease 0.15s';
          menuLinks.style.opacity = '1';
        }
        if (menuMainLinks) {
          menuMainLinks.style.transition = 'transform 0.4s ease 0.1s, opacity 0.4s ease 0.1s';
          menuMainLinks.style.transform = 'translate3d(0px, 0px, 0px)';
          menuMainLinks.style.opacity = '1';
        }
      });
    }

    function closeMenu() {
      isOpen = false;
      var bg = asideMenu.querySelector('.menu-background');
      if (bg) {
        bg.style.transition = 'transform 0.35s cubic-bezier(0.4, 0, 0.2, 1)';
        bg.style.transform = 'translate3d(101%, 0px, 0px)';
      }
      if (menuClose) {
        menuClose.style.transition = 'opacity 0.2s ease';
        menuClose.style.opacity = '0';
      }
      if (menuLinks) {
        menuLinks.style.transition = 'opacity 0.2s ease';
        menuLinks.style.opacity = '0';
      }
      if (menuMainLinks) {
        menuMainLinks.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
        menuMainLinks.style.transform = 'translate3d(0px, 4em, 0px)';
        menuMainLinks.style.opacity = '0';
      }
      setTimeout(function() {
        asideMenu.style.display = 'none';
        document.body.style.overflow = '';
      }, 380);
    }

    burgerBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      isOpen ? closeMenu() : openMenu();
    });

    if (menuClose) menuClose.addEventListener('click', closeMenu);

    // Close on Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && isOpen) closeMenu();
    });
  }

  // ── Scroll Animations (fade-in on scroll) ────────────────────────────────
  function initScrollAnimations() {
    // Selectors to EXCLUDE from scroll animation (nav/menu controlled by JS)
    var EXCLUDE = [
      '.nav', '.w-nav', '.nav-dropdown-link', '.dropdown-block',
      '.dropdown-layout', '.aside-menu', '.menu-layout', '.menu-background',
      '.menu-close', '.menu-links', '.menu-main-links', '.menu-cover-image',
      '.link-text-yellow-dot', '.link-text', '.burger-button-backgrouind',
      '.footer-shadow', '.main-button-shadow', '.main-button-line',
      '.home-hero-image-wrapper'
    ];

    var all = $$('[style*="opacity: 0"]');
    var animated = all.filter(function(el) {
      return !EXCLUDE.some(function(sel) {
        return el.matches(sel) || el.closest('.dropdown-block, .aside-menu, .nav');
      });
    });

    if (!('IntersectionObserver' in window)) {
      animated.forEach(function(el) {
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
      return;
    }

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
          el.style.opacity = '1';
          el.style.transform = 'translate3d(0,0,0) scale3d(1,1,1)';
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    animated.forEach(function(el) {
      observer.observe(el);
    });
  }

  // ── Testimonial Carousel ─────────────────────────────────────────────────
  // Matches live Webflow layout: slides are display:inline-block side-by-side,
  // mask has overflow:visible, slider has overflow:visible. The parent
  // .section has overflow:hidden which clips the peek.
  // Navigation animates the mask via CSS transform: translateX.
  function initCarousels() {
    var sliders = $$('.w-slider');
    sliders.forEach(function(slider) {
      var mask   = slider.querySelector('.w-slider-mask');
      var slides = $$('.w-slide', slider);
      var dots   = $$('.w-slider-dot', slider);
      var prevBtn = slider.querySelector('.w-slider-arrow-left');
      var nextBtn = slider.querySelector('.w-slider-arrow-right');

      if (!mask || slides.length <= 1) return;

      // ── Layout: inline-block slides side by side ──────────────────────────
      slider.style.overflow = 'visible';
      mask.style.overflow   = 'visible';
      mask.style.whiteSpace = 'nowrap';

      var slideWidth = mask.offsetWidth || slider.offsetWidth || 800;

      slides.forEach(function(s) {
        s.style.display        = 'inline-block';
        s.style.verticalAlign  = 'top';
        s.style.whiteSpace     = 'normal';
        s.style.width          = slideWidth + 'px';
        s.removeAttribute('aria-hidden');
      });

      var current = 0;
      var isAnimating = false;

      function goTo(idx, animate) {
        if (idx < 0) idx = slides.length - 1;
        if (idx >= slides.length) idx = 0;

        current = idx;

        // Update mask position
        var offset = -(idx * slideWidth);
        if (animate !== false) {
          mask.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
          isAnimating = true;
          var onEnd = function() {
            mask.removeEventListener('transitionend', onEnd);
            isAnimating = false;
          };
          mask.addEventListener('transitionend', onEnd);
        } else {
          mask.style.transition = 'none';
        }
        mask.style.transform = 'translateX(' + offset + 'px)';

        // Update aria on slides
        slides.forEach(function(s, i) {
          if (i === idx) s.removeAttribute('aria-hidden');
          else s.setAttribute('aria-hidden', 'true');
        });

        // Update dots
        dots.forEach(function(d, i) {
          d.classList.toggle('w-active', i === idx);
          d.setAttribute('aria-pressed', i === idx ? 'true' : 'false');
        });
      }

      // Initialise without animation
      goTo(0, false);

      // Arrow buttons
      if (nextBtn) nextBtn.addEventListener('click', function() {
        if (!isAnimating) goTo(current + 1);
      });
      if (prevBtn) prevBtn.addEventListener('click', function() {
        if (!isAnimating) goTo(current - 1);
      });

      // Dot buttons
      dots.forEach(function(d, i) {
        d.addEventListener('click', function() {
          if (!isAnimating) goTo(i);
        });
      });

      // Touch / swipe support
      var touchStartX = 0;
      slider.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
      }, { passive: true });
      slider.addEventListener('touchend', function(e) {
        var dx = e.changedTouches[0].clientX - touchStartX;
        if (Math.abs(dx) > 40) {
          if (!isAnimating) goTo(dx < 0 ? current + 1 : current - 1);
        }
      }, { passive: true });

      // "více / more" expand for truncated testimonials
      $$('.carousel-testimonial-more', slider).forEach(function(btn) {
        btn.addEventListener('click', function() {
          var testimonial = btn.closest('.carousel-testimonial');
          var truncated = testimonial && testimonial.querySelector('.carousel-testimonial-truncate');
          if (truncated) {
            truncated.style.webkitLineClamp = 'unset';
            truncated.style.display = 'block';
            truncated.style.overflow = 'visible';
          }
          btn.style.display = 'none';
        });
      });

      // Auto-play every 6 s; pause on hover/focus
      var interval = setInterval(function() { goTo(current + 1); }, 6000);
      slider.addEventListener('mouseenter', function() { clearInterval(interval); });
      slider.addEventListener('mouseleave', function() {
        clearInterval(interval);
        interval = setInterval(function() { goTo(current + 1); }, 6000);
      });
    });
  }

  // ── Active Nav Link ──────────────────────────────────────────────────────
  function markActiveNavLink() {
    var path = window.location.pathname;
    $$('a[href]').forEach(function(a) {
      var href = a.getAttribute('href');
      if (!href) return;
      // Normalize
      var hrefPath = href.replace(/\.html$/, '').replace(/\/index$/, '/') || '/';
      var currentPath = path.replace(/\.html$/, '').replace(/\/index$/, '/') || '/';
      if (hrefPath === currentPath || (hrefPath !== '/' && currentPath.endsWith(hrefPath))) {
        a.classList.add('w--current');
        a.setAttribute('aria-current', 'page');
      }
    });
  }

  // ── Smooth Anchor Scroll ─────────────────────────────────────────────────
  function initSmoothScroll() {
    $$('a[href^="#"]').forEach(function(a) {
      a.addEventListener('click', function(e) {
        var id = a.getAttribute('href').slice(1);
        var target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  // ── Webflow w-mod-js class ───────────────────────────────────────────────
  function initWebflowCompat() {
    // Add w-mod-js class to html element (required for CSS to work properly)
    document.documentElement.classList.add('w-mod-js');
    // Remove hidden state from w-mod-js-dependent elements
    document.documentElement.classList.add('w-mod-ix');
  }

  // ── FAQ Accordion (w-dropdown) ───────────────────────────────────────────
  function initAccordions() {
    var accordions = $$('.accordion.w-dropdown');
    if (!accordions.length) return;

    var ADD_ICON = 'images/67b351f4c755934221b66585_add-fill0-wght600-grad0-opsz24_20_1_.svg';

    // Fix icon path for subdirectory pages
    var pathDepth = (window.location.pathname.match(/\//g) || []).length - 1;
    var prefix = pathDepth > 1 ? '../' : '';
    var addIcon = prefix + ADD_ICON;

    accordions.forEach(function(acc) {
      var toggle = acc.querySelector('.accordion-toggle');
      var content = acc.querySelector('.accordion-dropdown');
      var icon = acc.querySelector('.accordion-icon-block img');
      if (!toggle || !content) return;

      // Ensure proper initial state
      content.style.display = 'none';
      content.style.opacity = '0';
      content.style.height = '0px';
      acc.classList.remove('w--open');

      toggle.addEventListener('click', function(e) {
        e.preventDefault();
        var isOpen = acc.classList.contains('w--open');

        // Close all others (accordion behavior)
        accordions.forEach(function(other) {
          if (other !== acc && other.classList.contains('w--open')) {
            other.classList.remove('w--open');
            var otherContent = other.querySelector('.accordion-dropdown');
            var otherIcon = other.querySelector('.accordion-icon-block img');
            if (otherContent) {
              otherContent.style.opacity = '0';
              otherContent.style.height = '0px';
              setTimeout(function() { otherContent.style.display = 'none'; }, 250);
            }
            if (otherIcon) otherIcon.style.transform = 'rotate(0deg)';
          }
        });

        if (isOpen) {
          // Close this one
          acc.classList.remove('w--open');
          content.style.opacity = '0';
          content.style.height = '0px';
          setTimeout(function() { content.style.display = 'none'; }, 250);
          if (icon) icon.style.transform = 'rotate(0deg)';
        } else {
          // Open this one
          acc.classList.add('w--open');
          content.style.display = 'block';
          content.style.transition = 'opacity 0.25s ease, height 0.25s ease';
          // Get natural height
          content.style.height = 'auto';
          var h = content.scrollHeight + 'px';
          content.style.height = '0px';
          requestAnimationFrame(function() {
            content.style.opacity = '1';
            content.style.height = h;
          });
          if (icon) { icon.style.transition = 'transform 0.25s ease'; icon.style.transform = 'rotate(45deg)'; }
        }
      });
    });
  }

  // ── CDN Fallback for Missing Images ─────────────────────────────────────
  // If a local image fails to load, try the Webflow CDN as fallback
  function initImageFallbacks() {
    var CDN_ST  = 'https://cdn.prod.website-files.com/67b351f4c755934221b66277/';
    var CDN_CMS = 'https://cdn.prod.website-files.com/67b351f4c755934221b662d0/';

    // Map: local filename → CDN URL (fallback for any images still missing locally)
    // Note: team photos are now all downloaded locally; keeping CDN fallback for blog/misc images
    var cdnMap = {
      // These team photos are now local — CDN fallback kept as safety net
      '67fa0478832cdc06e495b6b5_65450e48ec70f7d838edf89a_MichaelaKralova.jpeg': CDN_CMS + '67fa0478832cdc06e495b6b5_65450e48ec70f7d838edf89a_MichaelaKralova.jpeg',
      '67fa0478ff3797629639b018_677e4374d11099bb60f941d4_WhatsApp_2520Image_25202025-01-06_2520at_252014.01.53_2520_2_.jpeg': CDN_CMS + '67fa0478ff3797629639b018_677e4374d11099bb60f941d4_WhatsApp%2520Image%25202025-01-06%2520at%252014.01.53%2520(2).jpeg',
      // Blog images
      '67fa05ad909cf7ec7a5bd386_64131a4573926c53e4c8212c_marv_2520shamma_2520petr_2520mara_2520FLOW.png':         CDN_CMS + '67fa05ad909cf7ec7a5bd386_64131a4573926c53e4c8212c_marv%2520shamma%2520petr%2520mara%2520FLOW.png',
      '67fa05ae85195bec98df752c_6413163efec18fbaf55f0913_marv_2520shamma_2520louis_2520theo_2520FLOW.png':        CDN_CMS + '67fa05ae85195bec98df752c_6413163efec18fbaf55f0913_marv%2520shamma%2520louis%2520theo%2520FLOW.png',
      '67fa05ae0ed6b068638595e2_641315d2358366a47666a6bb_marv_2520shamma_2520TEDx_2520FLOW.png':                  CDN_CMS + '67fa05ae0ed6b068638595e2_641315d2358366a47666a6bb_marv%2520shamma%2520TEDx%2520FLOW.png',
      '67fa05ae59969dafd32603ab_64131bc6a541e877293bbb08_marv_2520shamma_2520eduzin.png':                         CDN_CMS + '67fa05ae59969dafd32603ab_64131bc6a541e877293bbb08_marv%2520shamma%2520eduzin.png',
      '67fa05af4ab03eb3caaeacca_6413191c73926ca33fc80f56_marv_2520shamma_2520talk_2520zlomu.png':                 CDN_CMS + '67fa05af4ab03eb3caaeacca_6413191c73926ca33fc80f56_marv%2520shamma%2520talk%2520zlomu.png',
      '67fa05ae93bc5ebc07b9e7e7_641317711bd52332d6f5038d_marv_2520shamma_2520na_2520vlne_2520podnikani_2520FLOW.png': CDN_CMS + '67fa05ae93bc5ebc07b9e7e7_641317711bd52332d6f5038d_marv%2520shamma%2520na%2520vlne%2520podnikani%2520FLOW.png',
      '67fa05ae61e24d76e7339090_62bc62bda6c21724b173b9bf_Flow_zalozeni_Flow_pilire.jpeg': CDN_CMS + '67fa05ae61e24d76e7339090_62bc62bda6c21724b173b9bf_Flow_zalozeni_Flow_pilire.jpeg',
      '67fa05ad1009eed5417a453c_629a06f52615627d37c29fd6_1_zMG2xRokwU0TADG7tNC7Lw.jpeg': CDN_CMS + '67fa05ad1009eed5417a453c_629a06f52615627d37c29fd6_1_zMG2xRokwU0TADG7tNC7Lw.jpeg',
      '67fa05ad1009eed5417a450b_629a06bc26638588a3f21bda_0_KOTOokIMM2pmbM9Y.jpeg': CDN_CMS + '67fa05ad1009eed5417a450b_629a06bc26638588a3f21bda_0_KOTOokIMM2pmbM9Y.jpeg',
      '67fa05ad1009eed5417a450f_629a06bc64c671f7ddc0d9c1_0_xarQLghBIcgoXo5n.jpeg': CDN_CMS + '67fa05ad1009eed5417a450f_629a06bc64c671f7ddc0d9c1_0_xarQLghBIcgoXo5n.jpeg',
      '67fa05ad85195bec98df7518_629f3156638026433e34a100_skolaflow_marvshammakids2.jpeg': CDN_CMS + '67fa05ad85195bec98df7518_629f3156638026433e34a100_skolaflow_marvshammakids2.jpeg',
      '67fa05ad85195bec98df751c_62aaf28906b229972a5ddbc1_skolaflow_4pilire.jpeg': CDN_CMS + '67fa05ad85195bec98df751c_62aaf28906b229972a5ddbc1_skolaflow_4pilire.jpeg',
      '67fa05ae61e24d76e733903e_62bc62886d06e59fd8fc8b99_Flow_tematicke_pilire.jpeg': CDN_CMS + '67fa05ae61e24d76e733903e_62bc62886d06e59fd8fc8b99_Flow_tematicke_pilire.jpeg',
      '67fa05ae61e24d76e7339046_62bc6246fe7b1f7566ab5c9d_Flow_dovednosti.jpeg': CDN_CMS + '67fa05ae61e24d76e7339046_62bc6246fe7b1f7566ab5c9d_Flow_dovednosti.jpeg',
      // Timeline SVG
      '67c582cad2d3c9b602f5e136_66d96930ad1e7d10bbc6aa59_skola_20flow_20timeline.svg': CDN_CMS + '67c582cad2d3c9b602f5e136_66d96930ad1e7d10bbc6aa59_skola%20flow%20timeline.svg',
      // Static icons
      '67b351f4c755934221b66561_icon-element-2_20_1_.svg':  CDN_ST + '67b351f4c755934221b66561_icon-element-2%20(1).svg',
      '67b351f4c755934221b6657f_design-element-1_20_1_.svg': CDN_ST + '67b351f4c755934221b6657f_design-element-1%20(1).svg',
      '67b351f4c755934221b66585_add-fill0-wght600-grad0-opsz24_20_1_.svg': CDN_ST + '67b351f4c755934221b66585_add-fill0-wght600-grad0-opsz24%20(1).svg',
      '67b351f4c755934221b66647_location-on-fill0-wght600-grad0-opsz24_20_1_.svg': CDN_ST + '67b351f4c755934221b66647_location-on-fill0-wght600-grad0-opsz24%20(1).svg',
      '67b351f4c755934221b66649_local-library-fill0-wght600-grad0-opsz24_20_1_.svg': CDN_ST + '67b351f4c755934221b66649_local-library-fill0-wght600-grad0-opsz24%20(1).svg',
      '67b351f4c755934221b6669e_facebook-logo-black.svg': CDN_ST + '67b351f4c755934221b6669e_facebook-logo-black.svg',
      '67b351f4c755934221b666a2_linkedin-logo-black.svg': CDN_ST + '67b351f4c755934221b666a2_linkedin-logo-black.svg',
      '67b351f4c755934221b666a3_instagram-logo-dark.svg': CDN_ST + '67b351f4c755934221b666a3_instagram-logo-dark.svg',
      '6900e0b366ea2612977f2440_Copy_20of_20_20Flow_OpenDay_Post1Announce-min.png': CDN_ST + '6900e0b366ea2612977f2440_Copy%20of%20%20Flow_OpenDay_Post1Announce-min.png',
      '696e29589da08f0f2728144e_WhatsApp_20Image_202026-01-19_20at_2013.47.52.jpeg': CDN_ST + '696e29589da08f0f2728144e_WhatsApp%20Image%202026-01-19%20at%2013.47.52.jpeg',
    };

    $$('img[src]').forEach(function(img) {
      var src = img.getAttribute('src');
      // Get just the filename from the local path
      var filename = src.split('/').pop();
      if (cdnMap[filename]) {
        img.addEventListener('error', function onErr() {
          img.removeEventListener('error', onErr);
          img.src = cdnMap[filename];
        });
      }
    });
  }

  // ── Hero Image Visibility ─────────────────────────────────────────────────
  function initHeroImage() {
    // Make hero cover image visible (Webflow normally animates it in)
    var heroImg = $('.cover-image.is-parallax');
    if (heroImg) {
      heroImg.style.display = '';
      heroImg.style.opacity = '1';
      heroImg.style.transform = 'translate3d(0,0,0) scale3d(1,1,1)';
    }
    // Also show the hero image wrapper animation
    var scrollAnim = $('.scrolling-animation.with-shadow');
    if (scrollAnim) {
      scrollAnim.style.transform = 'translate3d(0,0,0)';
      scrollAnim.style.opacity = '1';
    }

    // Unhide about-grid section images hidden by Webflow's interaction engine
    // (Webflow sets display:none + scale(1.3) on these; without interactions they stay hidden)
    $$('.about-grid .cover-image.is-parallax').forEach(function(img) {
      img.style.display = 'block';
      img.style.transform = 'translate3d(0px, -7%, 0px) scale3d(1, 1, 1)';
    });
    // Hide the colour-wipe overlay that Webflow would animate away
    $$('.about-grid .animation-color-background').forEach(function(el) {
      el.style.display = 'none';
    });

    // Show achievement blocks hidden by Webflow interactions
    $$('.achievement-block').forEach(function(el) {
      el.style.opacity = '1';
      el.style.transform = 'translate3d(0,0,0)';
    });
  }

  // ── Lightbox Gallery ─────────────────────────────────────────────────────
  function initLightbox() {
    var triggers = $$('.w-lightbox');
    if (!triggers.length) return;

    // Collect images from gallery on the page
    function buildGallery(startTrigger) {
      var imgs = [];
      triggers.forEach(function(a) {
        var thumb = a.querySelector('img.gallery-thumbnail');
        if (!thumb) return;
        // Prefer the largest srcset src, fall back to src
        var src = thumb.src;
        var srcset = thumb.getAttribute('srcset');
        if (srcset) {
          // Pick the largest size (last entry in srcset)
          var parts = srcset.split(',').map(function(s) { return s.trim().split(/\s+/); });
          // sort by declared width (px number)
          parts.sort(function(a, b) {
            return (parseInt(b[1]) || 0) - (parseInt(a[1]) || 0);
          });
          if (parts[0] && parts[0][0]) src = parts[0][0];
        }
        imgs.push({ src: src, alt: thumb.alt || '' });
      });
      var startIdx = 0;
      triggers.forEach(function(a, i) { if (a === startTrigger) startIdx = i; });
      return { imgs: imgs, startIdx: startIdx };
    }

    // Build lightbox DOM once
    var overlay = document.createElement('div');
    overlay.id = 'sf-lightbox';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.innerHTML = [
      '<div class="sf-lb-backdrop"></div>',
      '<button class="sf-lb-close" aria-label="Zavřít">&#x2715;</button>',
      '<button class="sf-lb-prev" aria-label="Předchozí">&#x2039;</button>',
      '<button class="sf-lb-next" aria-label="Další">&#x203A;</button>',
      '<div class="sf-lb-img-wrap"><img class="sf-lb-img" src="" alt=""></div>',
      '<div class="sf-lb-counter"></div>'
    ].join('');

    // Inject styles
    var style = document.createElement('style');
    style.textContent = [
      '#sf-lightbox{position:fixed;inset:0;z-index:9999;display:none;align-items:center;justify-content:center;}',
      '#sf-lightbox.is-open{display:flex;}',
      '.sf-lb-backdrop{position:absolute;inset:0;background:rgba(10,5,2,.88);cursor:zoom-out;}',
      '.sf-lb-img-wrap{position:relative;z-index:2;max-width:90vw;max-height:90vh;display:flex;align-items:center;justify-content:center;}',
      '.sf-lb-img{max-width:90vw;max-height:88vh;object-fit:contain;border-radius:12px;box-shadow:0 8px 48px rgba(0,0,0,.6);transition:opacity .25s ease;}',
      '.sf-lb-img.is-loading{opacity:0;}',
      '.sf-lb-close,.sf-lb-prev,.sf-lb-next{position:absolute;z-index:3;background:rgba(255,255,255,.12);border:none;cursor:pointer;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;transition:background .2s;}',
      '.sf-lb-close:hover,.sf-lb-prev:hover,.sf-lb-next:hover{background:rgba(255,255,255,.25);}',
      '.sf-lb-close{top:1.2rem;right:1.4rem;width:2.6rem;height:2.6rem;font-size:1.2rem;}',
      '.sf-lb-prev,.sf-lb-next{top:50%;transform:translateY(-50%);width:3.2rem;height:3.2rem;font-size:2.4rem;line-height:1;}',
      '.sf-lb-prev{left:1.2rem;}',
      '.sf-lb-next{right:1.2rem;}',
      '.sf-lb-counter{position:absolute;bottom:1.4rem;left:50%;transform:translateX(-50%);z-index:3;color:rgba(255,255,255,.7);font-size:.9rem;letter-spacing:.06em;}'
    ].join('');
    document.head.appendChild(style);
    document.body.appendChild(overlay);

    var imgEl      = overlay.querySelector('.sf-lb-img');
    var counterEl  = overlay.querySelector('.sf-lb-counter');
    var closeBtn   = overlay.querySelector('.sf-lb-close');
    var prevBtn    = overlay.querySelector('.sf-lb-prev');
    var nextBtn    = overlay.querySelector('.sf-lb-next');
    var backdropEl = overlay.querySelector('.sf-lb-backdrop');

    var gallery = [];
    var currentIdx = 0;

    function show(idx) {
      if (idx < 0) idx = gallery.length - 1;
      if (idx >= gallery.length) idx = 0;
      currentIdx = idx;
      var item = gallery[idx];
      imgEl.classList.add('is-loading');
      var tmp = new Image();
      tmp.onload = function() {
        imgEl.src = item.src;
        imgEl.alt = item.alt;
        imgEl.classList.remove('is-loading');
      };
      tmp.onerror = function() {
        imgEl.src = item.src;
        imgEl.classList.remove('is-loading');
      };
      tmp.src = item.src;
      counterEl.textContent = (idx + 1) + ' / ' + gallery.length;
      prevBtn.style.display = gallery.length > 1 ? '' : 'none';
      nextBtn.style.display = gallery.length > 1 ? '' : 'none';
    }

    function open(trigger) {
      var data = buildGallery(trigger);
      gallery = data.imgs;
      overlay.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      show(data.startIdx);
    }

    function close() {
      overlay.classList.remove('is-open');
      document.body.style.overflow = '';
      imgEl.src = '';
    }

    // Wire events
    triggers.forEach(function(a) {
      a.addEventListener('click', function(e) {
        e.preventDefault();
        open(a);
      });
    });

    closeBtn.addEventListener('click', close);
    backdropEl.addEventListener('click', close);
    prevBtn.addEventListener('click', function() { show(currentIdx - 1); });
    nextBtn.addEventListener('click', function() { show(currentIdx + 1); });

    document.addEventListener('keydown', function(e) {
      if (!overlay.classList.contains('is-open')) return;
      if (e.key === 'Escape')      close();
      if (e.key === 'ArrowLeft')   show(currentIdx - 1);
      if (e.key === 'ArrowRight')  show(currentIdx + 1);
    });

    // Touch swipe on lightbox
    var swipeStartX = 0;
    overlay.addEventListener('touchstart', function(e) { swipeStartX = e.touches[0].clientX; }, { passive: true });
    overlay.addEventListener('touchend', function(e) {
      var dx = e.changedTouches[0].clientX - swipeStartX;
      if (Math.abs(dx) > 40) show(dx < 0 ? currentIdx + 1 : currentIdx - 1);
    }, { passive: true });

    // Show gallery-block opacity (hidden by scroll animation fallback)
    $$('.gallery-lightbox-block').forEach(function(el) { el.style.opacity = '1'; });
  }

  // ── Footer Shadow Effect ─────────────────────────────────────────────────
  function initFooterShadow() {
    var shadows = $$('.footer-shadow');
    shadows.forEach(function(s) {
      s.style.opacity = '1';
    });
  }

  // ── Custom Checkboxes ────────────────────────────────────────────────────
  function initCustomCheckboxes() {
    $$('.w-checkbox-input--inputType-custom').forEach(function(customBox) {
      var label = customBox.closest('.w-checkbox');
      var input = label ? label.querySelector('input[type="checkbox"]') : null;
      if (!input) return;

      function updateVisual() {
        if (input.checked) {
          customBox.classList.add('w--redirected-checked');
        } else {
          customBox.classList.remove('w--redirected-checked');
        }
      }

      // Click on custom box toggles checkbox
      // preventDefault stops the parent <label> from double-toggling the input
      customBox.addEventListener('click', function(e) {
        e.preventDefault();
        input.checked = !input.checked;
        updateVisual();
      });

      // Clicking label text also works via native label behaviour
      input.addEventListener('change', updateVisual);

      // Set initial visual state
      updateVisual();
    });
  }

  // ── Initialize All ───────────────────────────────────────────────────────
  ready(function() {
    initWebflowCompat();
    initImageFallbacks();
    initDropdowns();
    initBurgerMenu();
    initScrollAnimations();
    initCarousels();
    markActiveNavLink();
    initSmoothScroll();
    initHeroImage();
    initFooterShadow();
    initAccordions();
    initLightbox();
    initCustomCheckboxes();

    console.log('[SkolaFlow] JS initialized');
  });

})();
