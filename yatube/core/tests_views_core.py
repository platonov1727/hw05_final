from django.test import TestCase


class PageNotFoundTest(TestCase):
    def test_error_page(self):
        response = self.client.get('/noneexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
