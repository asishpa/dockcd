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