from rest_framework import serializers

class CreateGitHubWebhookRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    secret = serializers.CharField()

class CreateGitHubWebhookResponseSerializer(serializers.Serializer):
    webhook_id = serializers.UUIDField()


class EditGitHubWebhookSecretRequestSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    secret = serializers.CharField()


class EditGitHubWebhookSecretResponseSerializer(serializers.Serializer):
    webhook_id = serializers.UUIDField()