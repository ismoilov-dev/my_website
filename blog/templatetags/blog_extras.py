import re

from django import template
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
