from rest_framework import serializers

from alerts.models import AlertRule

class AlertRuleCreateRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    conditions = serializers.ChoiceField(choices=["container_down", "container_restarting"])

class AlertRuleResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertRule
        fields = [
            "id",
            "condition",
            "frequency_minutes",
            "enabled",
        ]


class AlertChannelCreateRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=["email", "webhook"])
    email = serializers.EmailField(required=False)
    webhook_url = serializers.URLField(required=False)

class AlertChannelCreateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
class AlertChannelResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    email = serializers.EmailField(required=False)
    webhook_url = serializers.URLField(required=False)

class AlertChannelListRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
