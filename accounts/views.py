from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from common.api_response import error_response,success_response
from accounts.services import admin_exists
from accounts.models import User
from rest_framework.views import APIView
# Create your views here.
class LoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        username = request.data["username"]
        password = request.data["password"]

        user = authenticate(request, username=username, password=password)

        if not user:
            return error_response("INVALID_CREDENTIALS","Invalid username or password" ,status=401)
        refresh = RefreshToken.for_user(user)

        return success_response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "role": user.role
        })

class BootSstrapAdminView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if admin_exists():
            return error_response("ADMIN_ALREADY_EXISTS","An admin user already exists", status=400)
        username = request.data["username"]
        password = request.data["password"]

        User.objects.create_user(username=username, password=password, role=User.Role.ADMIN)
        return success_response({"message": "Admin user created successfully"})
    

class SetupStatusView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        exists = admin_exists()
        return success_response({"setup_required": not exists})
        return JsonResponse({"admin_exists": admin_exists()})