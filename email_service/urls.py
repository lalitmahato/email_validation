from django.urls import path, include
from email_service.views import ValidateEmailsView

urlpatterns = [
    path("api/validate/", ValidateEmailsView.as_view(), name="validate_email"),
]
