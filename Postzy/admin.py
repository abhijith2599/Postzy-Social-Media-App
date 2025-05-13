from django.contrib import admin
from .models import *
# from allauth.socialaccount.models import SocialAccount, SocialApp

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','password','fullname','email','phone_number')
    search_fields = ('username','fullname','email','phone_number')

admin.site.register(CustomUser,UserAdmin)

# admin.site.register(SocialAccount)
# admin.site.register(SocialApp)