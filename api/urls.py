from django.urls import path, include
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework import routers
from django.conf import settings


SWAGGER_URL = settings.SWAGGER_URL

schema_view = get_schema_view(
    openapi.Info(
        title="Email Validation API",
        default_version='v1',
        description='''Email Validation API''',
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="info@lalitmahato.com.np"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=SWAGGER_URL,
)

router = routers.SimpleRouter()

urlpatterns = [
    path('email-service/', include('email_service.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# router.register(r"province", ProvinceView, basename="province_view")

urlpatterns += router.urls

