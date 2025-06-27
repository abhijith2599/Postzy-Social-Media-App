
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.account.utils import user_email,user_field,user_username
from django.utils.text import slugify
import uuid,random

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
       
       # If user with same email exists, connect to it
       email = user_email(sociallogin.user)
       if email:
           try:
               existing_user = User.objects.get(email=email)
               sociallogin.connect(request, existing_user)
           except User.DoesNotExist:
               pass


    def populate_user(self, request, sociallogin, data):

        user = sociallogin.user

        # Set email and full_name
        user_email(user, data.get('email') or '')
        full_name = (data.get('name') or '') or (data.get('username') or '') or (data.get('first_name') or '') + ' ' + (data.get('last_name') or '')
        user_field(user, 'fullname', full_name)

        # Generate unique username
        base_username = slugify(data.get('email').split('@')[0])
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username

        return user