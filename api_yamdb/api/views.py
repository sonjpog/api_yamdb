from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

import permissions
from api.serializers import UserSerializer, TokenSerializer

User = get_user_model()


class UserViewSet(viewsets.ViewSet):
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
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'email': serializer.validated_data['email'],
                         'username': serializer.validated_data['username']},
                        status=status.HTTP_200_OK)


class UserProfileView(viewsets.ViewSet):
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
