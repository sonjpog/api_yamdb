from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers as ser, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

import permissions
from api.serializers import UserSerializer, TokenSerializer
from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import BasicActionsViewSet
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleChangeSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ViewSet):
    """CRUD операции."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdmin]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, username):
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignupViewSet(viewsets.ViewSet):
    """Регистрация пользователей."""
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'email': serializer.validated_data['email'],
                         'username': serializer.validated_data['username']},
                        status=status.HTTP_200_OK)


class UserProfileView(viewsets.ViewSet):
    """Профиль пользователя."""
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ViewSet):
    """Выдача токенов."""
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username'])
        confirmation_code = serializer.validated_data['confirmation_code']
        if user.confirmation_code != confirmation_code:
            return Response({'error': 'Неверный код подтверждения.'},
                            status=status.HTTP_400_BAD_REQUEST)
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class TitlesViewSet(ModelViewSet):
    """Получить список всех объектов."""
    queryset = Title.objects.all()
    serializer_class = TitleReadSerializer
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'POST'):
            return TitleChangeSerializer
        return TitleReadSerializer


class CategoryViewSet(BasicActionsViewSet):
    """Получить список всех категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(BasicActionsViewSet):
    """Получить список всех жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class MockUser:
    """Модель-заглушка для пользователя."""
    def __init__(self, username='mockuser'):
        self.username = username

    @property
    def is_authenticated(self):
        return True


class MockPermission:
    """Заглушка для проверки прав доступа."""
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (MockPermission,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title=title_id)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        try:
            # Используем MockUser вместо self.request.user
            mock_user = MockUser()
            serializer.save(author=mock_user, title=self.get_title())
        except IntegrityError:
            raise ser.ValidationError("Не удается создать повторяющийся отзыв.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
