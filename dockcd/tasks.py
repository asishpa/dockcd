from celery import shared_task
from deployment.models import Deployment
from deployment.executor import LocalDeploymentExecutor

@shared_task
def run_deployment(deployment_id):
    deployment = Deployment.objects.get(id=deployment_id)
    executor = LocalDeploymentExecutor(deployment)
    executor.run()