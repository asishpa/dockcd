from common.exceptions import CommandNotAllowed

def validate_command(user, command):
    from services.models import AllowedCommands  # lazy import

    if user.role == user.ROLE_ADMIN:
        return

    parts = command.split()
    if not parts:
        raise CommandNotAllowed("Empty command is not allowed.")

    base_command = parts[0]

    allowed = AllowedCommands.objects.filter(command=base_command).exists()
    if not allowed:
        raise CommandNotAllowed(
            f"Command '{base_command}' is not allowed for your role."
        )