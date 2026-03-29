from celery import shared_task
from .models import Deployment, ServiceDeployment
from .executor import LocalDeploymentExecutor


@shared_task
def run_deployment(service_deployment_id):
    sd = ServiceDeployment.objects.get(id=service_deployment_id)
    executor = LocalDeploymentExecutor(sd)
    print("Starting deployment executor for deployment id:", service_deployment_id)
    executor.run()