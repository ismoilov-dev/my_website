import json
import os
import re

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import ManifestFilesMixin, staticfiles_storage
from django.templatetags.static import static
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

# Admin text is written by hand, so a line may carry more than one marker
# (e.g. "* • Mentor Python students ..."). A lone "*" is a bullet, but "**" is
# the start of bold text, not a list.
BULLET_PREFIX = re.compile(r'^(?:[•\-–—]\s*|\*(?!\*)\s*)+')
HEADING_PREFIX = re.compile(r'^#{1,6}\s*')
BOLD = re.compile(r'\*\*(.+?)\*\*')


def _inline(text, escape):
    """Escape a line, then apply the one inline mark-up we support: **bold**."""
    return BOLD.sub(r'<strong>\1</strong>', escape(text))


@register.filter(needs_autoescape=True)
def bulletize(value, autoescape=True):
    """Render admin-entered CV text as clean HTML.

    Descriptions are free text: some are prose, some are bullet lists, and some
    carry leftover Markdown markers. Doing the conversion here keeps the markup
    correct and accessible, instead of letting JavaScript rewrite the DOM after
    the page has already painted.
    """
    if not value:
        return ''

    escape = conditional_escape if autoescape else str
    lines = [line.strip() for line in str(value).splitlines()]
    lines = [line for line in lines if line]

    html = []
    open_list = False

    for line in lines:
        if BULLET_PREFIX.match(line):
            if not open_list:
                html.append('<ul class="cv-bullets">')
                open_list = True
            html.append(f'<li>{_inline(BULLET_PREFIX.sub("", line), escape)}</li>')
            continue

        if open_list:
            html.append('</ul>')
            open_list = False

        heading = HEADING_PREFIX.match(line)
        text = _inline(HEADING_PREFIX.sub('', line), escape)
        html.append(f'<p><strong>{text}</strong></p>' if heading else f'<p>{text}</p>')

    if open_list:
        html.append('</ul>')

    return mark_safe(''.join(html))


def _json_ld(data):
    """Serialise a schema.org object for a <script type="application/ld+json">.

    The angle brackets and ampersand are escaped so no value can break out of
    the surrounding script element, the same precaution Django's json_script
    filter takes.
    """
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    for raw, escaped in (('<', '\\u003C'), ('>', '\\u003E'), ('&', '\\u0026')):
        payload = payload.replace(raw, escaped)
    return mark_safe(payload)


def _person_id(base_url):
    return f'{base_url}/#person'


@register.simple_tag
def static_v(path):
    """A static URL that changes whenever the file does.

    Django's dev server sends `Last-Modified` and no `Cache-Control`, which
    leaves the browser free to guess how long the file stays fresh -- Chrome
    guesses roughly a tenth of the file's age, so an asset last edited hours
    ago is reused for a long while without ever asking the server. Editing the
    stylesheet then changes nothing on screen until a hard refresh, which is a
    miserable way to develop and an easy way to conclude a feature is broken
    when it is only cached.

    Appending the file's modification time settles it: the URL is stable while
    the file is, and different the moment it is not, so the browser fetches
    exactly when it should.

    Production is left alone, because the manifest storage there already puts a
    content hash in the file name and does the job properly. Stamping those
    with an mtime as well would be worse than redundant: a deploy rewrites
    every file's timestamp, so unchanged assets would get a new URL on every
    release and lose the year-long caching the hash earns them.
    """
    if isinstance(staticfiles_storage, ManifestFilesMixin):
        return static(path)

    url = static(path)

    if '?' in url:
        return url

    source = finders.find(path)
    if not source:
        return url

    try:
        stamp = int(os.stat(source).st_mtime)
    except OSError:
        return url

    return f'{url}?v={stamp}'

@register.simple_tag(takes_context=True)
def site_schema(context):
    """Describe the site and its author to search engines.

    Structured data is what lets Google treat "Ismat Ismoilov" as a person
    rather than as two words on a page: sameAs links the site to the same
    identity as the GitHub, LinkedIn, Telegram and YouTube accounts, and
    alternateName covers the family-name-first spelling people also search for.
    """
    request = context['request']
    base = f'{request.scheme}://{request.get_host()}'

    person = {
        '@type': 'Person',
        '@id': _person_id(base),
        'name': settings.SITE_AUTHOR,
        'alternateName': settings.SITE_AUTHOR_ALTERNATES,
        'url': f'{base}/',
        'image': base + static('ismat.jpg'),
        'jobTitle': settings.SITE_JOB_TITLE,
        'knowsAbout': settings.SITE_EXPERTISE,
        'address': {'@type': 'PostalAddress', 'addressCountry': 'UZ'},
        'sameAs': [url for _, url in settings.SOCIAL_PROFILES],
    }
    website = {
        '@type': 'WebSite',
        '@id': f'{base}/#website',
        'url': f'{base}/',
        'name': settings.SITE_AUTHOR,
        'alternateName': settings.SITE_AUTHOR_ALTERNATES,
        'inLanguage': 'en',
        'publisher': {'@id': _person_id(base)},
    }
    return _json_ld({'@context': 'https://schema.org', '@graph': [person, website]})


@register.simple_tag(takes_context=True)
def article_schema(context, blog):
    """Mark a post up as a BlogPosting written by the site's author."""
    request = context['request']
    base = f'{request.scheme}://{request.get_host()}'

    schema_data = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'headline': blog.title,
        'description': blog.excerpt,
        'datePublished': blog.created_at.isoformat(),
        'dateModified': blog.updated_at.isoformat(),
        'mainEntityOfPage': base + blog.get_absolute_url(),
        'author': {'@id': _person_id(base)},
        'publisher': {'@id': _person_id(base)},
    }
    if blog.image:
        schema_data['image'] = base + blog.image.url

    return _json_ld(schema_data)

