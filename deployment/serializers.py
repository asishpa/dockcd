
from rest_framework import serializers


class TriggerDeploymentViewRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()

class TriggerDeploymentViewResponseSerializer(serializers.Serializer):
    deployment_ids = serializers.ListField(
        child=serializers.UUIDField()
    )

