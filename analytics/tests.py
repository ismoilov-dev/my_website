from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import PageView, UniqueVisitor

ADMIN = '/ismatismoilov709/'


class VisitorTrackingTests(TestCase):
    def test_public_request_creates_pageview_and_daily_unique_visitor(self):
        self.client.get('/', REMOTE_ADDR='203.0.113.1', HTTP_USER_AGENT='Browser')
        self.client.get('/', REMOTE_ADDR='203.0.113.1', HTTP_USER_AGENT='Browser')

        self.assertEqual(PageView.objects.filter(path='/').count(), 2)
        self.assertEqual(UniqueVisitor.objects.count(), 1)
        self.assertEqual(UniqueVisitor.objects.get().date, timezone.localdate())

    def test_admin_static_and_bots_are_not_tracked(self):
        self.client.get(ADMIN + 'login/', REMOTE_ADDR='203.0.113.2')
        self.client.get('/static/css/main.css', REMOTE_ADDR='203.0.113.2')
        self.client.get('/', REMOTE_ADDR='203.0.113.2', HTTP_USER_AGENT='Googlebot')

        self.assertFalse(PageView.objects.exists())


class DashboardTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser(
            'admin', 'admin@example.com', 'password'
        )
        self.client.force_login(user)

    def test_admin_home_shows_the_dashboard(self):
        response = self.client.get(ADMIN)

        self.assertContains(response, 'dash-welcome')
        self.assertContains(response, 'Visitors today')
        self.assertContains(response, 'Your content')

    def test_dashboard_counts_todays_traffic(self):
        PageView.objects.create(path='/', ip_address='203.0.113.9')
        PageView.objects.create(path='/blogs/', ip_address='203.0.113.9')
        UniqueVisitor.objects.create(ip_address='203.0.113.9')

        context = self.client.get(ADMIN).context

        self.assertEqual(context['today_page_views'], 2)
        self.assertEqual(context['today_unique_visitors'], 1)
        self.assertEqual(context['seven_day_unique_visitors'], 1)

    def test_dashboard_chart_always_covers_seven_days(self):
        """The chart must not collapse on quiet days, or it would read as broken."""
        days = self.client.get(ADMIN).context['daily_visitors']

        self.assertEqual(len(days), 7)
        self.assertTrue(days[-1]['is_today'])
        self.assertTrue(all(0 <= day['height'] <= 100 for day in days))

    def test_dashboard_lists_content_with_working_links(self):
        cards = self.client.get(ADMIN).context['content_cards']

        self.assertTrue(cards)
        for card in cards:
            self.assertTrue(card['add_url'], card['label'])
            self.assertTrue(card['list_url'], card['label'])

    def test_sidebar_puts_blog_before_analytics(self):
        app_list = self.client.get(ADMIN).context['app_list']

        labels = [app['app_label'] for app in app_list]
        self.assertLess(labels.index('blog'), labels.index('analytics'))

    def test_traffic_tables_are_read_only(self):
        for model in ('pageview', 'uniquevisitor', 'visitorlog'):
            with self.subTest(model=model):
                response = self.client.get(f'{ADMIN}analytics/{model}/add/')
                self.assertEqual(response.status_code, 403)
