from rest_framework import serializers

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    role = serializers.CharField()

class BootstrapAdminRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)

class BootstrapAdminResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class SetupStatusResponseSerializer(serializers.Serializer):
    admin_exists = serializers.BooleanField()

class CreateAccountRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=["admin", "developer", "viewer"])

class CreateAccountResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = serializers.DictField(child=serializers.CharField())

class UserListResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    is_active = serializers.BooleanField()
    role = serializers.CharField()

class UserStatusRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    
