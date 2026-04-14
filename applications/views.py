from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework.views import APIView
from applications.serializers import  ApplicationDeleteResponseSerializer, ApplicationDeleteRequestSerializer, ApplicationListResponseSerializer, ApplicationRegistrationSerializer,ApplicationRegistrationResponseSerializer,ApplicationServiceStatusViewSerializer, SyncApplicationResponseSerializer
from common.permissions import IsAdmin
from deployment.models import Deployment, ServiceDeployment
from deployment.tasks import run_deployment
from services.services import update_service_deploy_order
from .service import register_application_service, delete_application_service
from common.api_response import success_response,error_response
from common.permissions import IsAutheneticatedUser
from services.application_status_service import get_application_services_status
from applications.models import Application
from services.serializers import ServiceDeploymentOrderSerializer
import uuid
from django.db.models import F


class RegisterApplicationView(APIView):
    permission_classes = [IsAdmin]
    @extend_schema(
        request=ApplicationRegistrationSerializer,
        responses=ApplicationRegistrationResponseSerializer
    )
    
    def post(self, request):
        serializer = ApplicationRegistrationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        application, services = register_application_service(
            serializer.validated_data
        )
        response_data = ApplicationRegistrationResponseSerializer({
            "application_id": application.id
        ,   "name": application.name
        }).data
        return success_response(response_data)
    
class ApplicationServiceStatusView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Optional service UUID. If provided, returns status for only that service."
            )
        ],
        responses=ApplicationServiceStatusViewSerializer(many=True)
    )
    def get(self,request, application_id):
        service_id = request.query_params.get("service_id")

        if service_id:
            try:
                service_id = str(uuid.UUID(service_id))
            except ValueError:
                return error_response(
                    "INVALID_SERVICE_ID",
                    "service_id must be a valid UUID.",
                    status=400
                )

        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return error_response(
                "APPLICATION_NOT_FOUND",
                "No application found with the provided ID.",
                status=400
            )

        services = get_application_services_status(application, service_id=service_id)

        if service_id and not services:
            return error_response(
                "SERVICE_NOT_FOUND",
                "No service found with the provided service_id for this application.",
                status=404
            )

        response_data = ApplicationServiceStatusViewSerializer(services, many=True).data
        return success_response(response_data)

class ApplicationListView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
         responses=ApplicationListResponseSerializer(many=True)
     )
    def get(self, request):
        applications = Application.objects.select_related("github_webhook").all()
        response_data = ApplicationListResponseSerializer(applications, many=True).data
        return success_response(response_data)

class DeleteApplicationView(APIView):
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request=ApplicationDeleteRequestSerializer,
        responses=ApplicationDeleteResponseSerializer
    )           
    def delete(self, request, application_id):
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return error_response(
                "APPLICATION_NOT_FOUND",
                "No application found with the provided ID.",
                status=404
            )
        delete_application_service(application)
        return success_response({"message": "Application deleted successfully."})


class UpdateServiceDeployOrderView(APIView):

    permission_classes = [IsAdmin]

    @extend_schema(
        request=ServiceDeploymentOrderSerializer
    )
    def post(self, request, application_id):

        serializer = ServiceDeploymentOrderSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            application = Application.objects.get(id=application_id)

        except Application.DoesNotExist:

            return error_response(
                "APPLICATION_NOT_FOUND",
                "Application not found",
                status=404
            )

        update_service_deploy_order(
            application,
            serializer.validated_data["services"]
        )

        return success_response({
            "message": "Service deployment order updated successfully"
        })

class SyncApplicationView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=["Applications"],
        responses=SyncApplicationResponseSerializer
    )

    def post(self, request, application_id):

        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return error_response(
                "APPLICATION_NOT_FOUND",
                "No application found with the provided ID.",
                status=400
            )

        services = application.services.exclude(
            desired_commit=F("last_deployed_commit")
        )

        if not services.exists():

            return error_response(
                "APPLICATION_ALREADY_SYNCED",
                "All services are already synced.",
                status=400
            )

        deployment = Deployment.objects.create(
            application=application,
            commit_sha=max(
                [s.desired_commit for s in services if s.desired_commit],
                default=""
            )
        )

        service_deployments = []

        for service in services:

            sd = ServiceDeployment.objects.create(
                deployment=deployment,
                service=service,
                status=ServiceDeployment.STATUS_PENDING
            )

            run_deployment.delay(str(sd.id))

            service_deployments.append(str(sd.id))

        return success_response({
            "deployment_id": str(deployment.id),
            "service_deployments": service_deployments
        })