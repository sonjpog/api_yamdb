from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Genre, Review, Title, User

from reviews.models import User


class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'first_name',
                           'last_name', 'bio')}),
        ('Extra Fields', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'role', 'bio')

    list_editable = ('role',)


admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('review__title',)
    list_filter = ('review',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'score',
    )
    search_fields = ('pub_date',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category',
        'description',
        'get_genres',
    )
    search_fields = ('name',)
    list_filter = ('category',)
    list_editable = ('category',)
    empty_value_display = '-пусто-'

    def get_genres(self, obj):
        return ', '.join(genre.name for genre in obj.genres.all())
