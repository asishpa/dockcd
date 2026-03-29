from http.client import responses

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from common import docker_client
from common.api_response import success_response,error_response
from common.permissions import IsAdminOrDeveloper, IsAutheneticatedUser, IsAdmin
from services.command_service import validate_command
from services.docker_utils import get_service_container
from services.models import AllowedCommands, Service
from services.serializers import AllowedCommandCreateRequestSerializer, AllowedCommandResponseSerializer, ServiceActionRequestSerializer, ServiceContainersViewResponseSerializer, ServiceExecViewRequestSerializer, ServiceExecViewResponseSerializer, ServiceListBasicResponseSerializer, ServiceListRequestSerializer, ServiceListResponseSerializer, ServiceStatusViewResponseSerializer, ServiceActionResponseSerializer
from services.services import get_service_status, restart_service, start_service, stop_service
from services.command_service import validate_command
from deployment.exec_service import execute_command
from common.exceptions import CommandNotAllowed, ContainerNotFound
# Create your views here.
class ServiceStatusView(APIView):
    permission_classes = [IsAutheneticatedUser]
    @extend_schema(
        responses=ServiceStatusViewResponseSerializer
    )
    def get(self,request,service_id):
        service = Service.objects.get(id=service_id)
        status  = get_service_status(service)
        serializer = ServiceStatusViewResponseSerializer(data=status)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.data
        return success_response(response_data)

class RestartServiceView(APIView):
    permission_classes = [IsAdminOrDeveloper]
    @extend_schema(
        request= ServiceActionRequestSerializer,
        responses=ServiceActionResponseSerializer
    )
    def post(self,request,service_id):
        service = Service.objects.get(id=service_id)
        restarted_containers = restart_service(service)
        serializer = ServiceActionResponseSerializer(data={
            "action": "restart",
            "containers": restarted_containers
        })
        serializer.is_valid(raise_exception=True)
        response_data = serializer.data
        return success_response(response_data)
class StopServiceView(APIView):
    permission_classes = [IsAdmin]
    @extend_schema(
        request= ServiceActionRequestSerializer,
        responses=ServiceActionResponseSerializer
    )
    def post(self,request,service_id):
        service = Service.objects.get(id=service_id)
        stopped_containers = stop_service(service)
        serializer = ServiceActionResponseSerializer(data={
            "action": "stop",
            "containers": stopped_containers
        })
        serializer.is_valid(raise_exception=True)
        response_data = serializer.data
        return success_response(response_data)
class StartServiceView(APIView):
    permission_classes = [IsAdmin]
    @extend_schema(
        request= ServiceActionRequestSerializer,
        responses=ServiceActionResponseSerializer
    )
    def post(self,request,service_id):
        service = Service.objects.get(id=service_id)
        started_containers = start_service(service)
        serializer = ServiceActionResponseSerializer(data={
            "action": "start",
            "containers": started_containers
        })
        serializer.is_valid(raise_exception=True)
        response_data = serializer.data
        return success_response(response_data)
class ServiceExecView(APIView):

    permission_classes = [IsAdminOrDeveloper]

    @extend_schema(
        request=ServiceExecViewRequestSerializer,
        responses=ServiceExecViewResponseSerializer
    )
    def post(self, request, service_id):
        command = request.data.get("command")
        container_name = request.data.get("container_name")
        if not command and not container_name:
            return error_response("INVALID_REQUEST","Command and container_name are required", status=400)
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return error_response("SERVICE_NOT_FOUND","Service not found", status=400)
        container_names = get_service_container(service)
        if container_name not in container_names:
            return error_response("INVALID_CONTAINER","Container does not belong to this service")
        validate_command(request.user,command)

        result = execute_command(container_name,command)
        serializer = ServiceExecViewResponseSerializer(data={"output": result})
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.data)

class ServiceContainersView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        responses=ServiceContainersViewResponseSerializer
    )
    def get(self,request,service_id):

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return error_response("SERVICE_NOT_FOUND","Service not found", status=400)
        containers = get_service_container(service)
        serializer = ServiceContainersViewResponseSerializer(data={
            "containers": containers
        })
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.data)
    
class ContainerLogsView(APIView):
    permission_classes = [IsAutheneticatedUser]

    def get(self,request,container_name):
        tail = request.GET.get("tail", 200)
        try:
            container = docker_client.containers.get(container_name)
        except docker_client.errors.NotFound:
            return error_response("CONTAINER_NOT_FOUND","Container not found", status=400)
        logs = container.logs(tail=tail).decode("utf-8")
        return success_response({
            "container_name": container_name,
            "logs": logs})
class ServiceListView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        parameters=[ServiceListRequestSerializer],
        responses=ServiceListResponseSerializer(many=True)
    )
    def get(self,request):
        serializer = ServiceListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        application_id = serializer.validated_data["application_id"]
        basic = serializer.validated_data.get("basic", False)
        services = Service.objects.filter(application_id=application_id)

        if basic:
            response_data = ServiceListBasicResponseSerializer(services, many=True).data
            return success_response(response_data)

        response_data = ServiceListResponseSerializer(services, many=True).data
        return success_response(response_data)


class AllowedCommandListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdminOrDeveloper()]
        return [IsAdmin()]

    @extend_schema(
        responses=AllowedCommandResponseSerializer(many=True),
    )
    def get(self, request):
        commands = AllowedCommands.objects.all().order_by("command")
        response_data = AllowedCommandResponseSerializer(commands, many=True).data
        return success_response(response_data)

    @extend_schema(
        request=AllowedCommandCreateRequestSerializer,
        responses=AllowedCommandResponseSerializer,
    )
    def post(self, request):
        serializer = AllowedCommandCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        command = serializer.validated_data["command"].strip()
        description = serializer.validated_data.get("description", "")

        if not command:
            return error_response("INVALID_REQUEST", "command is required", status=400)

        allowed_command, created = AllowedCommands.objects.get_or_create(
            command=command,
            defaults={"description": description},
        )
        if not created:
            return error_response("COMMAND_EXISTS", f"Command '{command}' already exists.", status=400)

        response_data = AllowedCommandResponseSerializer(allowed_command).data
        return success_response(response_data)