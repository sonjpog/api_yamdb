from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters import rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView

from .filters import TitleFilter
from .mixins import BasicActionsViewSet
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleChangeSerializer, TitleReadSerializer)
from api.serializers import TokenSerializer, UserSerializer
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """CRUD операции."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username', 'email', 'bio', 'first_name', 'last_name',)
    lookup_field = 'username'
    http_method_names = 'get', 'post', 'head', 'patch', 'delete'

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


class SignupView(APIView):
    """Регистрация пользователей."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if User.objects.filter(email=request.data.get('email'),
                               username=request.data.get('username')).exists():
            return Response({'email': request.data.get('email'),
                             'username': request.data.get('username')},
                            status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = get_random_string(length=6)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({'email': user.email, 'username': user.username},
                        status=status.HTTP_200_OK)


class TokenView(APIView):
    """Выдача токенов."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-rating')
    filterset_class = TitleFilter
    filter_backends = [rest_framework.DjangoFilterBackend]
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return TitleChangeSerializer
        return TitleReadSerializer


class CategoryViewSet(BasicActionsViewSet):
    """Получить список всех категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(BasicActionsViewSet):
    """Получить список всех жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    """Создание отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_queryset(self):
        title = self.get_title()
        return Review.objects.filter(title=title)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Создание комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def get_review(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, title_id=title_id, id=review_id)

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
