from rest_framework import viewsets, mixins


class BasicActionsViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    Кастомный ViewSet, предоставляющий действия для создания, 
    получения списка и удаления объектов.

    Доступные действия:
    - create (POST): Создание нового объекта
    - list (GET): Получение списка объектов
    - destroy (DELETE): Удаление объекта
    """
    pass
