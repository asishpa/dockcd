import uuid
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView
from common.api_response import success_response, error_response
from applications.models import Application
from deployment.models import Deployment, ServiceDeployment
from services.models import Service
from common.permissions import IsAdmin, IsAutheneticatedUser
from deployment.serializers import (
    TriggerDeploymentViewRequestSerializer,
    TriggerDeploymentViewResponseSerializer,
    ApplicationDeploymentListItemSerializer,
    DeploymentLogsResponseSerializer,
    ServiceDeploymentListItemSerializer,
)
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
        deployment = trigger_application_deployment(application)
        if deployment is None:
            return error_response(
                code="NO_SERVICES_FOUND",
                message="No services are configured for this application.",
                status=400,
            )
        response_data = TriggerDeploymentViewResponseSerializer({
            "deployment_id": str(deployment.id)
        }).data
        return success_response(response_data)


class ApplicationDeploymentListView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="application_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Application UUID to list deployments for.",
            )
        ],
        responses=ApplicationDeploymentListItemSerializer(many=True)
    )
    def get(self, request):
        application_id = request.query_params.get("application_id")
        if not application_id:
            return error_response(
                code="APPLICATION_ID_REQUIRED",
                message="application_id query parameter is required.",
                status=400,
            )

        try:
            application_id = str(uuid.UUID(application_id))
        except ValueError:
            return error_response(
                code="INVALID_APPLICATION_ID",
                message="application_id must be a valid UUID.",
                status=400,
            )

        if not Application.objects.filter(id=application_id).exists():
            return error_response(
                code="APPLICATION_NOT_FOUND",
                message="No application found with the provided ID.",
                status=404,
            )

        deployments = Deployment.objects.filter(
            application_id=application_id
        ).order_by("-created_at")
        response_data = ApplicationDeploymentListItemSerializer(deployments, many=True).data
        return success_response(response_data)


class DeploymentLogsView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="deployment_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Deployment UUID to retrieve logs for.",
            )
        ],
        responses=DeploymentLogsResponseSerializer,
    )
    def get(self, request):
        deployment_id = request.query_params.get("deployment_id")
        if not deployment_id:
            return error_response(
                code="DEPLOYMENT_ID_REQUIRED",
                message="deployment_id query parameter is required.",
                status=400,
            )

        try:
            deployment_id = str(uuid.UUID(deployment_id))
        except ValueError:
            return error_response(
                code="INVALID_DEPLOYMENT_ID",
                message="deployment_id must be a valid UUID.",
                status=400,
            )

        try:
            deployment = Deployment.objects.get(id=deployment_id)
        except Deployment.DoesNotExist:
            return error_response(
                code="DEPLOYMENT_NOT_FOUND",
                message="No deployment found with the provided ID.",
                status=404,
            )

        response_data = DeploymentLogsResponseSerializer(deployment).data
        return success_response(response_data)


class ServiceDeploymentListView(APIView):
    permission_classes = [IsAutheneticatedUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Service UUID to list deployment runs for.",
            )
        ],
        responses=ServiceDeploymentListItemSerializer(many=True),
    )
    def get(self, request):
        service_id = request.query_params.get("service_id")
        if not service_id:
            return error_response(
                code="SERVICE_ID_REQUIRED",
                message="service_id query parameter is required.",
                status=400,
            )

        try:
            service_id = str(uuid.UUID(service_id))
        except ValueError:
            return error_response(
                code="INVALID_SERVICE_ID",
                message="service_id must be a valid UUID.",
                status=400,
            )

        if not Service.objects.filter(id=service_id).exists():
            return error_response(
                code="SERVICE_NOT_FOUND",
                message="No service found with the provided ID.",
                status=404,
            )

        service_deployments = ServiceDeployment.objects.filter(
            service_id=service_id
        ).select_related("deployment").order_by("-deployment__created_at")

        response_data = ServiceDeploymentListItemSerializer(service_deployments, many=True).data
        return success_response(response_data)
