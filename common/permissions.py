from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self,request, view):
        return( request.user
        and request.user.is_authenticated
        and request.user.role == 'admin'
)
class IsAdminOrDeveloper(BasePermission):
    def has_permission(self,request, view):
        return( request.user
        and request.user.is_authenticated
        and (request.user.role == 'admin' or request.user.role == 'developer')
)
class IsAutheneticatedUser(BasePermission):
    def has_permission(self,request, view):
        return( request.user
        and request.user.is_authenticated
)