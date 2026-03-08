from django.urls import path
from .views import RegisterApplicationView

urlpatterns = [
    path(
        "register/",
        RegisterApplicationView.as_view(),
        name="register-application"
    ),
]