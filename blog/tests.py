from django.test import Client, TestCase
from django.urls import reverse


class HealthzTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_healthz_endpoint(self):
        response = self.client.get(reverse('healthz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})
