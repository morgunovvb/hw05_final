from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AbstractModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        # Это абстрактная модель:
        abstract = True


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(AbstractModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True, null=True,
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Comment(AbstractModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )
    text = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=[
                'post',
                'author'],
                name='unique_together'),
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Автор',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    def __str__(self):
        return self.user
