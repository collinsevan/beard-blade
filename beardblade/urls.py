from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from barber import views as barber_views
from barber.views import (
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView
)

urlpatterns = [
    path('', barber_views.home, name='home'),
    path('base/', barber_views.base_view, name='base'),
    path('about/', barber_views.about, name='about'),
    path('services/', barber_views.services, name='services'),
    path('book/', barber_views.book_now, name='book_now'),
    path('accounts/profile/', barber_views.profile, name='profile'),
    path("accounts/register/", barber_views.register, name="register"),

    path('accounts/password_change/',
         CustomPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/',
         CustomPasswordChangeDoneView.as_view(), name='password_change_done'),

    path("accounts/logout/",
         auth_views.LogoutView.as_view(
             template_name="registration/logout.html"),
         name="logout"),

    path('accounts/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_request.html',
             email_template_name='registration/password_reset_email.html'
         ),
         name='password_reset'),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_change_done.html'
         ),
         name='password_reset_complete'),

    path("accounts/", include("django.contrib.auth.urls")),

    path('admin/', admin.site.urls),
    path("cancel/<int:booking_id>/",
         barber_views.booking_cancel, name="booking_cancel"),
    path('reviews/', barber_views.reviews, name='reviews'),
    path('review/delete/<int:review_id>/',
         barber_views.delete_review, name='delete_review'),
    path('review/create/<int:booking_id>/',
         barber_views.create_review, name='create_review'),
    path('review/edit/<int:review_id>/',
         barber_views.edit_review, name='edit_review'),
    path("ratings/", include("star_ratings.urls", namespace="ratings")),
]

handler400 = 'barber.views.custom_bad_request'
handler403 = 'barber.views.custom_permission_denied'
handler404 = 'barber.views.custom_page_not_found'
handler500 = 'barber.views.custom_server_error'
