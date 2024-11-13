import django
import os
django.setup()
os.environ["DJANGO_SETTINGS_MODULE"]= "core.settings"

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse, resolve
from unittest.mock import patch
from model_bakery.baker import make
import pytz
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from .urls import *
from .views import *


# pip install pytz
# pip install model-bakery
# Run tests using: py manage.py test
# Run tests using: py manage.py test app_name.tests_module.TestClass


#==================================== SignUp Test =============================================

class SignUpTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("signup")
        
        self.user_data = {
            "first_name": "Soheil",
            "last_name": "Daliri",
            "email": "soheil.dalirii@gmail.com",
            "password": "abcABC123&",
            "re_password": "abcABC123&"  
        }
        
    def test_customuser_model(self):
        user_1 = CustomUser.objects.create(
            first_name=self.user_data["first_name"], 
            last_name=self.user_data["last_name"], 
            email=self.user_data["email"]
        )
        user_1.set_password(self.user_data["password"])
        user_1.save()
        self.assertEqual(str(user_1), f"{user_1.first_name} {user_1.last_name}")
        self.assertEqual(user_1.email, user_1.email)
        
    def test_customuser_serializer(self):
        user_1 = CustomUser.objects.create(
            first_name=self.user_data["first_name"], 
            last_name=self.user_data["last_name"], 
            email=self.user_data["email"]
        )
        user_1.set_password(self.user_data["password"])
        user_1.save()
        serializer = CustomUserSerializer(user_1)
        serializer_data = serializer.data
        self.assertEqual(serializer_data["id"], user_1.id)
        self.assertIn("email", serializer_data)
        
    def test_sign_up_user(self):
        response = self.client.post(self.url, self.user_data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print("Response Data: ", response.data) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "اطلاعات شما ثبت شد، برای تکمیل فرایند ثبت نام به ایمیل خود بروید و ایمل تایید را تایید کنید.")
        
    def test_sign_pp_url_resolve(self):
        view = resolve("/api/v1/signup/")
        self.assertEqual(view.func.cls, SignupAPIView)


#==================================== Resend Verification Email Test ================================

class ResendVerificationEmailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("resend-verification-email")
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil",
            last_name="Daliri",
            email="soheil.dalirii@gmail.com",
        )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.token = str(RefreshToken.for_user(self.user_1))
        self.valid_email_data = {"email": self.user_1.email}
        self.invalid_email_data = {"email": "nonexistent@example.com"}

    @patch("users.views.email_sender")  
    def test_resend_verification_email(self, mock_email_sender):
        response = self.client.post(self.url, self.valid_email_data, format="json")
        if response.status_code != status.HTTP_200_OK:
            print("Response Data: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "ایمیل تایید دوباره ارسال شد.")
        # This line verifies that the mock_email_sender function was called exactly one time during the test. 
        # It's a way to assert that the function or method you are testing behaved as expected in terms of how many times it was invoked.
        # To confirm that the email_sender function is called exactly once, ensuring your logic is executed as anticipated.
        # To make sure that the function is neither called too many times nor missed entirely.
        mock_email_sender.assert_called_once()

    def test_user_already_verified(self):
        self.user_1.is_active = True
        self.user_1.save()
        response = self.client.post(self.url, self.valid_email_data, format="json")
        if response.status_code != status.HTTP_200_OK:
            print("Response Data: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "ایمیل شما قبلا تایید شده بوده است.")

    def test_email_not_found(self):
        response = self.client.post(self.url, self.invalid_email_data, format="json")
        if response.status_code != status.HTTP_404_NOT_FOUND:
            print("Response Data: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "ایمیل مورد نظر یافت نشد، دوباره ثبت نام کنید")

    def test_resend_verification_email_url_resolve(self):
        view = resolve("/api/v1/resend-verification-email/")
        self.assertEqual(view.func.cls, ResendVerificationEmailAPIView)



#==================================== Verify Email Test =============================================

class VerifyEmailTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("verify-email")
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil", 
            last_name="Daliri", 
            email="soheil.dalirii@gmail.com", 
        )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.token = str(RefreshToken.for_user(self.user_1))

    def test_verify_email_view(self):
        response = self.client.post(self.url, {"token": self.token}, format="json") 
        if response.status_code != status.HTTP_200_OK:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "ثبت نام شما کامل شد.")

    def test_verify_email_url_resolve(self):
        view = resolve("/api/v1/verify-email/")
        self.assertEqual(view.func.cls, VerifyEmailAPIView)

        
#==================================== User Profile Test =============================================

class UserProfileTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user-profile")
        
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil", 
            last_name="Daliri", 
            email="soheil.dalirii@gmail.com"
            )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.client.force_authenticate(user=self.user_1)
        
        self.user_profile_data = {
            "user": self.user_1.id,  
            "phone": "09123469239",
            "gender": "other",
            "bio": "I'm a full-stack developer"
        }
        
    def test_user_profile_model(self):
        profile_data = UserProfile.objects.create(user=self.user_1, phone="09123469239", gender="other", bio="I'm a full-stack developer")
        self.assertEqual(str(profile_data), f"{self.user_1.first_name} {self.user_1.last_name}")
        self.assertEqual(profile_data.phone, "09123469239")
    
    def test_user_profile_serializer(self):
        profile_data = UserProfile.objects.create(user=self.user_1, phone="09123469239", gender="other", bio="I'm a full-stack developer")
        serializer = UserProfileSerializer(profile_data)
        serializer_data = serializer.data
        self.assertEqual(serializer_data["id"], profile_data.id)
        self.assertIn("gender", serializer_data)
        
    def test_add_user_profile(self):  
        response = self.client.post(self.url, self.user_profile_data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print("Response Data: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "اطلاعات شما تکمیل شد")
        
    def test_user_profile_url_resolve(self):
        view = resolve("/api/v1/complete-profile/")
        self.assertEqual(view.func.cls, UserProfileAPIView)


#======================================= Login Test =================================================

class LoginTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("login")
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil",
            last_name="Daliri",
            email="soheil.dalirii@gmail.com",
            is_active=True
        )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        
        self.login_data = {"email": self.user_1.email, "password": "abcABC123&"}
    
    def test_login_serializer(self):
        serializer = LoginSerializer(data=self.login_data)
        # In API tests, like when testing user login or profile updates, the primary focus is on ensuring the API's response and behavior, which includes making sure that the correct data is accepted and returned. 
        # In those cases, the API endpoint handles calling is_valid(), and our tests ensure that the overall process works as expected.
        serializer.is_valid()
        serializer_data = serializer.data
        self.assertIn("email", serializer_data)
        self.assertNotIn("password", serializer_data)  
    
    def test_login_user_view(self):
        response = self.client.post(self.url, self.login_data, format="json")
        if response.status_code != status.HTTP_200_OK:
            print("Response Data: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_url_resolve(self):
        view = resolve("/api/v1/login/")
        self.assertEqual(view.func.cls, LoginAPIView)

        
#==================================== Fetch Users Test ==============================================

class FetchUsersTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("fetch-users-no-id")
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil",
            last_name="Daliri",
            email="soheil.dalirii@gmail.com",
            user_type="backend",
            is_active=True,
            is_admin=True 
        )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.client.force_authenticate(user=self.user_1)
    
    def test_fetch_users_serializer(self):
        serializer = FetchUsersSerializers(self.user_1)
        serialize_data = serializer.data
        self.assertIn("is_active", serialize_data)
        self.assertIn("date_joined", serialize_data)
    
    def test_fetch_users_view(self):
        response = self.client.get(self.url)
        if response.status_code != status.HTTP_200_OK:
            print("Response Data: ", response.data)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", []) # Access to nested data
        if results:
            user_data = results[0]  # Assuming there's at least one user in the results
            self.assertEqual(user_data["is_active"], True)
            self.assertEqual(user_data["id"], self.user_1.id)
        else:
            self.fail("No results found in response data")

    def test_fetch_users_url_resolve(self):
        view = resolve("/api/v1/fetch-users/")
        self.assertEqual(view.func.cls, FetchUsersGenericsView)

        
#==================================== Update User Test ==============================================

class UpdateUserTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("update-user")
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil", 
            last_name="Daliri", 
            email="soheil.dalirii@gmail.com", 
            is_active=True
        )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.client.force_authenticate(user=self.user_1)
        self.user_1_updated = {"first_name": "Reza", "last_name": "Ahmadi"}
    
    def test_update_user_serializer(self):
        serializer = UpdateUserSerializer(self.user_1, data=self.user_1_updated, partial=True)
        self.assertTrue(serializer.is_valid())  
        serializer.save()  
        serializer_data = serializer.data
        self.assertNotIn("email", self.user_1_updated)
        self.assertEqual(serializer_data["first_name"], "Reza")
        self.assertEqual(serializer_data["last_name"], "Ahmadi")

    
    def test_update_user_view(self):
        response = self.client.put(self.url, self.user_1_updated, format="json")
        if response.status_code != status.HTTP_200_OK:
            print("Response Data", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "اطلاعات شما با موفقیت تغییر کرد.")
    
    def test_update_user_url_resolve(self):
        view = resolve("/api/v1/update-user/")
        self.assertEqual(view.func.cls, UpdateUserAPIView)

        
