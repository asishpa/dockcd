from celery import shared_task
from .models import Deployment
from .executor import LocalDeploymentExecutor

@shared_task
def run_deployment(deployment_id):
    deployment = Deployment.objects.get(id=deployment_id)
    executor = LocalDeploymentExecutor(deployment)
    print("Starting deployment executor for deployment id:", deployment_id)
    executor.run()