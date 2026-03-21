from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import BootstrapAdminRequestSerializer, BootstrapAdminResponseSerializer, CreateAccountRequestSerializer, CreateAccountResponseSerializer, DeactivateAccountResponseSerializer, LoginRequestSerializer, SetupStatusResponseSerializer, SetupStatusResponseSerializer, UserListResponseSerializer, UserStatusRequestSerializer, MessageResponseSerializer
from common.api_response import error_response,success_response
from accounts.services import admin_exists
from accounts.models import User
from rest_framework.views import APIView
from common.permissions import IsAdminUser
from accounts.serializers import LoginResponseSerializer,LoginRequestSerializer
from drf_spectacular.utils import extend_schema
# Create your views here.
class LoginView(APIView):

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=LoginRequestSerializer, 
        responses=LoginResponseSerializer
    )
    def post(self, request):

        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)

        if not user:
            return error_response("INVALID_CREDENTIALS","Invalid username or password" ,status=401)
        refresh = RefreshToken.for_user(user)

        response_data = LoginResponseSerializer({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "role": user.role
        }).data
        return success_response(response_data)


class BootStrapAdminView(APIView):

    @extend_schema(
        request=BootstrapAdminRequestSerializer, 
        responses=BootstrapAdminResponseSerializer
    )   
    def post(self, request):
        if admin_exists():
            return error_response("ADMIN_ALREADY_EXISTS","An admin user already exists", status=400)
        serializer = BootstrapAdminRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        User.objects.create_user(username=username, password=password, role=User.ROLE_ADMIN)
        response_data = BootstrapAdminResponseSerializer({
            "message": "Admin user created successfully"
        }).data
        return success_response(response_data)
    
    

class SetupStatusView(APIView):
    @extend_schema(
        responses=SetupStatusResponseSerializer
    )
    def get(self, request):
        response_data = SetupStatusResponseSerializer({
            "admin_exists": admin_exists()
        }).data 
        return success_response(response_data)

class CreateAccountView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request = CreateAccountRequestSerializer,
        responses= CreateAccountResponseSerializer
    )
    def post(self, request):
        serializer = CreateAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
            role=serializer.validated_data["role"]
        )
        response_data = {
            "message": "Account created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }

        return success_response(response_data)

class UserListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        responses=UserListResponseSerializer(many=True)
    )   
    def get(self, request):
        users = User.objects.all()
        user_data = [{"id": user.id, "username": user.username, "role": user.role, "is_active": user.is_active} for user in users]
        return success_response(user_data)

class DeactivateUserView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=UserStatusRequestSerializer,
        responses=MessageResponseSerializer
    )   
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return success_response({"message": "User deactivated successfully"})
        except User.DoesNotExist:
            return error_response("USER_NOT_FOUND", "User not found", status=400)

class ActivateUserView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=UserStatusRequestSerializer,
        responses=MessageResponseSerializer
    )   
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return success_response({"message": "User activated successfully"})
        except User.DoesNotExist:
            return error_response("USER_NOT_FOUND", "User not found", status=400)