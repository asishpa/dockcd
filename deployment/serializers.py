
from rest_framework import serializers
from deployment.models import Deployment, ServiceDeployment


class TriggerDeploymentViewRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()

class TriggerDeploymentViewResponseSerializer(serializers.Serializer):
    deployment_id = serializers.UUIDField()


class ApplicationDeploymentListItemSerializer(serializers.ModelSerializer):
    deployment_id = serializers.UUIDField(source="id")

    class Meta:
        model = Deployment
        fields = [
            "deployment_id",
            "status",
            "commit_sha",
            "started_at",
            "finished_at",
            "created_at",
        ]


class DeploymentLogsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deployment
        fields = [
            "logs",
        ]


class ServiceDeploymentListItemSerializer(serializers.ModelSerializer):
    service_deployment_id = serializers.IntegerField(source="id")

    class Meta:
        model = ServiceDeployment
        fields = [
            "service_deployment_id",
            "status",
            "started_at",
            "finished_at",
        ]

