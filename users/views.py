from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import *
from .serializers import *
from custom_permission import UserCheckOut

#======================================= Needed Methods ===========================================

def email_sender(subject, message, HTML_Content, to):
    sender = settings.EMAIL_HOST_USER
    message = EmailMultiAlternatives(subject, message, sender, to)
    # message = EmailMultiAlternatives(Subject, Message, Sending_From, [To])
    message.attach_alternative(HTML_Content, "text/html")
    message.send()


#======================================== Custom User View ========================================

class SignupAPIView(APIView):
    
    @extend_schema(
        request = CustomUserSerializer,
        responses = {201: CustomUserSerializer}
    )
    def post(self, request):
        email = request.data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "ایمیل مورد نظر ثبت نام کرده است"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = RefreshToken.for_user(user).access_token
            domain = settings.ALLOWED_HOSTS[0]
            verification_link = f"http://{domain}/verify-email?token={str(token)}"
            subject = "Verify your email"
            message = f"Click the link to verify your email: {verification_link}"
            html_content = f"<p>Hello Dear {user.first_name} {user.last_name}<br><br></p><p>Click the link to verify your email: <a href='{verification_link}'>Verify Email</a></p>"
            email_sender(subject, message, html_content, [user.email])
            return Response({'message': "اطلاعات شما ثبت شد، برای تکمیل فرایند ثبت نام به ایمیل خود بروید و ایمل تایید را تایید کنید."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class SignupAPIViewAPIView):

#     @extend_schema(
#         request = CustomUserSerializer,
#         responses = {201: CustomUserSerializer},
#     )
#     def post(self, request, format=None):
#         serializer = CustomUserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#======================================= Verify Email View ====================================

class ResendVerificationEmailAPIView(APIView):
    
    @extend_schema(
        request = None,
        responses = {201: None}
    )
    def post(self, request):
        email = request.data.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                return Response({"message": "ایمیل شما قبلا تایید شده بوده است."}, status=status.HTTP_200_OK)
            
            token = RefreshToken.for_user(user).access_token
            domain = settings.ALLOWED_HOSTS[0]
            verification_link = f"http://{domain}/resend-verification-email?token={str(token)}"
            subject = "Verify your email"
            message = f"Click the link to verify your email: {verification_link}"
            html_content = f"<p>Click the link to verify your email: <a href='{verification_link}'>Verify Email</a></p>"
            email_sender(subject, message, html_content, [user.email])
            return Response({"message": "ایمیل تایید دوباره ارسال شد."}, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response({"error": "ایمیل مورد نظر یافت نشد، دوباره ثبت نام کنید"}, status=status.HTTP_404_NOT_FOUND)


class VerifyEmailAPIView(APIView):
    
    @extend_schema(
        request = None,
        responses = {201: None}
    )
    def post(self, request):
        token = request.data.get("token")
        try:
            payload = RefreshToken(token).payload
            user_id = payload.get("user_id")
            if not user_id:
                return Response({"error": "توکن معتبر نیست و یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            
            if not user.is_active:
                user.is_active = True
                user.save()
                return Response({"message": "ثبت نام شما کامل شد."}, status=status.HTTP_200_OK)
            return Response({"message": "کاربر قبلاً تأیید شده است."}, status=status.HTTP_400_BAD_REQUEST)
        except (TokenError, CustomUser.DoesNotExist):
            return Response({"error": "توکن معتبر نیست و یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

        
        
# class VerifyEmailAPIView(APIView):

#     @extend_schema(
#         request = ActivationCodeSerializer,
#         responses = {201: ActivationCodeSerializer},
#     )
#     def post(self, request, format=None):
#         serializer = ActivationCodeSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             user = request.user
#             user.is_active = True
#             user.save()
#             return Response({"message": "ثبت نام شما تکمیل شد"}, status=status.HTTP_202_ACCEPTED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ActivationCodeViewSet(viewsets.ViewSet):

#     @extend_schema(
#         request = ActivationCodeSerializer,
#         responses = {201: ActivationCodeSerializer},
#     )
#     def create(self, request, format=None):
#         serializer = ActivationCodeSerializer(data=request.data)
#         if serializer.is_valid():
#             activation_code = serializer.validated_data.get("activation_code")
#             user = get_object_or_404(CustomUser, activation_code=activation_code)
#             if user.activation_code == activation_code:
#                 user.is_active = True
#                 serializer.save()
#                 return Response({"message": "ثبت نام شما تکمیل شد"}, status=status.HTTP_202_ACCEPTED)
#             return Response({"message": "کد وارد شده صحیح نمی باشد"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  
#======================================= User Profile View ======================================

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request = UserProfileSerializer,
        responses = {201: UserProfileSerializer}
    )
    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "اطلاعات شما تکمیل شد"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
       
# class UserProfileViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request = UserProfileSerializer,
#         responses = {201: UserProfileSerializer}
#     )
#     def create(self, request):
#         serializer = UserProfileSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "اطلاعات شما ثبت شد"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# class UserProfileModelViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer
#     http_method_names = ['post']
    
 
#======================================= Login View ============================================

class LoginAPIView(APIView):
    
    @extend_schema(
        request=LoginSerializer,
        responses={201: LoginSerializer}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(username=email, password=password) 
            if user is not None:
                token = RefreshToken.for_user(user).access_token
                return Response({"token": str(token)}, status=status.HTTP_200_OK)
            return Response({"error": "نام کاربری و یا رمز عبور اشتباه است."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#======================================= Fetch Users View ============================================

class FetchUsersGenericsView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all().order_by("id")
    serializer_class = FetchUsersSerializers
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ["id", "first_name", "last_name", "email"]  
    

# class FetchUsersAPIView(APIView):
#     permission_classes = [IsAdminUser] 

#     @extend_schema(
#         request = FetchUsersSerializers,
#         responses = {201: FetchUsersSerializers},
#     )
#     def get(self, request, user_id=None):
#         paginator = PageNumberPagination()
#         paginator.page_size = 5
#         try:
#             if user_id is None:
#                 users = CustomUser.objects.all().order_by("id")
#                 result_page = paginator.paginate_queryset(users, request)
#                 serializer = FetchUsersSerializers(result_page, many=True)
#                 return paginator.get_paginated_response(serializer.data)
#                 # return Response(serializer.data, status=status.HTTP_200_OK)

#             try:
#                 user = CustomUser.objects.get(id=user_id)
#                 serializer = FetchUsersSerializers(user)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             except CustomUser.DoesNotExist:
#                 return Response({"message": "No user found for the given user ID."}, status=status.HTTP_404_NOT_FOUND)

#         except ValueError:
#             return Response({"error": "Invalid user ID. It must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
   

#======================================= Update User View ============================================

class UpdateUserAPIView(APIView):
    permission_classes = [UserCheckOut]
    
    @extend_schema(
        request=UpdateUserSerializer,
        responses={201: UpdateUserSerializer}
    )
    def put(self, request):
        user = request.user
        self.check_object_permissions(request, user)
        # in following line, we are initializing a serializer with an existing user instance and updating it with the new data from request.data.
        # partial=True allows partial updates. It means that not all fields are required in the request data.
        serializer = UpdateUserSerializer(data=request.data, instance=user, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "اطلاعات شما با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#======================================= Forget Password View ========================================

class PasswordResetAPIView(APIView):
    
    @extend_schema(
        request=PasswordResetSerializer,
        responses={201: PasswordResetSerializer}
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = CustomUser.objects.get(email=email)
                token = RefreshToken.for_user(user).access_token
                domain = settings.ALLOWED_HOSTS[0]
                reset_link = f"http://{domain}/password-reset?token={str(token)}"
                subject = "Password Reset Request"
                message = f"Click the link to reset your password: {reset_link}"
                html_content = f"<p>Hello Dear {user.first_name} {user.last_name}<br><br></p><p>Click the link to reset your password: <a href='{reset_link}'>Reset your password</a></p>"
                email_sender(subject, message, html_content, [user.email])
                # send_mail(
                #     "Password Reset Request",
                #     f"Click the link to reset your password: {reset_link}",
                #     settings.DEFAULT_FROM_EMAIL,
                #     [email],
                # )
                return Response({"message": "ایمیل تعییر رمز عبور ارسال شد."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "ایمیل وارد شده معتبر نمی باشد."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SetNewPasswordAPIView(APIView):
    
    @extend_schema(
        request=SetNewPasswordSerializer,
        responses={201: SetNewPasswordSerializer}
    )
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            password = serializer.validated_data["password"]
            try:
                payload = RefreshToken(token).payload
                # Extract user_id from payload
                user_id = payload.get("user_id")
                if not user_id:
                    return Response({"error": "توکن معتبر نیست و یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if user exists
                try:
                    user = CustomUser.objects.get(id=user_id)
                except CustomUser.DoesNotExist:
                    return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
                
                user.set_password(password)
                user.save()
                return Response({"message": "رمز عبور با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)

            except InvalidToken:
                return Response({"error": "توکن معتبر نیست و یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)
            except TokenError:
                return Response({"error": "توکن معتبر نیست و یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
#=====================================================================================================
