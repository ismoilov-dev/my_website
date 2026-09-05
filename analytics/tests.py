from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import PageView, UniqueVisitor


class VisitorTrackingTests(TestCase):
    def test_public_request_creates_pageview_and_daily_unique_visitor(self):
        self.client.get('/', REMOTE_ADDR='203.0.113.1', HTTP_USER_AGENT='Browser')
        self.client.get('/', REMOTE_ADDR='203.0.113.1', HTTP_USER_AGENT='Browser')

        self.assertEqual(PageView.objects.filter(path='/').count(), 2)
        self.assertEqual(UniqueVisitor.objects.count(), 1)
        self.assertEqual(UniqueVisitor.objects.get().date, timezone.localdate())

    def test_admin_static_and_bots_are_not_tracked(self):
        self.client.get('/ismatismoilov709/login/', REMOTE_ADDR='203.0.113.2')
        self.client.get('/static/css/main.css', REMOTE_ADDR='203.0.113.2')
        self.client.get('/', REMOTE_ADDR='203.0.113.2', HTTP_USER_AGENT='Googlebot')

        self.assertFalse(PageView.objects.exists())

    def test_dashboard_is_shown_on_admin_home(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.force_login(user)

        response = self.client.get('/ismatismoilov709/')

        self.assertContains(response, 'Website traffic')
