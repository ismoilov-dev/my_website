/* ismat.dev — shared behaviour.
   Everything here is optional polish: each block checks for the elements it
   needs and does nothing when they are absent, so one file can serve every
   page without a per-page bundle. */
(function () {
    'use strict';

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* --- Mobile navigation ---------------------------------------------- */

    var burger = document.getElementById('navBurger');
    var menu = document.getElementById('navMenu');

    if (burger && menu) {
        var setMenu = function (open) {
            menu.classList.toggle('is-open', open);
            burger.setAttribute('aria-expanded', String(open));
            burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        };

        burger.addEventListener('click', function () {
            setMenu(!menu.classList.contains('is-open'));
        });

        document.addEventListener('click', function (e) {
            if (!menu.contains(e.target) && !burger.contains(e.target)) setMenu(false);
        });

        /* Escape closes the menu and puts focus back where it started, so a
           keyboard user is never left stranded inside a closed panel. */
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && menu.classList.contains('is-open')) {
                setMenu(false);
                burger.focus();
            }
        });
    }

    /* --- Scroll-driven chrome -------------------------------------------
       The header shadow, the back-to-top button and the article progress bar
       all answer the same question -- how far down the page are we -- so they
       share one rAF-throttled scroll listener. */

    var header = document.getElementById('siteHeader');
    var toTop = document.getElementById('toTop');
    var progress = document.querySelector('.reading-progress span');
    var article = document.querySelector('[data-progress-target]');

    if (header || toTop || progress) {
        var ticking = false;

        var onScroll = function () {
            var y = window.scrollY || document.documentElement.scrollTop;

            if (header) header.classList.toggle('is-stuck', y > 8);
            if (toTop) toTop.classList.toggle('is-visible', y > 600);

            if (progress && article) {
                /* Measure against the article itself rather than the whole
                   document: the footer and post navigation are not reading. */
                var start = article.offsetTop;
                var span = article.offsetHeight - window.innerHeight;
                var pct = span > 0 ? ((y - start) / span) * 100 : (y > start ? 100 : 0);
                progress.style.width = Math.max(0, Math.min(100, pct)) + '%';
            }

            ticking = false;
        };

        window.addEventListener('scroll', function () {
            if (ticking) return;
            ticking = true;
            window.requestAnimationFrame(onScroll);
        }, { passive: true });

        window.addEventListener('resize', onScroll, { passive: true });
        onScroll();
    }

    if (toTop) {
        toTop.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
        });
    }

    /* --- Blog search ----------------------------------------------------
       Filters the already-rendered list in place. The archive is small and
       fully in the DOM, so this is instant and works without a round trip;
       month and year headings hide themselves once they have no posts left. */

    var search = document.getElementById('postSearch');

    if (search) {
        var summary = document.getElementById('searchSummary');
        var rows = Array.prototype.slice.call(document.querySelectorAll('[data-post-title]'));
        var months = Array.prototype.slice.call(document.querySelectorAll('.month-group'));
        var years = Array.prototype.slice.call(document.querySelectorAll('.year-group'));
        var noResults = document.getElementById('searchEmpty');

        var filter = function () {
            var term = search.value.trim().toLowerCase();
            var shown = 0;

            rows.forEach(function (row) {
                var match = !term || row.dataset.postTitle.indexOf(term) !== -1;
                row.hidden = !match;
                if (match) shown++;
            });

            /* A group is empty when every row inside it is hidden. */
            var hideEmpty = function (group) {
                group.hidden = !group.querySelector('[data-post-title]:not([hidden])');
            };
            months.forEach(hideEmpty);
            years.forEach(hideEmpty);

            if (noResults) noResults.hidden = shown !== 0;

            if (summary) {
                summary.textContent = term
                    ? shown + (shown === 1 ? ' post matches ' : ' posts match ') + '"' + search.value.trim() + '"'
                    : '';
            }
        };

        search.addEventListener('input', filter);

        /* Escape clears the field the way a native search input would. */
        search.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && search.value) {
                search.value = '';
                filter();
            }
        });
    }

    /* --- Share ----------------------------------------------------------
       The native share sheet on phones, a clipboard copy everywhere else. */

    var shareBtn = document.getElementById('shareBtn');

    if (shareBtn) {
        shareBtn.addEventListener('click', function () {
            var url = window.location.href;
            var label = shareBtn.querySelector('.share-text');
            var original = label ? label.textContent : '';

            var confirmCopy = function () {
                if (!label) return;
                label.textContent = 'Link copied';
                shareBtn.classList.add('is-copied');
                window.setTimeout(function () {
                    label.textContent = original;
                    shareBtn.classList.remove('is-copied');
                }, 2000);
            };

            if (navigator.share) {
                navigator.share({ title: document.title, url: url }).catch(function () { });
                return;
            }

            if (navigator.clipboard) {
                navigator.clipboard.writeText(url).then(confirmCopy).catch(function () { });
            }
        });
    }

    /* --- Scroll reveal ---------------------------------------------------
       Staggered entrances in the style of azimjon.com. Two roles in the
       markup: [data-reveal] animates on its own, while [data-reveal-group]
       is only a trigger whose [data-reveal-item] descendants come in one
       after another. Add [data-reveal-now] to a group that is already on
       screen at load -- the hero -- so it plays immediately instead of
       waiting for a scroll that may never happen.

       The per-item offset is written to a custom property rather than to
       `transition-delay` directly, so the stylesheet keeps ownership of the
       timing and this only decides the order. */

    var STAGGER_MS = 110;
    var LOAD_DELAY_MS = 300;

    var groups = Array.prototype.slice.call(
        document.querySelectorAll('[data-reveal], [data-reveal-group]')
    );
    if (!groups.length) return;

    /* Nothing to undo when motion is unwanted or unobservable: the hidden
       state is CSS-only and the elements simply stay as they are. */
    if (reduced || !('IntersectionObserver' in window)) return;

    var targetsOf = function (group) {
        if (!group.hasAttribute('data-reveal-group')) return [group];
        return Array.prototype.slice.call(group.querySelectorAll('[data-reveal-item]'));
    };

    var prepare = function (group, extraDelay) {
        targetsOf(group).forEach(function (el, index) {
            el.style.setProperty('--reveal-delay', (extraDelay + index * STAGGER_MS) + 'ms');
        });
    };

    /* Matches the 0.85s in the stylesheet, plus a little slack. */
    var DURATION_MS = 850;

    var reveal = function (group) {
        var targets = targetsOf(group);
        if (!targets.length) return;

        targets.forEach(function (el) { el.classList.add('is-revealed'); });

        /* Once the entrance has played, retire the markup that drove it.
           The reveal rule sets `transition` and `transition-delay` and
           outranks the components' own rules, so leaving it in place would
           mute every later hover transition on these elements and hold it
           back by the stagger offset. Dropping the attribute restores each
           element to its own styles, and costs nothing visually because it
           is already at its resting state. */
        var last = targets[targets.length - 1];
        var spent = parseInt(last.style.getPropertyValue('--reveal-delay'), 10) || 0;

        window.setTimeout(function () {
            targets.forEach(function (el) {
                el.style.removeProperty('--reveal-delay');
                el.classList.remove('is-revealed');
                el.removeAttribute('data-reveal');
                el.removeAttribute('data-reveal-item');
            });
        }, spent + DURATION_MS + 100);
    };

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            reveal(entry.target);
            observer.unobserve(entry.target);
        });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

    groups.forEach(function (group) {
        var now = group.hasAttribute('data-reveal-now');
        prepare(group, now ? LOAD_DELAY_MS : 0);

        if (now) {
            reveal(group);
        } else {
            observer.observe(group);
        }
    });

    /* Safety net. The hidden state lives in CSS, so anything the observer
       fails to reach would stay invisible for good -- an unacceptable way for
       an article to disappear. A short while after load, force in anything
       that has reached the viewport but has not been revealed. Groups further
       down the page are untouched, so genuine scroll reveals still play. */
    window.setTimeout(function () {
        groups.forEach(function (group) {
            if (!group.isConnected) return;
            var pending = group.querySelector('[data-reveal-item]') ||
                (group.hasAttribute('data-reveal') ? group : null);
            if (!pending) return;
            if (group.getBoundingClientRect().top < window.innerHeight) {
                observer.unobserve(group);
                reveal(group);
            }
        });
    }, 4000);
})();
