from django.shortcuts import render
from rest_framework.views import APIView
from common.docker_client import docker_client
from common.api_response import success_response,error_response
from common.permissions import IsAutheneticatedUser
from services.docker_utils import get_service_container
from services.models import Service
# Create your views here.
class ContainerLogsView(APIView):
    permission_classes = [IsAutheneticatedUser]

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