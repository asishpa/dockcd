from asyncio.log import logger
import cmd
from concurrent.futures import process
import os
import subprocess
from datetime import datetime
import uuid
from django.utils import timezone
from .models import Deployment
from common.redis_client import redis_client
class LocalDeploymentExecutor:
    def __init__(self, deployment: Deployment):
        self.deployment = deployment
        self.service = deployment.service
        self.application = self.service.application
        self.lock_token  = str(uuid.uuid4())
        

    def run(self):
        if not self._acquire_lock():
            logger.info(f"Deployment already in progress for service {self.service.name}. Marking this deployment as queued.")
            self.deployment.status = Deployment.STATUS_QUEUED
            self.deployment.logs += "\nAnother deployment is currently in progress. This deployment has been queued and will run once the current deployment finishes."
            self.deployment.save(update_fields=["status", "logs"])
            return

        try:
            self._mark_running()
            self._sync_repo()
            self._docker_compose_pull()
            self._docker_compose_up()
            self._mark_success()
        except Exception as exc:
            self._mark_failed(str(exc))
            raise
        finally:
            self._release_lock()
            self._trigger_next_deployment()

    # --------------------
    # State updates
    # --------------------

    def _mark_running(self):
        self.deployment.status = Deployment.STATUS_RUNNING
        self.deployment.started_at = timezone.now()
        self.deployment.save(update_fields=["status", "started_at"])

    def _mark_success(self):
        self.deployment.status = Deployment.STATUS_SUCCESS
        self.deployment.finished_at = timezone.now()
        self.deployment.save(update_fields=["status", "finished_at"])

    def _mark_failed(self, logs: str):
        self.deployment.status = Deployment.STATUS_FAILED
        self.deployment.logs = logs
        self.deployment.finished_at = timezone.now()
        self.deployment.save(update_fields=["status", "logs", "finished_at"])

    # --------------------
    # Git operations
    # --------------------

    def _sync_repo(self):
        deploy_path = self.service.deploy_path
        repo_url = self.application.repo_url
        branch = self.application.branch

        if not os.path.exists(deploy_path):
            self._git_clone(repo_url, deploy_path, branch)
        else:
            self._git_pull(deploy_path, branch)


    def _git_pull(self, deploy_path, branch):
        print(deploy_path)
        self._run_cmd(["git", "fetch", "origin"], cwd=deploy_path)
        self._run_cmd(["git", "checkout", branch], cwd=deploy_path)
        self._run_cmd(["git", "pull", "origin", branch], cwd=deploy_path)

    # --------------------
    # Docker operations
    # --------------------

    def _docker_compose_pull(self):
        self._run_cmd(
            ["docker", "compose", "-f", self.service.compose_file_path, "pull"],
            cwd=self.service.deploy_path
        )

    def _docker_compose_up(self):
        self._run_cmd(
            ["docker", "compose", "-f", self.service.compose_file_path, "up", "-d"],
            cwd=self.service.deploy_path
        )

    # --------------------
    # Command runner
    # --------------------

    def _run_cmd(self, cmd, cwd):

        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        command_str = " ".join(cmd)

        print(f"\nRunning command: {command_str}\n")

        self.deployment.logs += f"\n$ {command_str}\n"
        self.deployment.save(update_fields=["logs"])
    
        for line in process.stdout:
            print(line, end="")  # show in terminal

            self.deployment.logs += line

        process.wait()

        self.deployment.save(update_fields=["logs"])

        if process.returncode != 0:
            raise RuntimeError(f"Command failed: {command_str}")
    

    def _acquire_lock(self):
        lock_key = f"deploy_lock:{self.service.id}"
        acquired = redis_client.set(lock_key,self.lock_token, nx=True, ex=600)
        return acquired
    
    def _release_lock(self):
        lock_key = f"deploy_lock:{self.service.id}"
        token = redis_client.get(lock_key)
        if token == self.lock_token:
            redis_client.delete(lock_key)
    def _trigger_next_deployment(self):
        #this is intenetional to break circular import as run_deployment also imports LocalDeploymentExecutor to run the deployment task
        from .tasks import run_deployment
        queued = (
            Deployment.objects
            .filter(service=self.service, status=Deployment.STATUS_QUEUED)
        
        .order_by("created_at")
        )
        next_deployment = queued.first()
        if not next_deployment:
            return
        queued.exclude(id=next_deployment.id).update(status=Deployment.STATUS_SUPERSEDED)
        run_deployment.delay(str(next_deployment.id))