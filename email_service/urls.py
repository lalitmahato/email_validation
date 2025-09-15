from django.urls import path, include
from email_service.views import ValidateEmailsView, LiveEmailsValidateView

urlpatterns = [
    path("multiple-emails/validate/", ValidateEmailsView.as_view(), name="validate_email"),
    path("live-email/validate/", LiveEmailsValidateView.as_view(), name="live_email_validate"),
]
