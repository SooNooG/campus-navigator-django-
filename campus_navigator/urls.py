from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password reset и т.д.
    path('accounts/', include('accounts.urls')),            # register, profile
    path("", include("campus.urls")),
]