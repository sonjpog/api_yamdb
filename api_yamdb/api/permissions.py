from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение, позволяющее изменять отзыв
    только автору или модератору/администратору.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsModerator(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только модераторам.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator


class IsAdmin(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только администраторам.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только администраторам изменять данные.

    Всем остальным пользователям разрешен только доступ на чтение.
    Это разрешение предназначено для контроля доступа к изменению данных
    в зависимости от роли пользователя.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )
