"""
URL configuration for foodhub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home
from core import views as core_views


app_name = "core"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),  # Home page
    path("about/", core_views.about, name="about"),
    path("shipping/", core_views.shipping, name="shipping"),
    path("contact/", core_views.contact, name="contact"),
    path("users/", include("users.urls")),
    path("restaurants/", include("restaurants.urls")),
    path("menu/", include("menu.urls")),
    path("deliveries/", include("deliveries.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("privacy/", core_views.privacy, name="privacy"),
    path("terms/", core_views.terms, name="terms"),
    path("operator/export-csv/", core_views.export_csv, name="export_csv"),
    path(
        "operator/assign/<int:order_id>/",
        core_views.operator_assign,
        name="operator_assign",
    ),
    path("orders/", include("orders.urls", namespace="orders")),
]

# need only in dev mode (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
