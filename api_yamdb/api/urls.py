from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (TitlesViewSet,
                    CategoryViewSet,
                    GenreViewSet,
                    )

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('titles', TitlesViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
