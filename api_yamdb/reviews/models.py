from django.db import models


class UserPlaceholder(models.Model):
    username = models.CharField(max_length=255)

    def __str__(self):
        return self.username


class Review(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        'UserPlaceholder',  # Заглушка для CustomUser
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
