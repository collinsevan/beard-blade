"""
URL configuration for beardblade project.

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
from barber import views as barber_views
from django.contrib.auth import views as auth_views   # noqa F401


urlpatterns = [
    path('', barber_views.home, name='home'),
    path('base/', barber_views.base_view, name='base'),
    path('about/', barber_views.about, name='about'),
    path("book/", barber_views.book_now, name="book_now"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
]
