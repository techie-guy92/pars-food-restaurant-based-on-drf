from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import (SignupAPIView, VerifyEmailAPIView, ResendVerificationEmailAPIView,
                    UserProfileAPIView, LoginAPIView, FetchUsersGenericsView, UpdateUserAPIView, PasswordResetAPIView, SetNewPasswordAPIView)


router = DefaultRouter()
# router.register(r"activate", ActivationCodeViewSet, basename="activation-code")
# router.register(r"complete-registration", UserProfileViewSet, basename='user-profile')
# router.register(r"complete-registration", UserProfileModelViewSet, basename='user-profile')


urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("resend-verification-email/", ResendVerificationEmailAPIView.as_view(), name="resend-verification-email"),
    path("verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
    path("complete-profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("fetch-users/", FetchUsersGenericsView.as_view(), name="fetch-users-no-id"),
    # path("fetch-users/", FetchUsersAPIView.as_view(), name="fetch-users-no-id"),
    # re_path(r"^fetch-users/(?P<user_id>[\w\-]+)/$", FetchUsersAPIView.as_view(), name="fetch-users-by-id"),
    path("update-user/", UpdateUserAPIView.as_view(), name="update-user"),
    path("password-reset/", PasswordResetAPIView.as_view(), name="password-reset"),
    path("set-new-password/", SetNewPasswordAPIView.as_view(), name="set-new-password"),
]

urlpatterns += router.urls