from rest_framework import serializers


class ContainerStartRequestSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)    

class ContainerStartResponseSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=255)

class ContainerStopResponseSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=255)

class ContainerStopRequestSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)

class ContanerRestartRequestSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)

class ContainerLogsRequestSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)
    tail = serializers.IntegerField(required=False, default=200)