from rest_framework import serializers
from email_service.models import EmailDomains


class EmailDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDomains
        fields = ["domain", "mx_records", "smtp_response", "spf_records", "dmarc_records", "dkim_records"]


class ValidateRequestSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(), allow_empty=False)
