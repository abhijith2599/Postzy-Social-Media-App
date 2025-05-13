from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
import random
from datetime import datetime,timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken,TokenError  # For logout blacklisting

from .serializers import *
from .models import *


User = get_user_model()

class UserRegistrationView(APIView):    # For registering User to App

    permission_classes = [AllowAny]

    def post(self,request):

        serializer = UserRegisterSerializer(data = request.data)

        if not serializer.is_valid():

            return Response({"Error":"Invalid data check your Inputs and try again"},status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data  # validated_data is stored
        data.pop('confirm_password',None)    # removing conf_pass (optional)

        # if data['password'] != data['confirm_password']:
        #     return Response({"Error":"Passwords doen't match. Try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        if User.objects.filter(email = data['email']).exists():

            return Response({'Message':'User Alread exists, please Login'},status=status.HTTP_400_BAD_REQUEST)
        
        otp = random.randint(100000,999999)

        request.session['registration_data'] = {
            'username':data['username'],
            'email':data['email'],
            'fullname':data['fullname'],
            'password':make_password(data['password']),       # encrypting password for extra safety, no need for further encryption in create_user,just use create
            'phone_number':data['phone_number']
        }

        request.session['otp'] = otp
        request.session['otp_created_time'] = datetime.now().isoformat()    # saving timestamp as iso string
        request.session.set_expiry(300)   # expire in 5 minutes 

        sent = send_mail(
            subject="Postzy Registration OTP",
            message=f"Hi {data['fullname']} Welcome to Postzy, \n To complete the registration please enter this OTP. \n OTP is : {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[data['email']],
            fail_silently=False
        )
        if sent:
            return Response({"Message":"OTP send to your email, Please verify"},status=status.HTTP_200_OK)
        else:
            return Response({"Error":"Failed to send email,Please try again"},status=status.HTTP_400_BAD_REQUEST)


class RegistrationOTPConfirmView(APIView):

    def post(self,request):

        entered_otp = request.data.get('otp')
        saved_otp = request.session.get('otp')
        registration_data = request.session.get('registration_data')

        if not entered_otp or not saved_otp or not registration_data:
            return Response({"Error":"Datas Missing"},status=status.HTTP_400_BAD_REQUEST)

        if int(entered_otp) != int(saved_otp):
            return Response({"Error":"Invalid OTP, please try again."},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        user = User.objects.create(                     # not using create_user here, bcz password already encrypted manually when passed to sessions
            username = registration_data['username'],
            fullname = registration_data['fullname'],
            password = registration_data['password'],
            email = registration_data['email'],
            phone_number = registration_data['phone_number']
        )

        u_name = registration_data['username']
        del request.session['otp']
        del request.session['registration_data']

        if user:

            return Response({"Success":f"User Registered sucessfully {u_name}"}, status=status.HTTP_201_CREATED)
        
        return Response({"Error":"User registration Unsucessfull, please try again."},status=status.HTTP_400_BAD_REQUEST)
    

class ResendOTPRegistrationView(APIView):

    permission_classes = [AllowAny]

    def post(self,request):

        registration_data = request.session.get('registration_data')
        if not registration_data:
            return Response({"Error":"User Registration details not found or timer expired, Please register again"},status=status.HTTP_400_BAD_REQUEST)
        

        to_mail = registration_data.get('email')
        if not to_mail:
            return Response({"Error":"Email not found, Please try to register again"},status=status.HTTP_400_BAD_REQUEST)
        

        otp_created_str = request.session.get('otp_created_time')
        if otp_created_str:
            otp_created_time = datetime.fromisoformat(otp_created_str)  # conv the string back to timer obj
            now = datetime.now()
            diff = now - otp_created_time

            if diff < timedelta(minutes=2):
                # calculating seconds remaining
                seconds_remaining = int((timedelta(minutes=2) - diff).total_seconds())
                return Response({
                    "error": "Please wait before resending OTP.",
                    "seconds_remaining": seconds_remaining
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            return Response({"error": "OTP timestamp missing. Please register again."}, status=status.HTTP_400_BAD_REQUEST)


        otp = random.randint(100000,999999)
        request.session['otp'] = otp
        request.session['otp_created_time'] = datetime.now().isoformat()

        request.session.set_expiry(300)

        sent = send_mail(
            subject="Postzy OTP Resend",
            message=f"Hi {registration_data['fullname']} \n Here is your new OTP to complete your registration: {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_mail],
            fail_silently=False
        )

        if sent:
            return Response({"Success":"OTP resent sucessfully"},status=status.HTTP_200_OK)
        else:
            return Response({"Error":"Failed to send OTP. Try again Later"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LogOutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):
        
        refresh_token = request.data.get('refresh_token')    # pass it as json input
        
        if refresh_token is None:
            return Response({"Error":"Refresh Token Missing. Try Again"},status=status.HTTP_400_BAD_REQUEST)
        
        # marking user as logged_out
        user = request.user
        user.is_logged_in = False
        user.save(update_fields=['is_logged_in'])

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": "Logged out successfully"},status=status.HTTP_205_RESET_CONTENT)
        
        except TokenError:
            return Response({"Error":"Invalid or Expiredd Token"},status=status.HTTP_400_BAD_REQUEST)


class CustomeLoginView(APIView):

    def post(self,request):

        serializer = CustomTokenObtainPairSerializer(data = request.data)

        if serializer.is_valid():

            return Response(serializer.validated_data,status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)     # this .errros help to output "raise" errors
    
    
class CompleteProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):

        serializer = CompleteProfileSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        request.user.phone_number = serializer.validated_data['phone_number']
        request.user.save()

        return Response({"Success":"Phone number updated sucessfully"})








#               to see which user is active
# class WhoAmIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response({
#             "id": request.user.id,
#             "username": request.user.username,
#             "email": request.user.email,
#         })