from django.shortcuts import render
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from .models import AlertChannel, AlertRule
from .serializers import AlertChannelCreateRequestSerializer,AlertChannelCreateResponseSerializer, AlertChannelListRequestSerializer, AlertChannelResponseSerializer,AlertRuleCreateRequestSerializer,AlertRuleResponseSerializer
from rest_framework.views import APIView
from applications.models import Application
from common.api_response import success_response
from common.exceptions import ApplicationNotFound
from common.permissions import IsAdmin
# Create your views here.
class AlertRuleView(APIView):
    permission_classes = [IsAdmin]
    @extend_schema(
            tags=["Alerts"],
            request=AlertRuleCreateRequestSerializer,
            
    )
    def post(self, request):
        serializer = AlertRuleCreateRequestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            application_id = serializer.validated_data["application_id"]
            conditions = serializer.validated_data["conditions"]
            application = Application.objects.filter(id=application_id).first()
            if not application:
                raise ApplicationNotFound("Application not found")
            rule = AlertRule.objects.create(
                application=application,
                condition=conditions
            )
            return success_response({
                "message": "Alert rule created successfully",
            }
            )
    @extend_schema(
            tags=["Alerts"],
            parameters=[
                OpenApiParameter(
                    name="application_id",
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.QUERY,
                    required=True,
                )
            ],
            responses=AlertRuleResponseSerializer(many=True)
    )
    def get(self, request):
            application_id = request.query_params.get("application_id")
            rules = AlertRule.objects.filter(application_id=application_id)
            return success_response(data=AlertRuleResponseSerializer(rules, many=True).data)

class AlertChannelView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
            tags=["Alerts"],
            request=AlertChannelCreateRequestSerializer,
            responses=AlertChannelCreateResponseSerializer
    )
    def post(self, request):
        serializer = AlertChannelCreateRequestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            application_id = serializer.validated_data["application_id"]
            type = serializer.validated_data["type"]
            email = serializer.validated_data.get("email")
            webhook_url = serializer.validated_data.get("webhook_url")
            application = Application.objects.filter(id=application_id).first()
            if not application:
                raise ApplicationNotFound("Application not found")
            AlertChannel.objects.create(
                application=application,
                type=type,
                email=email,
                webhook_url=webhook_url
            )
            return success_response({
                "message": "Alert channel created successfully"
            })
        
    @extend_schema(
            tags=["Alerts"],
            parameters=[
                OpenApiParameter(
                    name="application_id",
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.QUERY,
                    required=True,
                )
            ],
            responses=AlertChannelResponseSerializer(many=True)
    )
    def get(self,request):
        application_id = request.query_params.get("application_id")
        channels = AlertChannel.objects.filter(application_id=application_id)
        return success_response(data=AlertChannelResponseSerializer(channels, many=True).data)



    
