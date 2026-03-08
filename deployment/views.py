from rest_framework.views import APIView
from common.api_response import success_response, error_response
from applications.models import Application
from .services import trigger_application_deployment


class TriggerDeploymentView(APIView):
    def post(self, request):
        application_id = request.data.get("application_id")
        aplication = Application.objects.get(id=application_id)
        deployments = trigger_application_deployment(aplication)
        return success_response({
            "deployment_ids": [str(d.id) for d in deployments]
        })