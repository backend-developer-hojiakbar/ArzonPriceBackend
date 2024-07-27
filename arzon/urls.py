from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf.urls.static import static
from django.conf import settings
from drugs.views import DrugSearchView, ExcelUploadViewSet, verify_token
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter

schema_view = get_schema_view(
    openapi.Info(
        title="booking API",
        default_version='v1',
        description="Mall official site description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
router = DefaultRouter()
router.register(r'upload', ExcelUploadViewSet, basename='excel-upload')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('router/', include(router.urls)),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/drugs/', DrugSearchView.as_view(), name='drug-search'),
    # path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('api/verify-token/', verify_token, name='verify_token'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)