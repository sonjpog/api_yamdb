from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from . import constants, validators


class User(AbstractUser):
    """Модель пользователя."""

    confirmation_code = models.CharField(max_length=constants.MAX_CODE_LENGHT,
                                         blank=True, null=True)
    role = models.CharField(
        max_length=constants.MAX_NAME_LENGHT,
        choices=[(constants.ADMIN, 'Admin'),
                 (constants.MODERATOR, 'Moderator'),
                 (constants.USER, 'User')],
        default=constants.USER
    )
    bio = models.TextField(blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=constants.MAX_NAME_LENGHT,
        unique=True,
        validators=[validators.validate_username],
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == constants.ADMIN
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == constants.MODERATOR


class BaseModel(models.Model):
    """Абстрактная модель для жанров и категорий."""

    name = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=constants.MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='URL-идентификатор'
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(BaseModel):
    """Модель для Жанров."""

    class Meta(BaseModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(BaseModel):
    """Модель для Категорий (типов) произведений."""

    class Meta(BaseModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Модель для Произведений."""

    name = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Название',
        help_text='Введите название произведения'
    )

    year = models.SmallIntegerField(
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


class BaseContent(models.Model):
    """Абстрактная модель для общего содержимого."""

    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['pub_date']

    def __str__(self):
        return self.text[:constants.MAX_NAME_LENGHT]


class Review(BaseContent):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
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


class Comment(BaseContent):
    """Модель для Комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
