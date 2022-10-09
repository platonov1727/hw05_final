from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_url_uses_correct_templates(self):
        """Проверка правильности шаблонов about"""
        test_url_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

        for urls, templates in test_url_templates.items():
            with self.subTest(templates=templates):
                response = self.guest_client.get(urls)
                self.assertTemplateUsed(response, templates)
