from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

MAX_LENGHT_OF_POST_STR = 15


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    theme = models.CharField(max_length=50,
                             help_text='Тема поста',
                             verbose_name='Тема поста',
                             blank=True,
                             default='')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',
                                    help_text='Дата публикации поста',
                                    db_index=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост')
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f'Post{self.text[:MAX_LENGHT_OF_POST_STR]}'


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Заголовок',
                             help_text='Название группы')
    slug = models.SlugField(verbose_name='адрес страниц',
                            unique=True,
                            help_text='Адрес страницы группы')
    description = models.TextField(verbose_name='Описание группы',
                                   help_text='Описание группы')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Comment(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор")
    text = models.TextField(verbose_name="Коментарии",
                            help_text="Оставте комментарий")
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="comments",
                             null=True,
                             blank=True)
    created = models.DateTimeField(verbose_name="Дата публикации",
                                   auto_now_add=True)

    def __str__(self):
        return self.text[:MAX_LENGHT_OF_POST_STR]

    class Meta:
        ordering = ('created',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Подписки',
                             related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               verbose_name='На кого подписываются',
                               related_name='following',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.user

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
