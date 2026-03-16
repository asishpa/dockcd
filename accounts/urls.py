from django.urls import path
from .views import BootStrapAdminView, LoginView, SetupStatusView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("bootstrap-admin/", BootStrapAdminView.as_view(), name="bootstrap_admin"),
    path("setup-status/", SetupStatusView.as_view(), name="setup_status"),      
]
