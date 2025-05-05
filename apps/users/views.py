from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.auth import login

# Create your views here.

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]



class LoginView(APIView):
    def post(self, request):
        # Get the email and password from the request body
        email = request.data.get("email")
        password = request.data.get("password")

        # Check if email and password are provided
        if not email or not password:
            return JsonResponse({"message": "Email and password must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user with email
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Log the user in
            login(request, user)

            # Return user details after successful login
            response_data = {
                "user_id": user.id,
                "email": user.email,
                "password":user.password,
                "message": "Login successful"
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        # If authentication fails
        return JsonResponse({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
