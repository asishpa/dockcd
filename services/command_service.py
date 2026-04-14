from common.exceptions import CommandNotAllowed
import shlex

import logging
logger = logging.getLogger(__name__)

def _extract_base_command(command):
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()

    if not parts:
        raise CommandNotAllowed("Empty command is not allowed.")

    return parts[0]


def ensure_allowed_command(command):
    from services.models import AllowedCommands

    command = command.strip()
    allowed_commands = AllowedCommands.objects.values_list('command', flat=True)

    is_allowed = any(command.startswith(allowed) for allowed in allowed_commands)

    logger.info(f"Validating command '{command}' - allowed: {is_allowed}")

    if not is_allowed:
        raise CommandNotAllowed(
            f"Command '{command}' is not in allowed commands."
        )

def validate_command(user, command):
    if user.role == user.ROLE_ADMIN:
        return

    ensure_allowed_command(command)