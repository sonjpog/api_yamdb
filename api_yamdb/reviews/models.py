from django.db import models

from . import constants, validators


class UserPlaceholder(models.Model):
    username = models.CharField(max_length=255)

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
        through='GenreTitle',
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
    text = models.TextField()
    author = models.ForeignKey(
        UserPlaceholder,  # Заглушка для CustomUser
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField()
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
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
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        UserPlaceholder,
        on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:20]
