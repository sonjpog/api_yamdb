from rest_framework import viewsets, status, serializers as ser
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Review
from .serializers import ReviewSerializer


class MockUser:
    """Модель-заглушка для пользователя."""
    def __init__(self, username='mockuser'):
        self.username = username

    @property
    def is_authenticated(self):
        return True


class MockTitle:
    """Модель-заглушка для Title."""
    def __init__(self, title_id=1):
        self.id = title_id
        self.name = "Mock Title"


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
        """Возвращает заглушку вместо реальной модели Title."""
        title_id = self.kwargs.get('title_id', 1)
        return MockTitle(title_id=title_id)

    def perform_create(self, serializer):
        """Creates a review for the current title."""
        try:
            # Используем MockUser вместо self.request.user
            mock_user = MockUser()
            mock_title = self.get_title()
            serializer.save(author=mock_user, title=mock_title)
        except IntegrityError:
            raise ser.ValidationError("Cannot create a duplicate review.")

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
