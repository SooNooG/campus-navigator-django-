from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom account views should be checked first so logout uses our GET-friendly handler.
    path('accounts/', include('accounts.urls')),            # register, profile, logout
    path('accounts/', include('django.contrib.auth.urls')),  # login, password reset и т.д.
    path("", include("campus.urls")),
]