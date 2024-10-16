from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.exceptions import NotFound


from reviews.models import Category, Comment, Genre, Review, Title
from reviews.constants import USERNAME_ME

from api_yamdb.settings import DEFAULT_FROM_EMAIL

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role')
        extra_kwargs = {'email': {'required': True}}

    def validate_username(self, value):
        if value == USERNAME_ME:
            raise serializers.ValidationError(
                f'Нельзя использовать "{USERNAME_ME}" в качестве username.'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Адрес электронной почты уже существует.'
            )
        return value

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.username != username:
                raise serializers.ValidationError(
                    'Пользователь с адресом электронной почты уже существует.'
                )
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'error': 'Неверный код подтверждения.'})
        data['user'] = user
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitleChangeSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=True
    )

    class Meta:
        model = Title
        fields = [
            'id',
            'name',
            'year',
            'genre',
            'description',
            'category',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            title_id = request.parser_context['kwargs']['title_id']
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(
                title=title,
                author=request.user
            ).exists():
                raise serializers.ValidationError(
                    "На одно произведение пользователь может оставить "
                    "только один отзыв."
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
