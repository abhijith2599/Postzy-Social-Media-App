from rest_framework import serializers

from django.contrib.auth import get_user_model    # use to get the customeuser model and assign that model to a variable User for easy accessing

User = get_user_model()

class UserRegisterSerializer(serializers.Serializer):

    class Meta:

        model = User

        fields = ['username','fullname','password','email','phone_number']


    #     extra_kwargs = {
    #         'password': {'write_only': True}
    #     }

    # def create(self, validated_data):
    #     user = CustomUser(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #         fullname=validated_data['fullname'],
    #         phone_number=validated_data['phone_number'],
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user



    #       extra_kwargs = {'password': {'write_only': True}}
    
    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user