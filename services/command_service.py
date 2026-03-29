from common.exceptions import CommandNotAllowed
import shlex


def _extract_base_command(command):
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()

    if not parts:
        raise CommandNotAllowed("Empty command is not allowed.")

    return parts[0]


def ensure_allowed_command(command):
    from services.models import AllowedCommands  # lazy import

    base_command = _extract_base_command(command)
    allowed = AllowedCommands.objects.filter(command=base_command).exists()
    if not allowed:
        raise CommandNotAllowed(
            f"Command '{base_command}' is not in allowed commands."
        )

def validate_command(user, command):
    if user.role == user.ROLE_ADMIN:
        return

    ensure_allowed_command(command)