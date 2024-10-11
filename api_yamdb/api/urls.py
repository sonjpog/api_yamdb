from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet,
                    GenreViewSet,
                    SignupViewSet,
                    TitlesViewSet,
                    TokenViewSet,
                    UserViewSet
                    )

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('signup', SignupViewSet, basename='signup')
router_v1.register('auth/token', TokenViewSet, basename='token')
router_v1.register('titles', TitlesViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
