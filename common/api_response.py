from rest_framework.response import Response


def success_response(data=None, status=200):
    return Response({
        "success": True,
        "data": data
    }, status=status)


def error_response(code, message, status=400):
    return Response({
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }, status=status)