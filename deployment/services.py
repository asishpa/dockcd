from deployment.models import Deployment
from deployment.executor import LocalDeploymentExecutor
from deployment.tasks import run_deployment

def trigger_application_deployment(application):
    services = application.services.all()
    print(f"Found {len(services)} services for application id {application.id}.")
    deployments = []
    for service in services:
        deployment = Deployment.objects.create(service=service)

        running = Deployment.objects.filter(
            service=service,
            status=Deployment.STATUS_RUNNING
        ).exists()

        if not running:
            run_deployment.delay(str(deployment.id))
        deployments.append(deployment)
    return deployments