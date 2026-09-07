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
       is only a trigger whose [data-reveal-item] descendants belong together.
       Add [data-reveal-now] to a group that is already on screen at load --
       the hero, a page banner -- so it plays immediately instead of waiting
       for a scroll that may never happen.

       Everything else is watched element by element rather than group by
       group, which is the whole point: a group is often taller than the
       window, and revealing all of it the moment its top edge appears spends
       the animation on cards the reader cannot see yet, leaving the rest of
       the page static as they scroll into it. Watching each element means a
       post row, a card or a CV entry animates when it -- not its container --
       arrives.

       Elements that arrive together still come in one after another: the
       observer hands over everything that crossed the line in the same frame,
       and those are ordered top to bottom and offset by STAGGER_MS. So a grid
       that scrolls into view as a block cascades, while a single card further
       down simply plays on its own.

       Either attribute may name an effect -- data-reveal="fade-left",
       data-reveal-item="zoom-in" -- using the same vocabulary as the AOS
       library. The names are the stylesheet's business, not this file's: it
       never reads them, so a new effect is a CSS rule and nothing here.

       The offsets are written to custom properties rather than to
       `transition-delay` directly, so the stylesheet keeps ownership of the
       timing and this only decides the order. data-reveal-delay and
       data-reveal-duration (milliseconds) override it per element. */

    var STAGGER_MS = 110;

    /* A cascade is a flourish, not a queue. Offsets stop growing once the
       batch has been arriving for this long, so a twentieth card is not still
       waiting seconds after the first one moved. It is a ceiling in time
       rather than a count of elements, because what makes a cascade drag is
       how long the tail waits, not how many are in it -- ten hero pieces at
       110ms apart are a flourish, and thirty would not be. */
    var STAGGER_CEILING_MS = 1100;

    var LOAD_DELAY_MS = 300;

    /* Matches the 0.85s default in the stylesheet. */
    var DURATION_MS = 850;

    /* Milliseconds from an attribute, ignoring anything that is not a
       positive number: a typo in a template should cost an element its
       override, not its entrance. */
    var msAttr = function (el, name) {
        var value = parseInt(el.getAttribute(name), 10);
        return isFinite(value) && value > 0 ? value : 0;
    };

    var pending = [];   /* waiting for the reader to scroll to them */
    var onLoad = [];    /* on screen already, played as soon as we start */

    Array.prototype.forEach.call(
        document.querySelectorAll('[data-reveal], [data-reveal-group]'),
        function (el) {
            var targets = el.hasAttribute('data-reveal-group')
                ? Array.prototype.slice.call(el.querySelectorAll('[data-reveal-item]'))
                : [el];
            var bucket = el.hasAttribute('data-reveal-now') ? onLoad : pending;
            Array.prototype.push.apply(bucket, targets);
        }
    );

    if (!pending.length && !onLoad.length) return;

    /* Nothing to undo when motion is unwanted or unobservable: the hidden
       state is CSS-only and the elements simply stay as they are. */
    if (reduced || !('IntersectionObserver' in window)) return;

    /* One batch: ordered, offset, and cleaned up after itself. */
    var revealBatch = function (batch, baseDelay) {
        batch.forEach(function (el, index) {
            var delay = baseDelay +
                Math.min(index * STAGGER_MS, STAGGER_CEILING_MS) +
                msAttr(el, 'data-reveal-delay');
            var duration = msAttr(el, 'data-reveal-duration');

            el.style.setProperty('--reveal-delay', delay + 'ms');
            if (duration) el.style.setProperty('--reveal-duration', duration + 'ms');
            el.classList.add('is-revealed');

            /* Once the entrance has played, retire the markup that drove it.
               The reveal rule sets `transition` and `transition-delay` and
               outranks the components' own rules, so leaving it in place would
               mute every later hover transition on these elements and hold it
               back by the stagger offset. Dropping the attribute restores each
               element to its own styles, and costs nothing visually because it
               is already at its resting state. */
            window.setTimeout(function () {
                el.style.removeProperty('--reveal-delay');
                el.style.removeProperty('--reveal-duration');
                el.classList.remove('is-revealed');
                el.removeAttribute('data-reveal');
                el.removeAttribute('data-reveal-item');
            }, delay + (duration || DURATION_MS) + 100);
        });
    };

    var topToBottom = function (a, b) {
        var ra = a.getBoundingClientRect();
        var rb = b.getBoundingClientRect();
        return (ra.top - rb.top) || (ra.left - rb.left);
    };

    var observer = new IntersectionObserver(function (entries) {
        var arrived = [];

        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            observer.unobserve(entry.target);
            arrived.push(entry.target);
        });

        if (!arrived.length) return;

        /* Reading order, not observer order: entries come back in whatever
           order the browser noticed them, and a cascade that runs bottom-up
           reads as a glitch. */
        arrived.sort(topToBottom);
        revealBatch(arrived, 0);
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0 });

    pending.forEach(function (el) { observer.observe(el); });
    revealBatch(onLoad, LOAD_DELAY_MS);

    /* Safety net. The hidden state lives in CSS, so anything the observer
       fails to reach would stay invisible for good -- an unacceptable way for
       an article to disappear. A short while after load, force in anything
       that has reached the viewport and is still waiting. Elements further
       down the page are untouched, so genuine scroll reveals still play. */
    window.setTimeout(function () {
        var stuck = pending.filter(function (el) {
            return el.isConnected &&
                !el.classList.contains('is-revealed') &&
                (el.hasAttribute('data-reveal') || el.hasAttribute('data-reveal-item')) &&
                el.getBoundingClientRect().top < window.innerHeight;
        });

        stuck.forEach(function (el) { observer.unobserve(el); });
        revealBatch(stuck.sort(topToBottom), 0);
    }, 4000);
})();
