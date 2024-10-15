from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from . import constants, validators

ROLES = [
    ('user', 'User'),
    ('moderator', 'Moderator'),
    ('admin', 'Admin')
]


class User(AbstractUser):
    """Модель пользователя."""
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    role = models.CharField(max_length=constants.MAX_NAME_LENGHT,
                            choices=ROLES, default='user')
    bio = models.TextField(constants.MAX_FIELD_LENGTH, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Genre(models.Model):
    """Модель для Жанров."""
    name = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=constants.MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='URL-идентификатор'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель для Категорий (типов) произведений."""

    name = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=constants.MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='URL-идентификатор'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для Произведений."""

    name = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Название',
        help_text='Введите название произведения'
    )

    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        help_text='Год выхода произведения',
        validators=[validators.validate_year]
    )

    genre = models.ManyToManyField(
        'Genre',
        related_name='titles',
        verbose_name='Жанр',
        help_text='Выберите жанры для произведения'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения',
        help_text='Введите описание произведения (необязательно)'
    )

    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='Категория',
        help_text='Выберите категорию для произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(constants.MIN_VALUE_VALIDATOR),
            MaxValueValidator(constants.MAX_VALUE_VALIDATOR)
        ],
        verbose_name='Оценка',
        help_text=(
            'Введите число от {min_value} до {max_value}, где {min_value} - '
            'минимально допустимое значение, {max_value} - максимально '
            'допустимое значение.'.format(
                min_value=constants.MIN_VALUE_VALIDATOR,
                max_value=constants.MAX_VALUE_VALIDATOR)
        )
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review_per_title_for_user'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return (
            f'Привет, {self.author}!\n'
            f'Вы оставили отзыв на произведение {self.title}.'
        )


class Comment(models.Model):
    """Модель для Комментариев."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:20]
