from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('signin/', SigninView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('verify-otp/', OTPVerifyView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]
