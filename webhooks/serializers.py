from rest_framework import serializers

class CreateGitHubWebhookRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    branch = serializers.CharField()

class CreateGitHubWebhookResponseSerializer(serializers.Serializer):
    webhook_id = serializers.UUIDField()