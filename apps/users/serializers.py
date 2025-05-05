from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        # Create a user and hash the password
        user = User.objects.create_user(
            username=validated_data['username'],  # You can still pass username here for registration, even though email is primary
            email=validated_data['email'],
            password=validated_data['password']  # Django will hash the password automatically
        )
        return user