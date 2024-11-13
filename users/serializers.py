from rest_framework import serializers
from django.core.mail import EmailMultiAlternatives 
from re import compile, match
from random import choice
from string import ascii_letters, digits
from django.conf import settings
from .models import *

#======================================= Needed Methods =====================================

def code_generator(count):
    # characters = list(string.ascii_letters + string.digits + "!?@#$%&*")
    characters = list(ascii_letters + digits)
    code_list = [choice(characters) for _ in range(count)]
    return "".join(code_list)
    
def email_sender(subject, message, HTML_Content, to):
    sender = settings.EMAIL_HOST_USER
    message = EmailMultiAlternatives(subject, message, sender, to)
    # message = EmailMultiAlternatives(Subject, Message, Sending_From, [To])
    message.attach_alternative(HTML_Content, "text/html")
    message.send()
    

#======================================= Custom User Serializer ====================================

class CustomUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=20, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "email", "password", "re_password"]
        
    def create(self, validated_data):
        # None: The default value to return if the "password" key isn't found in the dictionary. This prevents an error if the password isn't provided.
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError("وارد کردن رمز عبور ضروری است")
        
        user = CustomUser.objects.create_user(
            first_name = validated_data["first_name"],
            last_name = validated_data["last_name"],
            email = validated_data["email"],
            password = password
        )
        return user
    
    def validate(self, attrs):
        if attrs["password"] != attrs["re_password"]:
            raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نمی باسد")
        return attrs
    
    def validate_password(self, attr):
        passwordRe = compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*]).{8,}$")
        if not passwordRe.match(attr):
            raise serializers.ValidationError("رمز عبور باید متشکل از حروف کوچک، بزرگ و عدد باشد، و هشت رقمی نیز باشد") 
        return attr
    
    def validate_email(self, attr):
        emailRe = compile(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$")
        if not emailRe.match(attr):
            raise serializers.ValidationError("ایمیل معتبر نیست")
        return attr
    
    
# class CustomUserSerializer(serializers.ModelSerializer):
#     re_password = serializers.CharField(max_length=20, write_only=True)
    
#     class Meta:
#         model = CustomUser
#         fields = ["id", "first_name", "last_name", "email", "password", "re_password",]
        
#     def create(self, validated_data):
#         password = validated_data.pop("password", None)
#         if not password:
#             raise serializers.ValidationError("وارد کردن رمز عبور ضروری است")
        
#         activation_code = code_generator(count=5)
        
#         user = CustomUser.objects.create_user(
#             first_name = validated_data["first_name"],
#             last_name = validated_data["last_name"],
#             email = validated_data["email"],
#             password = password,
#             activation_code = activation_code,
#         )
#         subject = "Registration"
#         message = f"<h4>Hello Dear {user.first_name} {user.last_name}<br><br><h4>Your activation code is: {activation_code}</h4>"
#         to = user.email
#         mail_sender(subject, "", message, [to])
#         return user
    
#     def validate(self, attrs):
#         if attrs["password"] != attrs["re_password"]:
#             raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نمی باسد")
#         return attrs
    
#     def validate_password(self, attr):
#         passwordRe = compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*]).{8,}$")
#         if not passwordRe.match(attr):
#             raise serializers.ValidationError("رمز عبور باید متشکل از حروف کوچک، بزرگ و عدد باشد، و هشت رقمی نیز باشد") 
#         return attr
    
#     def validate_email(self, attr):
#         emailRe = compile(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$")
#         if not emailRe.match(attr):
#             raise serializers.ValidationError("ایمیل معتبر نیست")
        
#         if CustomUser.objects.filter(email=attr).exists():
#             raise serializers.ValidationError("ایمیل مورد نظر ثبت نام کرده است") 
#         return attr
        
    
#======================================= Activation Code Serializer ====================================

# class ActivationCodeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ["activation_code"]

#     def save(self, **kwargs):
#         user = self.instance
#         activation_code = self.validated_data.get("activation_code")
#         if user.activation_code == activation_code:
#             user.is_active = True
#             user.save()
#         return user
        

# class ActivationCodeSerializer(serializers.Serializer):
#     activation_code = serializers.CharField(max_length=20)

#     def validate_activation_code(self, value):
#         user = self.context["request"].user  
#         if user.activation_code != value:
#             raise serializers.ValidationError("کد فعال سازی اشتباه است")
#         return value

   
# class ActivationCodeSerializer(serializers.Serializer):
#     activation_code = serializers.CharField(max_length=20)

#     def update(self, instance, validated_data):
#         user = instance
#         activation_code = validated_data["activation_code"]
        
#         if user.activation_code == activation_code:
#             user.is_active = True
#             user.save()
#         return user


#======================================= User Profile Serializer ====================================

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        
        
#======================================= Login Serializer ===========================================

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    
#======================================= Login Serializer ===========================================

class FetchUsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "email", "is_active", "user_type", "date_joined"]      
       
       
#======================================= Update User Serializer =====================================

class UpdateUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=20, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "password", "re_password"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "email": {"required": False},
            "password": {"write_only": True, "required": False},
        }
        
    def update(self, instance, validated_data):
        # The second argument in validated_data is used to keep the previous value if the user doesn’t provide a new one.
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        password = validated_data.pop("password", None)

        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    def validate(self, attrs):
        # The part "password" in attrs is commonly used in DRF serializers to check if a specific field is present in the validated_data. This ensures that the validation logic only runs if the user has provided a new password.
        if "password" in attrs and attrs["password"] != attrs["re_password"]:
            raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نمی باشد")
        
        password = attrs.get("password")
        passwordRe = compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*]).{8,}$")
        if password and not passwordRe.match(password):
            raise serializers.ValidationError("رمز عبور باید متشکل از حروف کوچک، بزرگ و عدد باشد، و هشت رقمی نیز باشد")
        
        return attrs
    
    
#======================================= Forget Password Serializer =================================

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=20, write_only=True)
    re_password = serializers.CharField(max_length=20, write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["re_password"]:
            raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نمی باشد")
        
        password = attrs.get("password")
        passwordRe = compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*]).{8,}$")
        if password and not passwordRe.match(password):
            raise serializers.ValidationError("رمز عبور باید متشکل از حروف کوچک، بزرگ و عدد باشد، و هشت رقمی نیز باشد")
        
        return attrs

    # Customizes the serializer output to exclude sensitive fields like passwords.
    # In this case, the to_representation method was used to remove password and re_password fields from the serialized output.
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("password", None)
        data.pop("re_password", None)
        return data


#====================================================================================================