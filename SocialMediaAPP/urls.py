"""
URL configuration for SocialMediaAPP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from Postzy.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),

    path('Postzy/UserRegistration/',UserRegistrationView.as_view(),name='signup'),
    path('Postzy/SignUPOTPconfirm/',RegistrationOTPConfirmView.as_view(),name='register_otp_confirm'),
    path('Postzy/ResentOTP_REG/',ResendOTPRegistrationView.as_view(),name='resent_otp'),

    path('Postzy/login/',CustomeLoginView.as_view(),name='login'),
    path('Postzy/normal/login/',TokenObtainPairView.as_view(),name='normal_login'),
    path('Postzy/logout/',LogOutView.as_view(),name='logout'),
    path('Postzy/TokenRefresh/',TokenRefreshView.as_view(),name='token_refresh'),

    # Google OAuth URL
    path('Postzy/accounts/', include("allauth.urls")),
    path('Postzy/complete-profile/',CompleteProfileView.as_view(),name='complete_profile')
    # path('Postzy/whoami/', WhoAmIView.as_view(), name='whoami'),


]
