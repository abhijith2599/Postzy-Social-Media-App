from rest_framework import serializers

from django.contrib.auth import get_user_model    # use to get the customeuser model and assign that model to a variable User for easy accessing

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)     # declaring cnf_pass as a element so field don't throw error

    class Meta:

        model = User

        fields = ['username','fullname','password','email','phone_number','confirm_password']

        extra_kwargs = {
            'password': {'write_only': True},
            'email':{'required':True},
            'username':{'required':True}
        }

    def validate(self, attrs):       # conf_pass is not in model , so telling django it's manually added and don't throw error
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Password donot match")
        return attrs