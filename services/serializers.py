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
class ServiceListRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    basic = serializers.BooleanField(required=False, default=False)


class ServiceListBasicResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class ServiceListResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    application_id = serializers.UUIDField(source="application.id")
    compose_file_path = serializers.CharField()
    deploy_path = serializers.CharField()
    auto_deploy = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class AllowedCommandCreateRequestSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)


class AllowedCommandResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    command = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()
    