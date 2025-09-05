from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout

class LoginView(APIView):
    def post(self, request):
        return Response({'message': '로그인 성공'})

class LogoutView(APIView):
    def post(self, request):
        return Response({'message': '로그아웃 성공'})

class RegisterView(APIView):
    def post(self, request):
        return Response({'message': '회원가입 성공'})

class ProfileView(APIView):
    def get(self, request):
        return Response({'profile': {}})