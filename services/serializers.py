from rest_framework import serializers

class ServiceStatusViewResponseSerializer(serializers.Serializer):
    status = serializers.CharField() 

class ServiceActionRequestSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
class ServiceActionResponseSerializer(serializers.Serializer):
    action = serializers.CharField()
    containers = serializers.ListField(
        child=serializers.CharField()
    )

class ServiceExecViewRequestSerializer(serializers.Serializer):
    command = serializers.CharField()
    container_name = serializers.CharField()

class ServiceExecViewResponseSerializer(serializers.Serializer):
    output = serializers.CharField()

class ServiceContainersViewResponseSerializer(serializers.Serializer):
    containers = serializers.ListField(
        child=serializers.CharField()
    )

    