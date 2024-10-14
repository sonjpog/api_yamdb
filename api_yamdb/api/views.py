from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers as ser, status, viewsets
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import MethodNotAllowed

from api.serializers import UserSerializer, TokenSerializer
from reviews.models import Category, Comment, Genre, Review, Title
from .filters import TitleFilter
from .mixins import BasicActionsViewSet
from .permissions import IsAdmin, IsAuthorOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleChangeSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """CRUD операции."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username', 'email', 'bio', 'first_name', 'last_name',)

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        user = get_object_or_404(User, username=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk):
        user = get_object_or_404(User, username=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        user = get_object_or_404(User, username=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(method='PUT')

    @action(methods=['patch', 'get'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        return Response(serializer.data)


class SignupViewSet(viewsets.ModelViewSet):
    """Регистрация пользователей."""
    permission_classes = [AllowAny]

    def create(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        if User.objects.filter(email=email).exists():
            if not User.objects.filter(username=username).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=email)
            return Response({'email': user.email, 'username': user.username},
                            status=status.HTTP_200_OK)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            confirmation_code = get_random_string(length=6)
            user.confirmation_code = confirmation_code
            user.save()
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {confirmation_code}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'email': user.email, 'username': user.username},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(viewsets.ModelViewSet):
    """Профиль пользователя."""
    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ModelViewSet):
    """Выдача токенов."""
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'},
                            status=status.HTTP_404_NOT_FOUND)
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


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title=title_id)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        title = self.get_title()
        user_review_exists = Review.objects.filter(
            title=title,
            author=self.request.user
        ).exists()
        if user_review_exists:
            raise ValidationError("На одно произведение пользователь",
                                  "может оставить только один отзыв.")
        serializer.save(author=self.request.user, title=title)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
