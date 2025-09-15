from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from celery import chord, group, chain
from core.celery import get_smtp_records, aggregate_results, create_domain_record
from email_service.utils import get_unique_domain_from_email
from email_service.models import EmailDomains
from email_service.serializers import ValidateRequestSerializer, EmailDomainSerializer


class ValidateEmailsView(CreateAPIView):
    """
    POST /api/v1/email-service/api/validate/
    { "emails": ["a@b.com", "x@y.org"] }
    """
    serializer_class = ValidateRequestSerializer

    @staticmethod
    def get_dns_records(domains):
        final_result = {}
        email_domains_obj = EmailDomains.objects.filter(domain__in=domains).iterator()
        for email_domain in email_domains_obj:
            serializer = EmailDomainSerializer(email_domain)
            final_result[email_domain.domain] = serializer.data
        return final_result

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        emails = serializer.validated_data["emails"]

        unique_domains, new_domains = get_unique_domain_from_email(emails)
        email_domain_creation_tasks = group(
            create_domain_record.s(email_domain) for email_domain in new_domains
        ).apply_async()
        email_domain_creation_tasks.get(timeout=300)
        domain_wise_result = self.get_dns_records(unique_domains)
        final_result = [
            {"email": email, "result": domain_wise_result.get(email.split("@")[1], {"message": "Unable to get dns records"})}
            for email in emails
        ]
        return Response(final_result, status=status.HTTP_200_OK)
