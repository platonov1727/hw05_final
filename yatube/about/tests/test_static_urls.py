from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_url_exist_at_disired_loaction(self):
        """Проверка доступности адреса /about/author"""
        test_url = {
            HTTPStatus.OK: reverse('about:tech'),
            HTTPStatus.OK: reverse('about:tech')
        }

        for codes, urls in test_url.items():
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, codes)
