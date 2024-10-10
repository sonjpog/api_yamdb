from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import SignupViewSet, TokenViewSet, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('signup', SignupViewSet, basename='signup')
router_v1.register('auth/token', TokenViewSet, basename='token')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
