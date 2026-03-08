from rest_framework.views import APIView
from applications.serializers import ApplicationRegistrationSerializer
from .service import register_application_service
from common.api_response import success_response


class RegisterApplicationView(APIView):

    def post(self, request):
        serializer = ApplicationRegistrationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        application, services = register_application_service(
            serializer.validated_data
        )
        print(application)
        return success_response({
            "application_id": str(application.id)
        })