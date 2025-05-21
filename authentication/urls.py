from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from authentication import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView
)

app_name='authentication'

urlpatterns = [
    path('jwt-token/',
         views.JwtTokenObtainView.as_view(),
         name='token_obtain_pair'),

    path('jwt-token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),

    path('jwt-token/verify/',
         TokenVerifyView.as_view(),
         name='token_verify'),

    path('jwt-token/black-list/',
         TokenBlacklistView.as_view(),
         name='jwt_black_list'),

    path('sign-up/',
         views.SignUpView.as_view(),
         name='sign_up'),

    path('resend-verification/',
         views.ResendVerification.as_view(),
         name='resend_verification'),

    path('verify/',
         views.Verify.as_view(),
         name='verify'),

    path('check-verified/',
         views.UserVerificationCheckAPIView.as_view(),
         name='check_verified'),

    path('forgot-password/',
         views.ForgotPassword.as_view(),
         name='forgot_password'),

    path('change-password/',
         views.ChangePassword.as_view(),
         name='change_password'),
]