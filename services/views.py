from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from common import docker_client
from common.api_response import success_response,error_response
from common.permissions import IsAdminOrDeveloper, IsAutheneticatedUser, IsAdmin
from services.command_service import validate_command
from services.docker_utils import get_service_container
from services.models import Service
from services.serializers import ServiceActionRequestSerializer, ServiceContainersViewResponseSerializer, ServiceExecViewRequestSerializer, ServiceExecViewResponseSerializer, ServiceStatusViewResponseSerializer, ServiceActionResponseSerializer
from services.services import get_service_status, restart_service, start_service, stop_service
from deployment.exec_service import validate_command, execute_command
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