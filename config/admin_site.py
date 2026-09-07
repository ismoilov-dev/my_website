"""The admin site this project actually mounts.

Django's stock ``AdminSite`` lists apps alphabetically and opens on a bare list
of model names, which says nothing about what each one controls on the public
site. This subclass fixes both problems:

* the sidebar follows the order of the site's own navigation, so "Blog" sits
  where a person looks for it instead of after "Certificates";
* the landing page is a dashboard -- traffic figures, how much of each kind of
  content exists, and one-click shortcuts to the pages that get edited most.

It is installed through ``config.apps.PortfolioAdminConfig`` so that every
existing ``@admin.register`` call keeps working unchanged.
"""

from django.contrib.admin import AdminSite
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

# Sidebar order. Anything not listed keeps Django's alphabetical order and is
# appended, so adding a new app never makes the sidebar disappear.
APP_ORDER = ['blog', 'analytics', 'auth']

MODEL_ORDER = {
    'blog': [
        'Blog',
        'FeedPost',
        'FeedComment',
        'Talk',
        'WorkExperience',
        'Project',
        'Education',
        'Certificate',
        'VoluntaryActivity',
    ],
    'analytics': ['PageView', 'UniqueVisitor', 'VisitorLog'],
}

# The dashboard's "Your content" cards. Each row names a model, the words to
# put on the card, and the public page that model feeds -- the mapping that is
# otherwise only in the developer's head.
CONTENT_CARDS = [
    ('blog', 'blog', 'Blog posts', 'Articles shown on /blogs/'),
    ('blog', 'feedpost', 'Feed posts', 'Short life updates on /feed/'),
    ('blog', 'talk', 'Talks', 'Talk videos on /talks/'),
    ('blog', 'project', 'Projects', 'Projects section of /cv/'),
    ('blog', 'workexperience', 'Work experience', 'Experience section of /cv/'),
    ('blog', 'certificate', 'Certificates', 'Certificates section of /cv/'),
]

# The four buttons at the top of the dashboard: the things added most often.
QUICK_ACTIONS = [
    ('blog', 'blog', 'Write a blog post', 'A full article with a cover image'),
    ('blog', 'feedpost', 'Post a feed update', 'A short note, photo or video'),
    ('blog', 'talk', 'Add a talk', 'Upload a talk recording'),
    ('blog', 'project', 'Add a CV project', 'A new entry on your CV page'),
]


def _admin_url(name, *args):
    """Reverse an admin route, or return None when the model is not registered."""
    try:
        return reverse(name, args=args)
    except NoReverseMatch:
        return None


class PortfolioAdminSite(AdminSite):
    site_header = 'Ismat — site control panel'
    site_title = 'Ismat admin'
    index_title = 'Dashboard'
    # Shown on the "no permission" / logged-out pages and in the header link.
    site_url = '/'
    enable_nav_sidebar = True

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)

        def app_key(app):
            label = app.get('app_label', '')
            return (APP_ORDER.index(label) if label in APP_ORDER else len(APP_ORDER), app['name'])

        for app in app_list:
            order = MODEL_ORDER.get(app.get('app_label'), [])
            app['models'].sort(
                key=lambda model: (
                    order.index(model['object_name'])
                    if model['object_name'] in order
                    else len(order),
                    model['name'],
                )
            )

        app_list.sort(key=app_key)
        return app_list

    def index(self, request, extra_context=None):
        """Traffic, content counts and shortcuts, instead of a list of models."""
        # Imported here rather than at module scope: this module is loaded while
        # the app registry is still being populated.
        from django.apps import apps

        from analytics.models import PageView, UniqueVisitor

        today = timezone.localdate()
        week_start = today - timezone.timedelta(days=6)
        today_start = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time())
        )

        daily_counts = {
            row['date']: row['visitors']
            for row in UniqueVisitor.objects.filter(date__gte=week_start)
            .values('date')
            .annotate(visitors=Count('id'))
        }
        raw_days = [
            (week_start + timezone.timedelta(days=offset),
             daily_counts.get(week_start + timezone.timedelta(days=offset), 0))
            for offset in range(7)
        ]
        busiest = max((visitors for _, visitors in raw_days), default=0)
        daily_visitors = [
            {
                'date': date,
                'visitors': visitors,
                # A day with no visitors still gets a visible stub bar.
                'height': round(visitors / busiest * 100) if busiest else 0,
                'is_today': date == today,
            }
            for date, visitors in raw_days
        ]

        content_cards = []
        for app_label, model_name, label, hint in CONTENT_CARDS:
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                continue
            content_cards.append({
                'label': label,
                'hint': hint,
                'count': model._default_manager.count(),
                'add_url': _admin_url(f'admin:{app_label}_{model_name}_add'),
                'list_url': _admin_url(f'admin:{app_label}_{model_name}_changelist'),
            })

        quick_actions = [
            {
                'label': label,
                'hint': hint,
                'url': _admin_url(f'admin:{app_label}_{model_name}_add'),
            }
            for app_label, model_name, label, hint in QUICK_ACTIONS
        ]
        quick_actions = [action for action in quick_actions if action['url']]

        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
            'app_list': self.get_app_list(request),
            'today': today,
            'today_unique_visitors': daily_counts.get(today, 0),
            'today_page_views': PageView.objects.filter(timestamp__gte=today_start).count(),
            'seven_day_unique_visitors': sum(day['visitors'] for day in daily_visitors),
            'seven_day_page_views': PageView.objects.filter(
                timestamp__date__gte=week_start
            ).count(),
            'daily_visitors': daily_visitors,
            'top_pages': list(
                PageView.objects.filter(timestamp__date__gte=week_start)
                .values('path')
                .annotate(views=Count('id'))
                .order_by('-views', 'path')[:6]
            ),
            'content_cards': content_cards,
            'quick_actions': quick_actions,
            **(extra_context or {}),
        }
        request.current_app = self.name
        return TemplateResponse(request, 'analytics/admin/dashboard.html', context)
