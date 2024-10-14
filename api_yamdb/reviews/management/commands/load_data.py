import csv

from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User

TABLES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Словарь для хранения объектов
        created_objects = {}

        for model, csv_f in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{csv_f}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                objects = []
                for data in reader:
                    if model == Title:
                        # Создание объекта Title
                        title = Title(**data)
                        objects.append(title)

                    elif model == Genre:
                        # Создание объекта Genre
                        genre = Genre(**data)
                        objects.append(genre)

                    else:
                        # Для остальных моделей
                        objects.append(model(**data))

                # Массовое создание объектов
                created_objects[model] = model.objects.bulk_create(objects)

        # Связываем жанры с произведениями
        for title in created_objects[Title]:
            # Получаем жанры для текущего произведения
            # Предполагаем, что в заголовке есть поле 'genres'
            genres_for_title = data.get('genres', '').split(',')
            for genre_name in genres_for_title:
                # Получаем жанр по имени
                genre = Genre.objects.get(name=genre_name.strip())
                title.genre.add(genre)  # Добавляем жанр в поле ManyToMany

        self.stdout.write(self.style.SUCCESS('Все данные загружены'))
