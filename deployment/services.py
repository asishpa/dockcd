from deployment.models import Deployment
from deployment.executor import LocalDeploymentExecutor
from dockcd.tasks import run_deployment

def trigger_application_deployment(application):
    services = application.services.all()
    deployments = []
    for service in services:
        deployment = Deployment.objects.create(service=service)

        run_deployment.delay(deployment.id)
        deployments.append(deployment)
    return deployments