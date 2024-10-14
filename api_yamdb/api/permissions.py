from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение, позволяющее изменять отзыв только автору или модератору/администратору.
    """

    def has_object_permission(self, request, view, obj):
        # Если запрос "безопасный" (например, GET), то разрешаем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешаем изменение или удаление, если пользователь — автор, модератор или админ
        return obj.author == request.user or request.user.role in ['moderator', 'admin'] or request.user.is_staff


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == 'moderator')


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == 'admin')
