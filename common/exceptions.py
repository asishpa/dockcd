class ApplicationError(Exception):
    error_code = "APPLICATION_ERROR"
    status_code = 400

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class DeployPathInvalid(ApplicationError):
    error_code = "DEPLOY_PATH_INVALID"


class DeployPathExists(ApplicationError):
    error_code = "DEPLOY_PATH_ALREADY_EXISTS"


class GitCloneFailed(ApplicationError):
    error_code = "GIT_CLONE_FAILED"

class ContainerNotFound(ApplicationError):
    error_code = "CONTAINER_NOT_FOUND"
    status_code = 400
class CommandNotAllowed(ApplicationError):
    error_code = "COMMAND_NOT_ALLOWED"
    status_code = 403

class ContainerStartFailed(ApplicationError):
    error_code = "CONTAINER_START_FAILED"
    status_code = 500

class ContainerStopFailed(ApplicationError):
    error_code = "CONTAINER_STOP_FAILED"
    status_code = 500