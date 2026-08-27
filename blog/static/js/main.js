/* ismat.dev — shared behaviour: theme, mobile nav, scroll reveal. */
(function () {
    'use strict';

    /* --- Dark / light theme --------------------------------------------- */
    var toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.addEventListener('click', function () {
            var next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
            document.documentElement.dataset.theme = next;
            try {
                localStorage.setItem('theme', next);
            } catch (e) { /* storage blocked — theme still applies for this page */ }
        });
    }

    /* --- Mobile navigation ---------------------------------------------- */
    var burger = document.getElementById('navBurger');
    var menu = document.getElementById('navMenu');
    if (burger && menu) {
        burger.addEventListener('click', function () {
            var open = menu.classList.toggle('is-open');
            burger.setAttribute('aria-expanded', String(open));
            burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        });

        document.addEventListener('click', function (e) {
            if (!menu.contains(e.target) && !burger.contains(e.target)) {
                menu.classList.remove('is-open');
                burger.setAttribute('aria-expanded', 'false');
            }
        });
    }

    /* --- Header border on scroll ---------------------------------------- */
    var header = document.getElementById('siteHeader');
    if (header) {
        var onScroll = function () {
            header.classList.toggle('is-scrolled', window.scrollY > 4);
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    /* --- Scroll reveal (replaces the AOS CDN dependency) ----------------- */
    var revealables = document.querySelectorAll('[data-reveal]');
    if (!revealables.length) return;

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || !('IntersectionObserver' in window)) {
        revealables.forEach(function (el) { el.classList.add('is-visible'); });
        return;
    }

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { rootMargin: '0px 0px -40px 0px', threshold: 0.05 });

    revealables.forEach(function (el) { observer.observe(el); });
})();
