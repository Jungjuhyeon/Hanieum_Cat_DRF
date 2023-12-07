"""dj_pr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.urls import re_path as url


schema_view = get_schema_view(
    openapi.Info(
        title="open API",
        default_version='v1',
        description="Your Swagger Docs descriptions",
        terms_of_service="https://www.google.com/policies/terms/",
        #contact=openapi.Contact(email="contact@snippets.local"),
        #license=openapi.License(name="BSD License"),
  ),
    public=True,
    permission_classes=(AllowAny,)
)
urlpatterns = [
    #url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    #url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('djadmin/', admin.site.urls),
    path('uploader/', include('uploader.urls')),
]
# 미디어 경로 추가
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

