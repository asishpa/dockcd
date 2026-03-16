from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from common.api_response import success_response, error_response
from applications.models import Application
from common.permissions import IsAdmin, IsAutheneticatedUser
from deployment.serializers import TriggerDeploymentViewRequestSerializer, TriggerDeploymentViewResponseSerializer
from .services import trigger_application_deployment


class TriggerDeploymentView(APIView):
    permission_classes = [IsAdmin]
    @extend_schema(
        request=TriggerDeploymentViewRequestSerializer,
        responses=TriggerDeploymentViewResponseSerializer
    )   
    def post(self, request):
        serializer = TriggerDeploymentViewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application_id = serializer.validated_data.get("application_id")
        application = Application.objects.get(id=application_id)
        deployments = trigger_application_deployment(application)
        response_data = TriggerDeploymentViewResponseSerializer({
            "deployment_ids": [str(d.id) for d in deployments]
        }).data
        return success_response(response_data)