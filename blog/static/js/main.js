/* ismat.dev — shared behaviour: mobile nav, scroll reveal. */
(function () {
    'use strict';

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
