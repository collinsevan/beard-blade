from django.contrib import admin
from django.urls import path, include
from barber import views as barber_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', barber_views.home, name='home'),
    path('base/', barber_views.base_view, name='base'),
    path('about/', barber_views.about, name='about'),
    path('book/', barber_views.book_now, name='book_now'),
    path("accounts/register/", barber_views.register, name="register"),
    path("accounts/logout/", auth_views.LogoutView.as_view(
        template_name="registration/logout.html"), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
]
