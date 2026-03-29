from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import ActivateUserView, AdminResetPasswordView, BootStrapAdminView, CreateAccountView, DeactivateUserView, LoginView, SetupStatusView, UserListView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("bootstrap-admin/", BootStrapAdminView.as_view(), name="bootstrap_admin"),
    path("setup-status/", SetupStatusView.as_view(), name="setup_status"),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-user/', CreateAccountView.as_view(), name='create_user'),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:user_id>/deactivate/", DeactivateUserView.as_view(), name="deactivate_user"),
    path("users/<int:user_id>/activate/", ActivateUserView.as_view(), name="activate_user"),
    path("users/<int:user_id>/reset-password/", AdminResetPasswordView.as_view()),
]
