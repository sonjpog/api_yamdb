from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)


class Titles(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles'
    )
    genres = models.ManyToManyField(
        Genre, related_name='titles')

    def __str__(self):
        return self.name
