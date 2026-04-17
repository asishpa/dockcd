import os
import subprocess
import logging
from django.utils import timezone
from django.db.models import F, Value
from django.db.models.functions import Concat

from deployment.models import Deployment, ServiceDeployment
from deployment.executor import LocalDeploymentExecutor
from deployment.tasks import run_deployment

logger = logging.getLogger(__name__)

def trigger_application_deployment(application):
    deployment = Deployment.objects.create(
        application=application,
        status = Deployment.STATUS_PENDING
        )
    
    # Sync repo first as the initial step
    _sync_application_repo(deployment, application)
    
    # Then queue service deployments
    for service in application.services.order_by("deploy_order"):
        sd = ServiceDeployment.objects.create(
            deployment=deployment,
            service=service,
            status=ServiceDeployment.STATUS_PENDING
        )
        run_deployment.delay(str(sd.id))
    return deployment


def _sync_application_repo(deployment, application):
    """Sync the application repository before service deployments."""
    deploy_path = application.deploy_path
    repo_url = application.repo_url
    branch = application.branch
    
    try:
        log_line = f"[{timezone.now().isoformat()}] [app:{application.name}] Starting repository sync...\n"
        Deployment.objects.filter(id=deployment.id).update(
            logs=Concat(F("logs"), Value(log_line))
        )
        
        if not os.path.exists(deploy_path):
            _git_clone(repo_url, deploy_path, branch)
            sync_msg = f"Repository cloned from {repo_url} branch {branch}"
        else:
            _git_pull(deploy_path, branch)
            sync_msg = f"Repository pulled latest changes from {repo_url} branch {branch}"
        
        log_line = f"[{timezone.now().isoformat()}] [app:{application.name}] {sync_msg}\n"
        Deployment.objects.filter(id=deployment.id).update(
            logs=Concat(F("logs"), Value(log_line))
        )
        logger.info(f"Application {application.name} repo sync completed")
    except Exception as exc:
        log_line = f"[{timezone.now().isoformat()}] [app:{application.name}] Repository sync failed: {str(exc)}\n"
        Deployment.objects.filter(id=deployment.id).update(
            logs=Concat(F("logs"), Value(log_line)),
            status=Deployment.STATUS_FAILED,
            finished_at=timezone.now()
        )
        logger.error(f"Application {application.name} repo sync failed: {exc}")
        raise


def _git_clone(repo_url, deploy_path, branch):
    """Clone git repository."""
    cmd = ["git", "clone", "-b", branch, repo_url, deploy_path]
    _run_cmd(cmd, cwd=os.path.dirname(deploy_path))


def _git_pull(deploy_path, branch):
    """Pull latest changes from git repository."""
    _run_cmd(["git", "fetch", "origin"], cwd=deploy_path)
    _run_cmd(["git", "checkout", branch], cwd=deploy_path)
    _run_cmd(["git", "pull", "origin", branch], cwd=deploy_path)


def _run_cmd(cmd, cwd):
    """Run a shell command and raise exception on failure."""
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    command_str = " ".join(cmd)
    logger.info(f"Running command: {command_str} in {cwd}")
    
    for line in process.stdout:
        logger.debug(line.strip())
    
    process.wait()
    
    if process.returncode != 0:
        raise RuntimeError(f"Command failed: {command_str}")