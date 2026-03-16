##here do not use common api response as these are not client facing apis and we want to return specific status for different scenarios like ignored, duplicate etc which is not error but also not success. We can use custom status codes or messages in the response to indicate these scenarios clearly.

import json

from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_spectacular.utils import extend_schema

from applications.models import Application
from common.api_response import success_response
from common.permissions import IsAdmin
from deployment.tasks import run_deployment
from services.models import Service
from deployment.models import Deployment
from webhooks.models import GitHubWebhook
from webhooks.serializers import CreateGitHubWebhookRequestSerializer, CreateGitHubWebhookResponseSerializer
from webhooks.services import create_github_webhook
from webhooks.utils import verify_github_signature
from rest_framework.views import APIView
from webhooks.utils import is_duplicate_event

@csrf_exempt
@require_POST
def github_webhook(request):
    payload = request.body 
    signature = request.headers.get("X-Hub-Signature-256")
    delivery_id = request.headers.get("X-GitHub-Delivery")
    
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    repo_url = data["repository"]["clone_url"]
    branch = data["repository"]["default_branch"]

    try:
        application = Application.objects.get(
            repo_url=repo_url,
            branch=branch
        )
    except Application.DoesNotExist:
        return JsonResponse({"status": "ignored"}, status=200)

    try:
        webhook = application.github_webhook

    except GitHubWebhook.DoesNotExist:
        return HttpResponseForbidden("Webhook not configured")

    if not verify_github_signature(
        webhook.secret,
        payload,
        signature
    ):
        return HttpResponseForbidden("Invalid signature")
    if is_duplicate_event(delivery_id):
        return JsonResponse({"status": "duplicate"}, status=200)
    changed_files = set()

    for commit in data.get("commits", []):
        for f in commit.get("added", []):
            changed_files.add(f)
        for f in commit.get("modified", []):
            changed_files.add(f)
        for f in commit.get("removed", []):
            changed_files.add(f)

    triggered = []

    services = Service.objects.filter(
        application=application,
        auto_deploy=True
    )

    for service in services:
        if service.compose_file_path in changed_files:
            deployment = Deployment.objects.create(
                service=service,
                commit_sha=data.get("after", "")
            )
            run_deployment.delay(deployment.id)
            triggered.append(str(deployment.id))

    return JsonResponse({
        "status": "processed",
        "deployments": triggered
    })


class CreateGitHubWebhookView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        request=CreateGitHubWebhookRequestSerializer,
        responses=CreateGitHubWebhookResponseSerializer
    )
    def post(self, request):

        serializer = CreateGitHubWebhookRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application_id = serializer.validated_data["application_id"]
        secret = serializer.validated_data["secret"]

        webhook = create_github_webhook(application_id, secret)
        response_data = CreateGitHubWebhookResponseSerializer({
            "webhook_id": webhook.id
        }).data
        return success_response(response_data)