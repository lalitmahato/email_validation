from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ValidateRequestSerializer
from celery import chord, group
from core.celery import get_smtp_records, aggregate_results, create_email_domain_record
from email_service.utils import get_unique_domain_from_email


class ValidateEmailsView(CreateAPIView):
    """
    POST /api/v1/email-service/api/validate/
    { "emails": ["a@b.com", "x@y.org"] }
    """
    serializer_class = ValidateRequestSerializer

    def post(self, request):
        serializer = ValidateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        emails = serializer.validated_data["emails"]
        unique_email_domains = get_unique_domain_from_email(emails)
        unique_email_domain_tasks = group(
            create_email_domain_record.s(emails_domains) for emails_domains in unique_email_domains
        )
        email_domain_tasks_callback = aggregate_results.s()
        email_domain_tasks_result = chord(unique_email_domain_tasks)(email_domain_tasks_callback)
        creation_result = email_domain_tasks_result.get(timeout=60)
        print(creation_result)
        tasks = group(get_smtp_records.s(email) for email in emails)
        callback = aggregate_results.s()
        result = chord(tasks)(callback)
        final_result = result.get(timeout=300)
        return Response(final_result, status=status.HTTP_200_OK)
