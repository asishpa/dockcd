from django.shortcuts import render
from rest_framework.views import APIView
from common.api_response import success_response
from common.permissions import IsAdminOrDeveloper, IsAutheneticatedUser, IsAdmin
from services.models import Service
from services.services import get_service_status, restart_service, start_service, stop_service
# Create your views here.
class ServiceStatusView(APIView):
    permission_classes = [IsAutheneticatedUser]
    def get(self,request,service_id):
        service = Service.objects.get(id=service_id)
        status  = get_service_status(service)
        return success_response(status)

class RestartServiceView(APIView):
    permission_classes = [IsAdminOrDeveloper]
    def post(self,request,service_id):
        service = Service.objects.get(id=service_id)
        restarted_containers = restart_service(service)
        return success_response({
            "action": "restart",
            "containers": restarted_containers
        })
class StopServiceView(APIView):
    permission_classes = [IsAdmin]
    def post(self,request,service_id):
        service = Service.objects.get(id=service_id)
        stopped_containers = stop_service(service)
        return success_response({
            "action": "stop",
            "containers": stopped_containers
        })
class StartServiceView(APIView):
    permission_classes = [IsAdmin]
    def post(self,request,service_id):
        service = Service.objects.get(id=service_id)
        started_containers = start_service(service)
        return success_response({
            "action": "start",
            "containers": started_containers
        })