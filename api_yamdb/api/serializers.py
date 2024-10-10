import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role'
        )

        def validate_username(self, value):
            if value == 'me':
                raise serializers.ValidationError(
                    "Нельзя использовать 'me' в качестве username.")
            return value

        def create(self, validated_data):
            confirmation_code = str(random.randint(100000, 999999))
            user = User(**validated_data)
            user.confirmation_code = confirmation_code
            user.save()
            send_mail(
                str({confirmation_code}),
                [validated_data['email']],
                fail_silently=False,
            )
            return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if user is None:
            raise serializers.ValidationError('Пользователь не найден.')
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения.')
        return data
