import datetime as dt
from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(title='Тестовый заголовок',
                                         slug='test-slug',
                                         description='Тестовое описание')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            pub_date=dt.datetime.now(),
        )
        cache.clear()

    def test_urls_exist_at_desired_locations(self):
        """Проверка доступности адресов для всех пользователей"""
        test_codes_urls = {
            HTTPStatus.OK:
            reverse('posts:index'),
            HTTPStatus.OK:
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            HTTPStatus.OK:
            reverse('about:author'),
            HTTPStatus.OK:
            reverse('about:tech'),
            HTTPStatus.OK:
            reverse('posts:profile', kwargs={'username': self.user.username}),
            HTTPStatus.OK:
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            HTTPStatus.NOT_FOUND:
            '/unexisting-page/'
        }

        for codes, adresses in test_codes_urls.items():
            with self.subTest(addresses=adresses):
                response = self.guest_client.get(adresses)
                self.assertEqual(response.status_code, codes)

    def test_urls_exist_at_desired_locations_authorized_users(self):
        """Проверка страниц доступных авторизованнымользователям"""
        test_codes_urls = {
            HTTPStatus.OK: reverse('posts:post_edit', kwargs={'post_id':self.post.id}),
            HTTPStatus.OK: reverse('posts:post_create'),
        }

        for codes, adresses in test_codes_urls.items():
            with self.subTest(adresses=adresses):
                response = self.authorized_client.get(adresses)
                self.assertEqual(response.status_code, codes)

    def test_urls_use_correct_templates(self):
        """Проверка правильности ипользования шаблонов адресами"""

        test_templates_urls = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create.html',
            '/create/': 'posts/create.html'
        }

        for urls, templates in test_templates_urls.items():
            with self.subTest(templates=templates):
                response = self.authorized_client.get(urls)
                self.assertTemplateUsed(response, templates, 'NOT OKAY')
