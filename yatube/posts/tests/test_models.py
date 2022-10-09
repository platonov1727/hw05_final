from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def test_models_have_correct_name(self):
        """Тест модели имеют корректное имя"""
        test_post = PostModelTest.post
        expected_value_post = str(test_post.text)
        test_group = PostModelTest.group
        expected_value_group = str(test_group.title)
        self.assertEqual(expected_value_post,
                         test_post.text[:15], '__str__поломан')
        self.assertEqual(expected_value_group, test_group.title)

    def test_model_verbose_is_correct(self):
        """Проверяем, что у моделей присутствуют verbose_name"""
        verbose_field = PostModelTest.post
        field_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }

        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    verbose_field._meta.get_field(
                        field).verbose_name, expected_value)

    def test_model_help_text_is_correct(self):
        """Проверяем, что у моделей присутствуют help_text"""
        test_field = PostModelTest.post
        field_help = {
            'text': 'Введите текст поста',
            'pub_date': 'Дата публикации поста',
            'group': 'Группа, к которой будет относиться пост'
        }

        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    test_field._meta.get_field(field).help_text, expected_value
                )
