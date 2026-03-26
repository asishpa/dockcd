from rest_framework import serializers


class ContainerBaseSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)

class ContainerOperationResponseSerializer(ContainerBaseSerializer):
    message = serializers.CharField(max_length=255)
class ContainerStartRequestSerializer(ContainerBaseSerializer):
    pass

class ContainerStartResponseSerializer(ContainerOperationResponseSerializer):
    pass
class ContainerStopResponseSerializer(ContainerOperationResponseSerializer):
    pass
class ContainerStopRequestSerializer(ContainerBaseSerializer):
    pass

class ContainerRestartRequestSerializer(ContainerBaseSerializer):
    pass
class ContainerRestartResponseSerializer(ContainerOperationResponseSerializer):
    pass

class ContainerLogsRequestSerializer(ContainerBaseSerializer):
    tail = serializers.IntegerField(required=False, default=200)

class ContainerLogsResponseSerializer(serializers.Serializer):
    container_id = serializers.CharField(max_length=255)
    logs = serializers.ListField(
        child=serializers.CharField()
    )



class ContainerListResponseSerializer(serializers.Serializer):
    containers = serializers.ListField(
        child=serializers.DictField()
    )