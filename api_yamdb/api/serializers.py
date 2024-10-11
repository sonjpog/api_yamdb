import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers

from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role'
        )

        def validate_username(self, value):
            if value == 'me':
                raise serializers.ValidationError(
                    "Нельзя использовать 'me' в качестве username.")
            return value

        def create(self, validated_data):
            confirmation_code = str(random.randint(100000, 999999))
            user = User(**validated_data)
            user.confirmation_code = confirmation_code
            user.save()
            send_mail(
                str({confirmation_code}),
                [validated_data['email']],
                fail_silently=False,
            )
            return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if user is None:
            raise serializers.ValidationError('Пользователь не найден.')
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения.')
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

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
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title

        
class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fields = ('author',)
