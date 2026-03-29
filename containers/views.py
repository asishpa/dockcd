from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from common.docker_client import docker_client
from common.api_response import success_response,error_response
from common.permissions import IsAutheneticatedUser
from containers.container_actions import start_container, stop_container, restart_container
from containers.serializers import ContainerListResponseSerializer, ContainerLogsRequestSerializer, ContainerLogsResponseSerializer, ContainerRestartRequestSerializer, ContainerStartResponseSerializer, ContainerStartRequestSerializer,ContainerStopRequestSerializer,ContainerStopResponseSerializer,ContainerRestartResponseSerializer
from services.docker_utils import get_service_container
from services.models import Service
from applications.models import Application
from drf_spectacular.utils import OpenApiParameter, extend_schema
from common.permissions import IsAutheneticatedUser

# Create your views here.
class ContainerLogsView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
    parameters=[
        OpenApiParameter(
            name="container_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Docker container ID",
        ),
        OpenApiParameter(
            name="tail",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of log lines to return",
            required=False,
            default=200,
        ),
    ],
    responses=ContainerLogsResponseSerializer
)
    def get(self, request, container_id, *args, **kwargs):
        try:
            tail = int(request.GET.get("tail", 200))
        except ValueError:
            return error_response("INVALID_TAIL", "tail must be an integer", status=400)

        try:
            container = docker_client.containers.get(container_id)
        except docker_client.errors.NotFound:
            return error_response("CONTAINER_NOT_FOUND", "Container not found", status=400)

        logs = container.logs(tail=tail).decode("utf-8").splitlines()

        return success_response({
            "container_id": container_id,
            "logs": logs
        })


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

class ContainerListView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="application_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
        responses=ContainerListResponseSerializer
    )     
    def get(self, request):
        application_id = request.query_params.get("application_id")
        application = Application.objects.get(id=application_id)
        deploy_path = application.deploy_path.rstrip("/")

        containers = docker_client.containers.list(all=True)

        container_data = []

        for c in containers:
            labels = c.labels
            working_dir = labels.get("com.docker.compose.project.working_dir", "")

            if working_dir and working_dir.startswith(deploy_path):
                container_data.append({
                    "id": c.short_id.split(":")[-1],
                    "name": c.name,
                    "status": c.status
                })

        return success_response({"containers": container_data})