from deployment.models import Deployment, ServiceDeployment
from deployment.executor import LocalDeploymentExecutor
from deployment.tasks import run_deployment

def trigger_application_deployment(application):
    deployment = Deployment.objects.create(
        application=application,
        status = Deployment.STATUS_PENDING
        )
    for service in application.services.order_by("deploy_order"):
        sd = ServiceDeployment.objects.create(
            deployment=deployment,
            service=service,
            status=ServiceDeployment.STATUS_PENDING
        )
        run_deployment.delay(str(sd.id))
    return deployment