from django.test import TestCase


class MetricsTests(TestCase):
    def test_metrics_endpoint_exposes_prometheus_data(self):
        resp = self.client.get("/metrics")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "django_http_requests_total_by_method")