from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('profile/update/', views.updateUser, name="update-user"),
    path('', views.home, name="home"),
    path('flight/search/', views.flight_search, name='flight_search'),
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
     
     path('setup-2fa-email/', views.setup_2fa_email, name='setup_2fa_email'),
    path('send-2fa-email/', views.send_2fa_email ,name='send_2fa_email'),
    path('verify-2fa-email/', views.verify_2fa_email, name='verify_2fa_email'),
     
    path('dashboard/', views.dashboard, name='dashboard'),
     path('payment/', views.payment, name='payment'),
    path('process_payment/', views.process_payment, name='process_payment'),
     path('payment_success/', views.payment_success, name='payment_success'),
     path('payment_error/', views.payment_error, name='payment_error'),

    # Password reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name="password_reset.html",
             email_template_name='password_reset_email.html',
          ),name='password_reset'),

    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
         name='password_reset_done'),

    path('password_reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),
         name='password_reset_confirm'),

    path('password_reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
         name='password_reset_complete'),

     # CAPTCHA URL
     path('captcha/', include('captcha.urls')),

     #Flight URL
     path('flight_search/', views.flight_search, name='flight_search'),
    path('flight_booking/<str:flight_id>/', views.flight_booking, name='flight_booking'),
    path('booking_confirmation/<str:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
   ]
