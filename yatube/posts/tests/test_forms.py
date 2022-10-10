import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    """Проверка форм"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Les")
        cls.group = Group.objects.create(title="Тестовый тайтл",
                                         slug="test-slug",
                                         description="Тестовое описание")
        cls.group_second = Group.objects.create(title="Тестовый тайтл2",
                                                slug="test-slug2",
                                                description="test desc2")
        cls.post = Post.objects.create(author=cls.user,
                                       text="Тестовый текст",
                                       group=cls.group)
        cls.form = PostForm()
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиента авторизованного и неавторизованного"""
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """Валидная форма создает запись в базе Post"""
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(name='small.gif',
                                      content=small_gif,
                                      content_type='image/gif')

        posts_count = Post.objects.count()
        form_data = {
            'text': "Новый пост",
            'group': self.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(reverse("posts:post_create"),
                                               data=form_data)
        post = Post.objects.first()
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists())

    def test_create_post_form_status_code(self):
        """Проверка статус кодов для формы поста"""
        post_url = {
            HTTPStatus.OK: reverse("posts:post_create"),
            HTTPStatus.OK: reverse("posts:post_edit", kwargs={"post_id": 1}),
        }

        for status, urls in post_url.items():
            with self.subTest(urls=urls):
                response = self.authorized_client.get(urls)
                self.assertEqual(response.status_code, status)

    def test_edit_post_form(self):
        """Валидная форма редактирует запись в Post"""
        form_data = {
            "text": "Новый пост 1",
            "group": self.group.pk,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}))
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(self.post.group.pk, form_data["group"])

    def test_guest_users_forms(self):
        """Тест неавторизованных пользователей"""
        test_urls = {
            HTTPStatus.FOUND: reverse("posts:post_create"),
            HTTPStatus.FOUND: reverse("posts:post_edit", kwargs={"post_id":
                                                                     1}),
        }

        for status, urls in test_urls.items():
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, status)

    def test_not_authorized_user_posted(self):
        """Тест неавторизованных пользователей"""
        form_data = {
            "text": "Новый пост",
            "group": self.group.pk,
        }
        self.guest_client.post(reverse("posts:post_create"), data=form_data)
        self.assertEqual(Post.objects.count(), 1)

    def test_authorized_comments(self):
        """Валидная форма сохраняет коммент в БД"""
        comments_count = Comment.objects.count()
        comment_data = {'text': 'test text'}
        self.authorized_client.post(reverse('posts:add_comment',
                                            kwargs={'post_id': self.post.id}),
                                    data=comment_data)
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, 'test text')

    def test_guest_comment(self):
        """Тест неавторизованный пользователь не может оставить коммент"""
        comments_count = Comment.objects.count()
        comment_data = {'text': 'Im not authorized'}
        self.guest_client.post(reverse('posts:add_comment',
                                       kwargs={'post_id': self.post.id}),
                               data=comment_data)
        self.assertEqual(comments_count, 0)
