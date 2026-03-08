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