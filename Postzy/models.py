from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator    # for checking phone number contains only integers and len = 10

# Create your models here.

class CustomUser(AbstractUser):

    phone_number = models.CharField(max_length=10,
                                     unique=True,
                                     validators=[RegexValidator(r'^[0-9]{10}$','Enter a Valid 10 Digit Phone Number')]  # r - rawstring
                                    )

    fullname = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username