from rest_framework import serializers
from django.contrib.auth import get_user_model    # use to get the customeuser model and assign that model to a variable User for easy accessing

from rest_framework_simplejwt.tokens import RefreshToken   # for creating refresh token in the new customeLogIN
from django.contrib.auth import authenticate
from django.db.models import Q

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)     # declaring cnf_pass as a element so field don't throw error

    class Meta:

        model = User

        fields = ['username','fullname','password','email','phone_number','confirm_password']

        extra_kwargs = {                # write_only mens the data will never be outputed in response, even we passed whole data, it will be moved with api , but not outputed
            'password': {'write_only': True},   # so it is always there, but not shown in output, marked as sensitive content
            'email':{'required':True},
            'username':{'required':True}      # required.Tr.. -> makes the field mandatory, if it is missing in input , DRF throw error
        }
        # tweak field behavior without manually redefining each field using --> extra_kwargs.

    def validate(self, attrs):       # conf_pass is not in model , so telling django it's manually added and don't throw error
        
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Password donot match")
        
        return attrs         # attrs : Cleaned dictionary of valid input fields.



class CustomTokenObtainPairSerializer(serializers.Serializer):
    
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        identifier = attrs.get('identifier')   # input given in json as "identifier"->represnt u_name/ph_no/email
        password = attrs.get('password')

        if not identifier or not password:
            raise serializers.ValidationError({"identifier error":"Both login id and password are required"})
        
        user = User.objects.filter(Q(username=identifier) | Q(email=identifier) | Q(phone_number=identifier)).first()    # if filter.first() used no need for try catch only in get Does... raises

        if not user:
            raise serializers.ValidationError({"user error":"User not found"})
                                                                # when raise is triggered , validate() stop (function is ended) and don't reaches return
                                                                # DRF will catch the error and passed to view, which return the error as HTTp Response

        if not user.check_password(password):       # used to hash the pass and check that hashed pass with pass in user table which is hashed
            raise serializers.ValidationError({"password error":"Incorrect Password"})
        
        if not user.is_active:
            raise serializers.ValidationError({"disabled error":"User account is disabled"})
        
        if user.is_logged_in:
            raise serializers.ValidationError({"User Error":"User already logged in"})
        
        # marking user as logged_in
        user.is_logged_in = True   
        user.save(update_fields=['is_logged_in'])

        refresh = RefreshToken.for_user(user)     # generating token for the user logging in

        return{
            "refresh":str(refresh),
            "access":str(refresh.access_token),
            "user_id":user.id,
            "username":user.username,
            "email":user.email
        }
    

class CompleteProfileSerializer(serializers.Serializer):

    phone_number = serializers.CharField(max_length = 10)

    def validate_phone_number(self,value):

        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Invalid Phone Number")
        return value