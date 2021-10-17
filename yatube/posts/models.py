from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields.related import ForeignKey

User = get_user_model()


class Group(models.Model):
    """Модель хранит в себе название группы, относительную ссылку на группу
    и описание группы."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True, verbose_name='URL')
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель хранит в себе посты. Текст поста, дата публикации,
    автора и группу в который был написан пост."""
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Модель хранит в себе комментарии к постам. Пост для которого был
    написан комментарий, автор комментария текст и дату публикации."""
    post = ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Напишите свой комментарий',
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )


class Follow(models.Model):
    """Модель хранит в себе подписки на авторов. Пользователя который
    подписался и пользователя на которого подписались."""
    user = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        UniqueConstraint(fields=['user', 'author'], name='unique_subscription')
