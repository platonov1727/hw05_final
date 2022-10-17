import datetime as dt

from django import forms
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User

POST_PER_PAGE = 10


class PostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Les')
        cls.user2 = User.objects.create_user(username='RandomUser')
        cls.user3 = User.objects.create_user(username='RandomUser2')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group2 = Group.objects.create(title='Вторая тест группа',
                                          description='Второе описание группы',
                                          slug='second-test-slug')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание тестовой группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(text='Тестовый текст',
                                       pub_date=dt.datetime.now(),
                                       author=cls.user,
                                       group=cls.group)
        cls.comment = Comment.objects.create(post=cls.post,
                                             author=cls.user2,
                                             text='Отписка')
        cls.comment2 = Comment.objects.create(post=cls.post,
                                              author=cls.user,
                                              text='Лайк')
        cls.follow = Follow.objects.create(user=cls.user2, author=cls.user)

    def setUp(self):
        cache.clear()

    def test_pages_uses_correct_templates(self):
        """URL исплоьзует соответствующий шаблон."""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
                'posts/create.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
                'posts/post_detail.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }

        for reverse_name, template in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_for_post_is_correct(self):
        """Шаблон постов сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        index_group = first_object.group
        index_text = first_object.text
        index_author = first_object.author
        self.assertEqual(index_text, 'Тестовый текст')
        self.assertEqual(str(index_group), (self.group.title))
        self.assertEqual(index_author.username, self.user.username)

    def test_context_for_index_is_correct(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        objects = response.context
        index_title = objects['title']
        index_text = objects['text']
        index_post = objects['page_obj'][0].text
        self.assertEqual(index_title, 'Это главная страница проекта Yatube.')
        self.assertEqual(index_text, 'Последние обновления на сайте')
        self.assertEqual(index_post, 'Тестовый текст')

    def test_context_for_group_list_is_correct(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        objects = response.context
        group_title = objects['title']
        group_group = objects['group']
        group_post = objects['page_obj'][0].text
        self.assertEqual(group_group, self.group, 'Ошибка группы')
        self.assertEqual(group_title, 'Записи сообщества', 'Ошибка')
        self.assertEqual(group_post, 'Тестовый текст')

    def test_context_for_profile_is_correct(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        objects = response.context
        profile_title = objects['title']
        profile_username = objects['author']
        self.assertEqual(profile_title, 'Профайл пользователя')
        self.assertEqual(profile_username.username, self.user.username)

    def test_context_for_post_detail_is_correct(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        objects = response.context
        detail_post = objects['post']
        comment = objects['comments'][0]
        comment2 = objects['comments'][1]
        self.assertEqual(detail_post.text, 'Тестовый текст')
        self.assertEqual(comment, self.comment)
        self.assertEqual(comment2, self.comment2)

    def test_context_for_create_post_is_correct(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for key, expected in form_fields.items():
            with self.subTest(key=key):
                form_field = response.context['form'].fields[key]
                self.assertIsInstance(form_field, expected)

    def test_context_for_post_edit_is_correct(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for key, expected in form_fields.items():
            with self.subTest(key=key):
                form_field = response.context['form'].fields[key]
                self.assertIsInstance(form_field, expected)

    def test_paginator_context_is_correct(self):
        """Шаблоны index, group_list и profile
        сформированные с правильным контекстом
        """
        paginator_objects = []
        for i in range(1, 11):
            posts_for_pagination = Post(author=self.user,
                                        text='Тестовый текст ' + str(i),
                                        group=self.group)
            paginator_objects.append(posts_for_pagination)
        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index':
                reverse('posts:index'),
            'group':
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'profile':
                reverse('posts:profile',
                        kwargs={'username': self.user.username})
        }
        for pagination, page in paginator_data.items():
            with self.subTest(pagination=pagination):
                response_page = self.authorized_client.get(page)
                response_page_1 = self.authorized_client.get(page + '?page=2')
                self.assertEqual(len(response_page.context['page_obj']), 10)
                self.assertEqual(len(response_page_1.context['page_obj']), 1)

    def test_cache_index(self):
        """Проверка кэширования постов"""
        test_post = Post.objects.create(text='some text',
                                        author=self.user,
                                        group=self.group)
        count_posts = Post.objects.count()
        self.authorized_client.get(reverse('posts:index'))
        test_post.delete()
        self.assertEqual(count_posts, 2)
        cache.clear()
        count_posts = Post.objects.count()
        self.assertEqual(count_posts, 1)

    def test_follow_another_user(self):
        """Follow на другого пользователя работает корректно"""
        self.authorized_client.get(
            reverse("posts:profile_follow", kwargs={"username": self.user2}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user2).exists()
        self.assertEqual(True, follow_exist)

    # #
    def test_unfollow_another_user(self):
        """Unfollow от другого пользователя работает корректно"""
        self.authorized_client.get(
            reverse("posts:profile_follow", kwargs={"username": self.user2}))
        self.authorized_client.get(
            reverse("posts:profile_unfollow", kwargs={"username": self.user2}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user2).exists()
        self.assertEqual(False, follow_exist)

    def test_post_follow_index_correct_context(self):
        """Follow index сформирован с правильным контекстом"""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user2}))
        follow_exist = Follow.objects.filter(user=self.user2,
                                             author=self.user).exists()
        self.assertEqual(True, follow_exist)

        test_post = Post.objects.create(text='Test text for follow',
                                        author=self.user2)
        expected = test_post.text
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_post = response.context['page_obj'].object_list[0]
        self.assertEqual(first_post.text, expected)

        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user2}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user2).exists()
        self.assertEqual(False, follow_exist)

        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertFalse(len(response.context.get('page_obj').object_list))
