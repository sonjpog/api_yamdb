import csv

from django.core.management import BaseCommand

from reviews.constants import DATA_PATH
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
    """
    Команда для загрузки данных из CSV файлов в базу данных.

    Данные связываются с моделями, указанными в словаре TABLES.
    """

    def handle(self, *args, **kwargs):
        """Обработка загрузки данных и их связей."""

        created_objects = {}

        for model, csv_f in TABLES.items():
            with open(
                f'{DATA_PATH}/{csv_f}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                objects = []
                for data in reader:
                    if model == Title:
                        title = Title(**data)
                        objects.append(title)
                    elif model == Genre:
                        genre = Genre(**data)
                        objects.append(genre)
                    else:
                        objects.append(model(**data))

                created_objects[model] = model.objects.bulk_create(objects)

        for title in created_objects[Title]:
            genres_for_title = data.get('genres', '').split(',')
            for genre_name in genres_for_title:
                genre = Genre.objects.get(name=genre_name.strip())
                title.genre.add(genre)

        self.stdout.write(self.style.SUCCESS('Все данные загружены'))