#==================================== Password Reset Test ===========================================

class PasswordResetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("password-reset")
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil", 
            last_name="Daliri", 
            email="soheil.dalirii@gmail.com", 
            is_active=True
        )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.client.force_authenticate(user=self.user_1)
        self.user_data = {"email": self.user_1.email}
        self.invalid_user_data = {"email": "invalid.email@example.com"}

    def test_password_reset_serializer(self):
        serializer = PasswordResetSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        serializer_data = serializer.data
        self.assertIn("email", serializer_data)

    def test_password_reset_view(self):
        response = self.client.post(self.url, self.user_data, format="json")
        if response.status_code != status.HTTP_200_OK:
            print("Response Data", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "ایمیل تعییر رمز عبور ارسال شد.")
    
    # The @patch decorator is a powerful tool used to replace objects in your code with mock objects during testing. 
    # It is particularly useful for isolating and testing specific parts of your code by controlling their behavior.
    # It is used when we want to test a method that relies on external systems or services (like sending emails, accessing a database, or making network calls), you can use it to replace those dependencies with mock objects.
    # it allows you to control the behavior of the mocked objects. For instance, you can specify what the mock should return or how it should behave when called.
    # It helps verify that certain interactions occur during the execution of your code. For example, you can check if a specific function is called the expected number of times with the correct arguments.
    @patch("users.views.email_sender")
    def test_password_reset_view_email_sending(self, mock_email_sender):
        response = self.client.post(self.url, self.user_data, format="json")
        if response.status_code != status.HTTP_200_OK:
            print("Response Data", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "ایمیل تعییر رمز عبور ارسال شد.")
        mock_email_sender.assert_called_once()

    def test_password_reset_invalid_email(self):
        response = self.client.post(self.url, self.invalid_user_data, format="json")
        if response.status_code != status.HTTP_404_NOT_FOUND:
            print("Response Data", response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "ایمیل وارد شده معتبر نمی باشد.")
        
    def test_password_reset_url_resolve(self):
        view = resolve("/api/v1/password-reset/")
        self.assertEqual(view.func.cls, PasswordResetAPIView)

        
#==================================== Set New Password Test =========================================

class SetNewPasswordTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("set-new-password")
        self.user_1 = CustomUser.objects.create(
            first_name="Soheil", 
            last_name="Daliri", 
            email="soheil.dalirii@gmail.com", 
            is_active=True
        )
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.client.force_authenticate(user=self.user_1)

        self.token = str(RefreshToken.for_user(self.user_1))
        
        self.user_data = {
            "password": "abcABC123*", 
            "re_password": "abcABC123*", 
            "token": self.token
        }
        self.non_esixt_user_data = {
            "password": "abcABC123*", 
            "re_password": "abcABC123*", 
            "token": "invalid_token"
        }
        self.invalid_user_data = {
            "password": "abcABC", 
            "re_password": "abcABC", 
            "token": self.token
        }

    def test_set_new_password_serializer(self):
        serializer = SetNewPasswordSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        serializer_data = serializer.validated_data  # it checks the validation result
        self.assertIn("password", serializer_data)
        self.assertIn("re_password", serializer_data)
        self.assertIn("token", serializer_data)

    def test_set_new_password_view(self):
        response = self.client.post(self.url, self.user_data, format="json")
        if response.status_code != status.HTTP_200_OK:
            print("Response Data", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "رمز عبور با موفقیت تغییر کرد.")

    def test_set_new_password_view_non_exsist_user(self):
        response = self.client.post(self.url, self.non_esixt_user_data, format="json")
        # In scenarios where a user does not exist, it's indeed more appropriate to use a 404 Not Found status code. 
        # This can help to differentiate between a general invalid request and a situation where the specific resource is missing.
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            print("Response Data", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "توکن معتبر نیست و یا منقضی شده است.")

    def test_set_new_password_view_invalid_data(self):
        response = self.client.post(self.url, self.invalid_user_data, format="json")
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            print("Response Data", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "رمز عبور باید متشکل از حروف کوچک، بزرگ و عدد باشد، و هشت رقمی نیز باشد"
        )

    def test_set_new_password_url_resolve(self):
        view = resolve("/api/v1/set-new-password/")
        self.assertEqual(view.func.cls, SetNewPasswordAPIView)

        
#====================================================================================================
