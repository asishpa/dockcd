from rest_framework.views import exception_handler
from rest_framework.response import Response
from common.exceptions import ApplicationError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    if isinstance(exc, ApplicationError):
        return Response({
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message
            }
        }, status=exc.status_code)

    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": response.data
            }
        }, status=response.status_code)
    logger.exception("Unhandled exception in API")

    return Response({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Unexpected server error"
        }
    }, status=500)