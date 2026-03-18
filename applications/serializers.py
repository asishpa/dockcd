from rest_framework import serializers


class ApplicationRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    repo_url = serializers.URLField()
    branch = serializers.CharField(default="main")
    deploy_path = serializers.CharField()
    already_cloned = serializers.BooleanField(default=False)

    def validate_deploy_path(self, value):
        if not value.startswith("/opt/dockcd"):
            raise serializers.ValidationError(
                "Deploy path must be inside /opt/dockcd"
            )
        return value
    
class ApplicationRegistrationResponseSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    name = serializers.CharField(max_length=100)

class ApplicationServiceStatusViewSerializer(serializers.Serializer):
    service_name = serializers.CharField()
    status = serializers.CharField()
    service_id = serializers.UUIDField()
    container_count = serializers.IntegerField()
    containers = serializers.ListField(child=serializers.DictField())

class ApplicationListResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    branch = serializers.CharField()
    created_at = serializers.DateTimeField()
    deploy_path = serializers.CharField()
