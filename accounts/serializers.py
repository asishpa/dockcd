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