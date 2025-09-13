from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ValidateRequestSerializer
from celery import chord, group
from core.celery import get_smtp_records, aggregate_results

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
        tasks = group(get_smtp_records.s(email) for email in emails)
        callback = aggregate_results.s()
        result = chord(tasks)(callback)
        final_result = result.get(timeout=60)
        return Response(final_result, status=status.HTTP_200_OK)
