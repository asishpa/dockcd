from rest_framework import serializers
from services.models import Service


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
    sync_status = serializers.CharField()
    desired_commit = serializers.CharField()
    last_deployed_commit = serializers.CharField()
    service_id = serializers.UUIDField()
    container_count = serializers.IntegerField()
    containers = serializers.ListField(child=serializers.DictField())

class ApplicationListResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    branch = serializers.CharField()
    created_at = serializers.DateTimeField()
    deploy_path = serializers.CharField()
    has_webhook = serializers.SerializerMethodField()

    def get_has_webhook(self, obj):
        return hasattr(obj, "github_webhook")

class ApplicationDeleteRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()

class ApplicationDeleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class ServiceStatusSerializer(serializers.ModelSerializer):

    sync_status = serializers.SerializerMethodField()

    def get_sync_status(self, obj):
        if obj.desired_commit != obj.last_deployed_commit:
            return "out_of_sync"
        return "synced"

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "sync_status",
            "desired_commit",
            "last_deployed_commit"
        ]

class SyncApplicationResponseSerializer(serializers.Serializer):
    deployment_id = serializers.UUIDField()
    service_deployments = serializers.ListField(
        child=serializers.UUIDField()
    )
