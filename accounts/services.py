from accounts.models import User

def admin_exists():
    return User.objects.filter(role=User.ROLE_ADMIN).exists()