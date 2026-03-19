from django.shortcuts import render
from rest_framework.views import APIView
from common.docker_client import docker_client
from common.api_response import success_response,error_response
from common.permissions import IsAutheneticatedUser
from containers.container_actions import start_container, stop_container, restart_container
from containers.serializers import ContainerLogsRequestSerializer, ContainerLogsResponseSerializer, ContainerRestartRequestSerializer, ContainerStartResponseSerializer, ContainerStartRequestSerializer,ContainerStopRequestSerializer,ContainerStopResponseSerializer,ContainerRestartResponseSerializer
from services.docker_utils import get_service_container
from services.models import Service
from drf_spectacular.utils import extend_schema
# Create your views here.
class ContainerLogsView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
            request= ContainerLogsRequestSerializer,
            responses= ContainerLogsResponseSerializer
            
    )
    def get(self, request, container_id, *args, **kwargs):
        tail = request.GET.get("tail", 200)
        try:
            container = docker_client.containers.get(container_id)
        except docker_client.errors.NotFound:
            return error_response("CONTAINER_NOT_FOUND","Container not found", status=400)
        logs = container.logs(tail=tail).decode("utf-8").splitlines()
        return success_response({
            "container_id": container_id,
            "logs": logs})


class ContainerStartView(APIView):
    permission_classes = [IsAutheneticatedUser]


    @extend_schema(
        request=ContainerStartRequestSerializer,
        responses=ContainerStartResponseSerializer
    )
    def post(self, request, container_id, *args, **kwargs):
        start_container(container_id)
        return success_response({"message": f"Container {container_id} started successfully"})

class ContainerStopView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        request=ContainerStopRequestSerializer,
        responses=ContainerStopResponseSerializer
    )
    def post(self, request, container_id):
        stop_container(container_id)
        return success_response({"message": f"Container {container_id} stopped successfully"})


class ContainerRestartView(APIView):


    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        request = ContainerRestartRequestSerializer,
        responses = ContainerRestartResponseSerializer
    )
    def post(self, request, container_id):
        restart_container(container_id)
        return success_response({"message": f"Container {container_id} restarted successfully"})