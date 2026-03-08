import cmd
from concurrent.futures import process
import os
import subprocess
from datetime import datetime

from django.utils import timezone
from .models import Deployment


class LocalDeploymentExecutor:
    def __init__(self, deployment: Deployment):
        self.deployment = deployment
        self.service = deployment.service
        self.application = self.service.application

    def run(self):
        try:
            self._mark_running()
            self._sync_repo()
            self._docker_compose_pull()
            self._docker_compose_up()
            self._mark_success()
        except Exception as exc:
            self._mark_failed(str(exc))
            raise

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